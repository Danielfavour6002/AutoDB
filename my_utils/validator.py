from typing import List, Optional
from pydantic import BaseModel, Field

class ColumnSchema(BaseModel):
    name: str = Field(description="Name of the column")
    type: str = Field(description="SQLAlchemy type (e.g., Integer, String, DateTime)")
    primary_key: bool = Field(default=False)
    nullable: bool = Field(default=True)
    references: Optional[str] = Field(None)

class TableSchema(BaseModel):
    table_name: str = Field(description="Name of the table to create")
    columns: List[ColumnSchema] = Field(description="List of columns")
    dialect: str = Field(default="postgresql")