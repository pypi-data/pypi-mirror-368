"""
Document models for Thoth SQL Database Manager.
Provides type-safe document structures similar to thoth_vdb architecture.
"""
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4


class ThothDbType(Enum):
    """Types of documents supported by Thoth SQL Database Manager"""
    TABLE = "table"
    COLUMN = "column"
    QUERY = "query"
    SCHEMA = "schema"
    FOREIGN_KEY = "foreign_key"
    INDEX = "index"


class BaseThothDbDocument(BaseModel):
    """Base class for all Thoth database documents"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    thoth_type: ThothDbType
    text: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TableDocument(BaseThothDbDocument):
    """Document representing a database table"""
    table_name: str
    comment: str = ""
    schema_name: str = "public"
    row_count: Optional[int] = None
    thoth_type: ThothDbType = ThothDbType.TABLE
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.text:
            self.text = f"Table: {self.table_name} in schema {self.schema_name}. {self.comment}"


class ColumnDocument(BaseThothDbDocument):
    """Document representing a database column"""
    table_name: str
    column_name: str
    data_type: str
    comment: str = ""
    is_pk: bool = False
    is_nullable: bool = True
    default_value: Optional[str] = None
    max_length: Optional[int] = None
    schema_name: str = "public"
    thoth_type: ThothDbType = ThothDbType.COLUMN
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.text:
            pk_text = " (Primary Key)" if self.is_pk else ""
            nullable_text = " NOT NULL" if not self.is_nullable else ""
            self.text = f"Column: {self.table_name}.{self.column_name} ({self.data_type}{nullable_text}){pk_text}. {self.comment}"


class QueryDocument(BaseThothDbDocument):
    """Document representing a SQL query with metadata"""
    query: str
    query_type: str = "SELECT"  # SELECT, INSERT, UPDATE, DELETE, etc.
    description: str = ""
    parameters: List[str] = Field(default_factory=list)
    result_columns: List[str] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    thoth_type: ThothDbType = ThothDbType.QUERY
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.text:
            self.text = f"{self.query_type} query: {self.description}. SQL: {self.query[:100]}..."


class SchemaDocument(BaseThothDbDocument):
    """Document representing a database schema"""
    schema_name: str
    description: str = ""
    table_count: Optional[int] = None
    owner: Optional[str] = None
    thoth_type: ThothDbType = ThothDbType.SCHEMA
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.text:
            self.text = f"Schema: {self.schema_name}. {self.description}"


class ForeignKeyDocument(BaseThothDbDocument):
    """Document representing a foreign key relationship"""
    source_table_name: str
    source_column_name: str
    target_table_name: str
    target_column_name: str
    constraint_name: str = ""
    schema_name: str = "public"
    thoth_type: ThothDbType = ThothDbType.FOREIGN_KEY
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.text:
            self.text = f"Foreign Key: {self.source_table_name}.{self.source_column_name} -> {self.target_table_name}.{self.target_column_name}"


class IndexDocument(BaseThothDbDocument):
    """Document representing a database index"""
    index_name: str
    table_name: str
    columns: List[str]
    is_unique: bool = False
    is_primary: bool = False
    index_type: str = "btree"
    schema_name: str = "public"
    thoth_type: ThothDbType = ThothDbType.INDEX
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.text:
            unique_text = "Unique " if self.is_unique else ""
            primary_text = "Primary " if self.is_primary else ""
            self.text = f"{unique_text}{primary_text}Index: {self.index_name} on {self.table_name}({', '.join(self.columns)})"


# Type aliases for convenience
ThothDocument = Union[
    TableDocument,
    ColumnDocument,
    QueryDocument,
    SchemaDocument,
    ForeignKeyDocument,
    IndexDocument
]

# Document type mapping for factory methods
DOCUMENT_TYPE_MAP = {
    ThothDbType.TABLE: TableDocument,
    ThothDbType.COLUMN: ColumnDocument,
    ThothDbType.QUERY: QueryDocument,
    ThothDbType.SCHEMA: SchemaDocument,
    ThothDbType.FOREIGN_KEY: ForeignKeyDocument,
    ThothDbType.INDEX: IndexDocument,
}


def create_document(doc_type: ThothDbType, **kwargs) -> BaseThothDbDocument:
    """Factory function to create documents by type"""
    document_class = DOCUMENT_TYPE_MAP.get(doc_type)
    if not document_class:
        raise ValueError(f"Unsupported document type: {doc_type}")
    return document_class(**kwargs)