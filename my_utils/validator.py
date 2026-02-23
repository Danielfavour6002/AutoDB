from typing import List, Optional
from pydantic import BaseModel, Field

class ForeignKeySchema(BaseModel):
    table: str
    column: str

class ColumnSchema(BaseModel):
    name: str
    type: str
    primary_key: bool = False
    nullable: bool = True
    unique: bool = False
    default: Optional[str] = None
    foreign_key: Optional[ForeignKeySchema] = None

class TableSchema(BaseModel):
    name: str
    columns: List[ColumnSchema]

class DatabaseSchema(BaseModel):
    tables: List[TableSchema]
    dialect: str = "postgresql"