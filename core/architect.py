import re
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Text, DateTime, Boolean, Numeric
)
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql, mysql, sqlite as sqlite_dialect, mssql, oracle

from my_utils.validator import DatabaseSchema


# ── TYPE MAPPER ──────────────────────────────────────────────────
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
    return String(255)  # safe fallback


# ── DIALECT MAP ───────────────────────────────────────────────────
DIALECT_MAP = {
    "postgresql": postgresql.dialect(),
    "mysql":      mysql.dialect(),
    "sqlite":     sqlite_dialect.dialect(),
    "mssql":      mssql.dialect(),
    "oracle":     oracle.dialect(),
    "mariadb":    mysql.dialect(),  # MariaDB is MySQL-compatible
}


# ── DEPENDENCY SORT (topological) ────────────────────────────────
def _topo_sort(tables: list) -> list:
    """
    Sort tables so referenced tables always come before tables that reference them.
    Handles circular refs gracefully by falling back to original order.
    """
    name_to_table = {t.name: t for t in tables}
    deps = {t.name: set() for t in tables}

    for t in tables:
        for col in t.columns:
            if col.foreign_key:
                ref_table = col.foreign_key.table
                if ref_table in name_to_table and ref_table != t.name:
                    deps[t.name].add(ref_table)

    sorted_names = []
    visited      = set()
    visiting     = set()  # cycle detection

    def visit(name):
        if name in visiting:
            return  # cycle — skip
        if name in visited:
            return
        visiting.add(name)
        for dep in deps.get(name, []):
            visit(dep)
        visiting.discard(name)
        visited.add(name)
        sorted_names.append(name)

    for t in tables:
        visit(t.name)

    return [name_to_table[n] for n in sorted_names if n in name_to_table]


# ── MAIN BUILD FUNCTION ───────────────────────────────────────────
def build_sql(llm_output: dict, dialect: str = "postgresql") -> list[str]:
    """
    Convert LLM JSON output → validated schema → SQLAlchemy → SQL strings.
    Returns a list of CREATE TABLE statements (one per table).
    """
    db_schema = DatabaseSchema.model_validate(llm_output)
    metadata  = MetaData()  # single shared metadata — critical for FK resolution
    tables    = {}

    # ── PASS 1: register all tables in shared metadata ──
    for table in db_schema.tables:
        cols = []
        for col in table.columns:
            col_args = [col.name, map_type(col.type)]
            if col.foreign_key:
                col_args.append(
                    ForeignKey(f"{col.foreign_key.table}.{col.foreign_key.column}",
                               use_alter=True,   # deferred — avoids ordering issues
                               name=f"fk_{table.name}_{col.name}")
                )
            cols.append(Column(
                *col_args,
                primary_key = col.primary_key,
                nullable    = col.nullable,
                unique      = getattr(col, "unique", False),
            ))
        tables[table.name] = Table(table.name, metadata, *cols)

    # ── PASS 2: sort by dependency then compile ──
    dialect_obj   = DIALECT_MAP.get(dialect, postgresql.dialect())
    sorted_tables = _topo_sort(list(db_schema.tables))
    results       = []

    for t in sorted_tables:
        tbl_obj   = tables[t.name]
        statement = CreateTable(tbl_obj)
        sql       = str(statement.compile(dialect=dialect_obj))
        results.append(sql.strip())

    return results
