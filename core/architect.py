import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import Table, Column, MetaData, Integer, String, ForeignKey, Numeric, Text, DateTime, Boolean ,create_engine
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql, sqlite, mysql
from my_utils.validator import TableSchema, DatabaseSchema
from my_utils.llm_handler import generate_sql_func, generate_sql

#1. The Architect (Structure)
#Design and modify your database using plain English. 
#* **Intelligent Drafting:** Generates structured JSON schemas before converting them to dialect-specific SQL via SQLAlchemy.
#* **Reflective Context:** Scans your existing database to suggest `ALTER` commands instead of creating redundant tables.
#* **Sandbox Mode:** No DB? No problem. Generate raw SQL scripts for any major dialect (Postgres, MySQL, SQLite) without a connection.

type_map = {"Integer": Integer, "String": String}
def map_type(type_str : str):
    type_map = {
        "int" : Integer(),
        "varchar" : String(),
        "decimal" : Numeric(),
        "text" : Text(),
        "timestamp" : DateTime(),
        "boolean" : Boolean()
    }
    return type_map.get(type_str, String)



def build_sql(llm_output: dict, dialect: str) -> list[str]:
    db_schema = DatabaseSchema.model_validate(llm_output)
    metadata = MetaData()
    statements = []
    for table in db_schema.tables:
        cols = []
        for col in table.columns:
            fk = ForeignKey(col.references) if col.references else None
            cols.append(
                Column(
                    col.name,
                    map_type(col.type),
                    fk,
                    primary_key=col.primary_key,
                    nullable=col.nullable

                )
            )
        Table(
            table.name,
            metadata,
            *cols
        )
        dialects = {
            "postgresql": postgresql.dialect(),
            "sqlite": sqlite.dialect(),
            "mysql": mysql.dialect()
    }

        table_statement = CreateTable(Table)
        statement = str(table_statement.compile(dialect=dialects.get(dialect, postgresql.dialect())))
        statements.append(statement)
    return statements


print("genrating schema.....")
sql_query = generate_sql("create a database for an ecoomerce platform", database_schema=DatabaseSchema)
print("done")
test = build_sql(sql_query, "postgres")
print(test)