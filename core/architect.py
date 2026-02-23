import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import Table, Column, MetaData, Integer, String, ForeignKey, create_mock_engine
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql, sqlite, mysql
from my_utils.validator import TableSchema
from my_utils.llm_handler import generate_sql_func


type_map = {"Integer": Integer, "String": String}

def get_sql_preview(parsed_data: TableSchema):
    """
   generate sql from prompt usi
    """
    metadata = MetaData()
    
    # Map AI strings to SQLAlchemy types
    
    cols = []
    for c in parsed_data.columns:
        # Handle ForeignKeys if provided
        fk = ForeignKey(c.references) if c.references else None
        
        cols.append(Column(
            c.name, 
            type_map.get(c.type, String), 
            fk,
            primary_key=c.primary_key, 
            nullable=c.nullable
        ))

    # Construct the table object
    table = Table(parsed_data.table_name, metadata, *cols)

    # Use the appropriate dialect for the preview
    dialects = {
        "postgresql": postgresql.dialect(),
        "sqlite": sqlite.dialect(),
        "mysql": mysql.dialect()
    }

    # This generates the "CREATE TABLE..." string without executing it
    statement = CreateTable(table)
    return str(statement.compile(dialect=dialects.get(parsed_data.dialect, postgresql.dialect())))

def create_table_from_json(parsed_json : TableSchema, engine):

    metadata = MetaData()
    cols = []
    try:
        for col in parsed_json["columns"]:
            cols.append(
                Column(col["name"], type_map.get(col["type"], String), ForeignKey(col["references"]), primary_key=col["primary_key"], nullable=col["nullable"])
            ) 
    except Exception as e:
        print(f"error creating table {e}")
    
    table = Table(
        parsed_json["table_name"],
        metadata,
        *cols
    )
    metadata.create_all(engine)
    return table

ff = generate_sql_func("i want a to create a database with table users, and columsn orders, type", TableSchema)
print(ff)