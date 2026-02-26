import re
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Text, DateTime, Boolean, Numeric
)
from sqlalchemy.schema import CreateTable, AddConstraint
from sqlalchemy.dialects import postgresql, mysql, sqlite as sqlite_dialect, mssql, oracle

from my_utils.validator import DatabaseSchema


def map_type(type_str: str):
    t = type_str.lower().strip()
    if t in ("int", "integer", "serial", "bigint", "bigserial"):
        return Integer()
    if t.startswith("varchar"):
        m = re.search(r'\d+', t)
        return String(int(m.group())) if m else String(255)
    if t.startswith("decimal") or t.startswith("numeric"):
        nums = re.findall(r'\d+', t)
        return Numeric(int(nums[0]), int(nums[1])) if len(nums) >= 2 else Numeric(10, 2)
    if t == "text":
        return Text()
    if t in ("timestamp", "datetime", "date"):
        return DateTime()
    if t in ("boolean", "bool"):
        return Boolean()
    return String(255)


DIALECT_MAP = {
    "postgresql": postgresql.dialect(),
    "mysql":      mysql.dialect(),
    "sqlite":     sqlite_dialect.dialect(),
    "mssql":      mssql.dialect(),
    "oracle":     oracle.dialect(),
    "mariadb":    mysql.dialect(),
}


def _topo_sort(tables: list, name_to_schema: dict) -> list:
    """Sort so referenced tables come before tables that reference them."""
    deps = {t.name: set() for t in tables}
    for t in tables:
        for col in t.columns:
            if col.foreign_key and col.foreign_key.table != t.name:
                if col.foreign_key.table in {x.name for x in tables}:
                    deps[t.name].add(col.foreign_key.table)

    sorted_names = []
    visited = set()
    visiting = set()

    def visit(name):
        if name in visiting or name in visited:
            return
        visiting.add(name)
        for dep in deps.get(name, []):
            visit(dep)
        visiting.discard(name)
        visited.add(name)
        sorted_names.append(name)

    for t in tables:
        visit(t.name)

    return [name_to_schema[n] for n in sorted_names if n in name_to_schema]


def build_sql(llm_output: dict, dialect: str = "postgresql") -> list[str]:
    """
    Returns a list of SQL strings — one CREATE TABLE per entry,
    plus ALTER TABLE statements for FKs after all tables exist.
    Each string is a complete, executable statement with no trailing semicolon.
    """
    db_schema    = DatabaseSchema.model_validate(llm_output)
    metadata     = MetaData()
    sa_tables    = {}   # name → SQLAlchemy Table
    schema_map   = {t.name: t for t in db_schema.tables}

    # Pass 1 — build tables WITHOUT FK constraints so order doesn't matter
    for table in db_schema.tables:
        cols = []
        for col in table.columns:
            cols.append(Column(
                col.name,
                map_type(col.type),
                primary_key=col.primary_key,
                nullable=col.nullable,
                unique=getattr(col, "unique", False),
            ))
        sa_tables[table.name] = Table(table.name, metadata, *cols)

    dialect_obj   = DIALECT_MAP.get(dialect, postgresql.dialect())
    sorted_schema = _topo_sort(list(db_schema.tables), schema_map)
    results       = []

    # Pass 2 — emit CREATE TABLE (no FKs yet)
    for t in sorted_schema:
        sa_tbl = sa_tables[t.name]
        sql    = str(CreateTable(sa_tbl).compile(dialect=dialect_obj)).strip()
        results.append(sql)

    # Pass 3 — emit ALTER TABLE ... ADD CONSTRAINT for every FK
    for t in sorted_schema:
        for col in t.columns:
            if col.foreign_key:
                ref_table  = col.foreign_key.table
                ref_col    = col.foreign_key.column
                constraint_name = f"fk_{t.name}_{col.name}"
                # Raw SQL — works across all dialects
                alter = (
                    f"ALTER TABLE {t.name} "
                    f"ADD CONSTRAINT {constraint_name} "
                    f"FOREIGN KEY ({col.name}) "
                    f"REFERENCES {ref_table}({ref_col})"
                )
                results.append(alter)

    return results
