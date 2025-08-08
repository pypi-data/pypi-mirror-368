# Thoth Database Manager

A Python library for managing SQL databases with support for multiple database types, LSH-based similarity search, and a modern plugin architecture.

## Features

- **Multi-Database Support**: PostgreSQL, MySQL, MariaDB, SQLite, SQL Server, Oracle, Informix, and Supabase
- **Plugin Architecture**: Extensible design for adding new database types
- **LSH Search**: Locality-Sensitive Hashing for finding similar values across database columns
- **Type Safety**: Pydantic-based document models for structured data
- **Modern API**: Clean, plugin-based interface for all database operations

## Installation

### Basic Installation

```bash
uv add thoth-dbmanager
```

### Installation with Database Support

To use specific databases, you'll need to install the corresponding database drivers. You can install them individually or use our convenience extras:

#### Install with All Database Support

```bash
uv add thoth-dbmanager[all]
```

#### Install with Specific Database Support

**PostgreSQL:**

```bash
uv add thoth-dbmanager[postgresql]
# or manually: uv add psycopg2-binary
```

**MySQL:**

```bash
uv add thoth-dbmanager[mysql]
# or manually: uv add mysql-connector-python
```

**MariaDB:**

```bash
uv add thoth-dbmanager[mariadb]
# or manually: uv add mariadb
```

**SQL Server:**

```bash
uv add thoth-dbmanager[sqlserver]
# or manually: uv add pyodbc
```

**Oracle:**

```bash
uv add thoth-dbmanager[oracle]
# or manually: uv add cx_Oracle
```

**Informix:**

```bash
uv add thoth-dbmanager[informix]
# or manually: uv add IfxPy
```

**Supabase:**

```bash
uv add thoth-dbmanager[supabase]
# or manually: uv add supabase gotrue
```

**SQLite** is supported out of the box (no additional drivers needed).

#### Development Installation

```bash
uv add thoth-dbmanager[dev]
```

## Quick Start

### Basic Usage

```python
from thoth_dbmanager import ThothDbManager

# Create a database manager instance
manager = ThothDbManager.get_instance(
    db_type="postgresql",
    db_root_path="./data",
    db_mode="dev",
    host="localhost",
    port=5432,
    database="mydb",
    user="username",
    password="password"
)

# Get database information
tables = manager.get_tables()
columns = manager.get_columns("my_table")
foreign_keys = manager.get_foreign_keys()

# Execute SQL queries
results = manager.execute_sql("SELECT * FROM my_table LIMIT 10")

# Get example data for understanding table contents
example_data = manager.get_example_data("my_table", number_of_rows=20)
```

### LSH Similarity Search

```python
# Query for similar values across all database columns
similar_values = manager.query_lsh(
    keyword="john doe",
    top_n=10,
    signature_size=30,
    n_gram=3
)

# Results are organized by table and column
for table_name, columns in similar_values.items():
    for column_name, values in columns.items():
        print(f"Similar values in {table_name}.{column_name}: {values}")
```

## Supported Databases

| Database | Connection Parameters |
|----------|----------------------|
| **PostgreSQL** | `host`, `port`, `database`, `user`, `password` |
| **MySQL** | `host`, `port`, `database`, `user`, `password` |
| **MariaDB** | `host`, `port`, `database`, `user`, `password` |
| **SQLite** | `database_path` |
| **Supabase** | `host`, `port`, `database`, `user`, `password`, `project_url`, `api_key` |
| **SQL Server** | `server`, `database`, `user`, `password` |
| **Oracle** | `host`, `port`, `service_name`, `user`, `password` |
| **Informix** | `server`, `database`, `host`, `user`, `password` |

## API Reference

### ThothDbManager

The main class for database operations.

#### Class Methods

##### `get_instance(db_type: str, **kwargs) -> ThothDbManager`

Creates or retrieves a singleton instance of the database manager.

**Parameters:**
- `db_type` (str): Database type identifier
- `db_root_path` (str): Path to store database-related files
- `db_mode` (str): Operating mode ("dev", "prod", etc.)
- `**kwargs`: Database-specific connection parameters

**Returns:** Database manager instance

#### Instance Methods

##### `execute_sql(sql: str, params: dict = None, fetch: str = "all", timeout: int = 60) -> Any`

Execute SQL queries against the database.

**Parameters:**
- `sql` (str): SQL query string
- `params` (dict, optional): Query parameters for prepared statements
- `fetch` (str): How to fetch results ("all", "one", or number)
- `timeout` (int): Query timeout in seconds

**Returns:** Query results

##### `get_tables() -> List[Dict[str, str]]`

Get list of tables in the database.

**Returns:** List of dictionaries with `name` and `comment` keys

##### `get_columns(table_name: str) -> List[Dict[str, Any]]`

Get column information for a specific table.

**Parameters:**
- `table_name` (str): Name of the table

**Returns:** List of dictionaries with column metadata (`name`, `data_type`, `comment`, `is_pk`)

##### `get_foreign_keys() -> List[Dict[str, str]]`

Get foreign key relationships in the database.

**Returns:** List of dictionaries with foreign key information

##### `get_example_data(table_name: str, number_of_rows: int = 30) -> Dict[str, List[Any]]`

Get the most frequent values for each column in a table.

**Parameters:**
- `table_name` (str): Name of the table
- `number_of_rows` (int): Maximum number of example values per column

**Returns:** Dictionary mapping column names to lists of example values

##### `query_lsh(keyword: str, signature_size: int = 30, n_gram: int = 3, top_n: int = 10) -> Dict[str, Dict[str, List[str]]]`

Search for similar values using LSH (Locality-Sensitive Hashing).

**Parameters:**
- `keyword` (str): Search term
- `signature_size` (int): MinHash signature size
- `n_gram` (int): N-gram size for text processing
- `top_n` (int): Number of similar values to return

**Returns:** Nested dictionary: `{table_name: {column_name: [similar_values]}}`

### Factory Pattern (Alternative API)

For more advanced usage, you can use the factory pattern:

```python
from thoth_dbmanager import ThothDbFactory

# Create manager using factory
manager = ThothDbFactory.create_manager(
    db_type="postgresql",
    db_root_path="./data",
    db_mode="dev",
    host="localhost",
    port=5432,
    database="mydb",
    user="username",
    password="password"
)

# List available database types
available_dbs = ThothDbFactory.list_available_databases()

# Get required parameters for a database type
params = ThothDbFactory.get_required_parameters("postgresql")
```

## Document-Based API (Advanced)

The library also provides a document-based API for structured data access:

```python
# Get tables as structured documents
if hasattr(manager, 'get_tables_as_documents'):
    table_docs = manager.get_tables_as_documents()
    for doc in table_docs:
        print(f"Table: {doc.table_name}")
        print(f"Schema: {doc.schema_name}")
        print(f"Comment: {doc.comment}")

# Get columns as structured documents
if hasattr(manager, 'get_columns_as_documents'):
    column_docs = manager.get_columns_as_documents("my_table")
    for doc in column_docs:
        print(f"Column: {doc.column_name} ({doc.data_type})")
        print(f"Nullable: {doc.is_nullable}")
        print(f"Primary Key: {doc.is_pk}")
```

## Database Connection Examples

### PostgreSQL

**Installation:**

```bash
uv add thoth-dbmanager[postgresql]
```

**Usage:**
```python
manager = ThothDbManager.get_instance(
    db_type="postgresql",
    db_root_path="./data",
    db_mode="production",
    host="localhost",
    port=5432,
    database="myapp",
    user="dbuser",
    password="dbpass"
)
```

### MySQL

**Installation:**

```bash
uv add thoth-dbmanager[mysql]
```

**Usage:**

```python
manager = ThothDbManager.get_instance(
    db_type="mysql",
    db_root_path="./data",
    db_mode="production",
    host="localhost",
    port=3306,
    database="myapp",
    user="dbuser",
    password="dbpass"
)
```

### MariaDB

**Installation:**

```bash
uv add thoth-dbmanager[mariadb]
```

**Usage:**

```python
manager = ThothDbManager.get_instance(
    db_type="mariadb",
    db_root_path="./data",
    db_mode="production",
    host="localhost",
    port=3306,
    database="myapp",
    user="dbuser",
    password="dbpass"
)
```

### SQLite

**Installation:**

```bash
# No additional drivers needed - SQLite is included with Python
uv add thoth-dbmanager
```

**Usage:**

```python
manager = ThothDbManager.get_instance(
    db_type="sqlite",
    db_root_path="./data",
    db_mode="dev",
    database_path="./data/myapp.db"
)
```

### SQL Server

**Installation:**

```bash
uv add thoth-dbmanager[sqlserver]
```

**Usage:**

```python
manager = ThothDbManager.get_instance(
    db_type="sqlserver",
    db_root_path="./data",
    db_mode="production",
    server="localhost",
    database="myapp",
    user="dbuser",
    password="dbpass"
)
```

### Oracle

**Installation:**

```bash
uv add thoth-dbmanager[oracle]
```

**Usage:**

```python
manager = ThothDbManager.get_instance(
    db_type="oracle",
    db_root_path="./data",
    db_mode="production",
    host="localhost",
    port=1521,
    service_name="ORCL",
    user="dbuser",
    password="dbpass"
)
```

### Informix

**Installation:**

```bash
uv add thoth-dbmanager[informix]
```

**Usage:**

```python
manager = ThothDbManager.get_instance(
    db_type="informix",
    db_root_path="./data",
    db_mode="production",
    server="informix_server",
    database="myapp",
    host="localhost",
    user="dbuser",
    password="dbpass"
)
```

### Supabase

**Installation:**

```bash
uv add thoth-dbmanager[supabase]
```

**Usage:**

```python
manager = ThothDbManager.get_instance(
    db_type="supabase",
    db_root_path="./data",
    db_mode="production",
    host="db.example.supabase.co",
    port=5432,
    database="postgres",
    user="postgres",
    password="your_password",
    project_url="https://your-project.supabase.co",
    api_key="your_supabase_api_key"
)
```

## Error Handling

The library provides clear error messages for common issues:

```python
try:
    manager = ThothDbManager.get_instance(
        db_type="postgresql",
        db_root_path="./data",
        # Missing required parameters
    )
except ValueError as e:
    print(f"Configuration error: {e}")

try:
    results = manager.execute_sql("SELECT * FROM nonexistent_table")
except Exception as e:
    print(f"Query error: {e}")
```

## LSH Search Details

The LSH (Locality-Sensitive Hashing) feature allows you to find similar text values across your database:

1. **Automatic Setup**: LSH indexes are created automatically from your database content
2. **Cross-Column Search**: Search across all text columns in all tables
3. **Fuzzy Matching**: Find similar values even with typos or variations
4. **Configurable**: Adjust similarity sensitivity with parameters

### LSH Use Cases

- **Data Deduplication**: Find duplicate or near-duplicate records
- **Data Quality**: Identify inconsistent data entry
- **Search Enhancement**: Provide "did you mean?" functionality
- **Data Exploration**: Discover related content across tables

## Architecture

The library uses a modern plugin architecture:

- **Plugins**: Database-specific implementations
- **Adapters**: Low-level database operations
- **Factory**: Plugin instantiation and management
- **Documents**: Type-safe data models using Pydantic
- **Registry**: Plugin discovery and registration

This design makes it easy to:
- Add support for new database types
- Maintain consistent APIs across databases
- Extend functionality without breaking existing code

## Contributing

To add support for a new database type:

1. Create an adapter class implementing `DbAdapter`
2. Create a plugin class implementing `DbPlugin`
3. Register the plugin with `@register_plugin("db_type")`
4. Add connection parameter validation
5. Implement required abstract methods

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please visit the project repository.
