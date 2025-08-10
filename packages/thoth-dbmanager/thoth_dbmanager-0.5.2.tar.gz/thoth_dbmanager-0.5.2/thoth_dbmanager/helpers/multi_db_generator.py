import logging
import random
import re
from typing import Dict, List, Optional
from pathlib import Path

from thoth_dbmanager.helpers.schema import DatabaseSchema


class MultiDbGenerator:
    """
    Class for multi-database schema generation.
    Works with any ThothDbManager implementation.
    """

    CACHED_DB_SCHEMA = {}

    def __init__(
        self,
        dbmanager,
        tentative_schema: Optional[DatabaseSchema] = None,
        schema_with_examples: Optional[DatabaseSchema] = None,
        schema_with_descriptions: Optional[DatabaseSchema] = None,
        add_examples: bool = True):
        self.db_manager = dbmanager
        self.db_id = dbmanager.db_id if dbmanager else None
        self.add_examples = add_examples
        self.schema_structure = tentative_schema or DatabaseSchema()
        self.schema_with_examples = schema_with_examples or DatabaseSchema()
        self.schema_with_descriptions = schema_with_descriptions or DatabaseSchema()

        if dbmanager and self.db_id not in MultiDbGenerator.CACHED_DB_SCHEMA:
            self._load_schema_into_cache()
        self._initialize_schema_structure()

    def _load_schema_into_cache(self) -> None:
        """Load database schema into cache using manager methods"""
        schema_dict = self.db_manager.get_schema_dict()
        db_schema = DatabaseSchema.from_schema_dict(schema_dict)
        MultiDbGenerator.CACHED_DB_SCHEMA[self.db_id] = db_schema

        # Set primary keys
        primary_keys = self.db_manager.get_primary_keys()
        schema_with_primary_keys = {
            table_name: {col: {"primary_key": True} for col in cols}
            for table_name, cols in primary_keys.items()
        }
        db_schema.set_columns_info(schema_with_primary_keys)

        # Set foreign keys
        foreign_keys = self.db_manager.get_foreign_keys()
        schema_with_references = {
            table_name: {
                column_name: {
                    "foreign_keys": info.get("foreign_keys", []),
                    "referenced_by": info.get("referenced_by", []),
                }
                for column_name, info in columns.items()
            }
            for table_name, columns in foreign_keys.items()
        }
        db_schema.set_columns_info(schema_with_references)

    def _set_primary_keys(self, database_schema: DatabaseSchema) -> None:
        """Set primary keys using manager method"""
        primary_keys = self.db_manager.get_primary_keys()
        schema_with_primary_keys = {
            table_name: {col: {"primary_key": True} for col in cols}
            for table_name, cols in primary_keys.items()
        }
        database_schema.set_columns_info(schema_with_primary_keys)

    def _set_foreign_keys(self, database_schema: DatabaseSchema) -> None:
        """Set foreign keys using manager method"""
        foreign_keys = self.db_manager.get_foreign_keys()
        schema_with_references = {
            table_name: {
                column_name: {
                    "foreign_keys": info.get("foreign_keys", []),
                    "referenced_by": info.get("referenced_by", []),
                }
                for column_name, info in columns.items()
            }
            for table_name, columns in foreign_keys.items()
        }
        database_schema.set_columns_info(schema_with_references)

    def _initialize_schema_structure(self) -> None:
        """Initialize the schema structure with table and column info"""
        self._load_table_and_column_info()
        self._load_column_examples()
        self._load_column_descriptions()

    def _load_table_and_column_info(self) -> None:
        """Load table and column information from cached schema"""
        if self.db_id in MultiDbGenerator.CACHED_DB_SCHEMA:
            self.schema_structure = MultiDbGenerator.CACHED_DB_SCHEMA[
                self.db_id
            ].subselect_schema(self.schema_structure)
            self.schema_structure.add_info_from_schema(
                schema=MultiDbGenerator.CACHED_DB_SCHEMA[self.db_id],
                field_names=["type", "primary_key", "foreign_keys", "referenced_by"],
            )

    def _load_column_examples(self) -> None:
        """Load examples for columns in the schema"""
        self.schema_structure.add_info_from_schema(
            schema=self.schema_with_examples, field_names=["examples"]
        )

    def _load_column_descriptions(self) -> None:
        """Load descriptions for columns in the schema"""
        self.schema_structure.add_info_from_schema(
            schema=self.schema_with_descriptions,
            field_names=[
                "original_column_name",
                "column_name",
                "column_description",
                "data_format",
                "value_description",
            ],
        )

    def _extract_create_ddl_commands(self) -> Dict[str, str]:
        """Extract CREATE TABLE DDL commands for all tables

        Returns:
            Dict[str, str]: Dictionary mapping table names to their CREATE TABLE DDL statements
        """
        if hasattr(self.db_manager, 'extract_create_ddl_commands'):
            return self.db_manager.extract_create_ddl_commands()
        else:
            raise NotImplementedError("extract_create_ddl_commands method not implemented for this database manager")

    def generate_schema_string(
        self,
        include_value_description: bool = True,
        shuffle_cols: bool = True,
        shuffle_tables: bool = True,
    ) -> str:
        """
        Generates a schema string with descriptions and examples.

        Args:
            include_value_description (bool): Flag to include value descriptions.
            shuffle_cols (bool): Flag to shuffle columns within tables.
            shuffle_tables (bool): Flag to shuffle tables in the output.

        Returns:
            str: The generated schema string.
        """
        ddl_commands = self._extract_create_ddl_commands()
        schema_strings = []
        
        if shuffle_tables:
            ddl_tables = list(ddl_commands.keys())
            random.shuffle(ddl_tables)
            ddl_commands = {
                table_name: ddl_commands[table_name] for table_name in ddl_tables
            }
        
        for table_name, ddl_command in ddl_commands.items():
            ddl_command = re.sub(r"\s+", " ", ddl_command.strip())
            create_table_match = re.match(
                r'CREATE TABLE "?`?([\w -]+)`?"?\s*\((.*)\)', ddl_command, re.DOTALL
            )
            
            if not create_table_match:
                logging.warning(f"Could not parse DDL command for table {table_name}")
                continue
            
            table = create_table_match.group(1).strip()
            if table != table_name:
                logging.warning(f"Table name mismatch: {table} != {table_name}")
            
            column_definitions = create_table_match.group(2).strip()
            
            if table_name in self.schema_structure.tables:
                table_schema = self.schema_structure.tables[table_name]
                
                # Start building the new CREATE TABLE statement
                schema_lines = [f"CREATE TABLE {table_name}", "("]
                
                # Process column definitions
                definitions = self._separate_column_definitions(column_definitions)
                column_defs = []
                constraint_defs = []
                
                # Extract column definitions and constraints
                for definition in definitions:
                    if definition.lower().startswith("foreign key") or definition.lower().startswith("constraint"):
                        constraint_defs.append(definition)
                    else:
                        column_match = re.match(r'"?`?([\w_]+)`?"?\s+(.*)', definition)
                        if column_match:
                            column_name = column_match.group(1)
                            column_type = column_match.group(2)
                            
                            # Remove NULL/NOT NULL constraints as requested
                            column_type = re.sub(r'\s+(?:NOT\s+)?NULL', '', column_type, flags=re.IGNORECASE)
                            
                            # Check if this is a primary key
                            is_primary_key = "primary key" in column_type.lower()
                            
                            # Format the column definition
                            column_def = f"\t{column_name} {column_type}"
                            
                            # Add comments with examples and descriptions
                            if column_name in table_schema.columns:
                                column_info = table_schema.columns[column_name]
                                comment_parts = []
                                
                                # Add examples if available
                                if hasattr(column_info, 'examples') and column_info.examples:
                                    examples = [f"`{ex}`" for ex in column_info.examples[:3]]  # Limit to 3 examples
                                    comment_parts.append(f"examples: {', '.join(examples)}")
                                
                                # Add column name if available
                                if hasattr(column_info, 'column_name') and column_info.column_name:
                                    comment_parts.append(f"| `{column_info.column_name}`")
                                
                                # Add column description if available
                                if hasattr(column_info, 'column_description') and column_info.column_description:
                                    comment_parts.append(f"description: {column_info.column_description}")
                                
                                # Add value description if available and requested
                                if include_value_description and hasattr(column_info, 'value_description') and column_info.value_description:
                                    comment_parts.append(f"values: {column_info.value_description}")
                                
                                # Add the comment to the column definition
                                if comment_parts:
                                    column_def += f" -- {' '.join(comment_parts)}"
                            
                            column_defs.append(column_def)
        
                # Process foreign key constraints with references
                for column_name, column_info in table_schema.columns.items():
                    if hasattr(column_info, 'foreign_keys') and column_info.foreign_keys:
                        for ref_table, ref_column in column_info.foreign_keys:
                            # Fixed: Properly access tuple elements instead of using dictionary access
                            fk_constraint = f"\tforeign key ({column_name}) references {ref_table} ({ref_column}) on update cascade on delete cascade"
                            constraint_defs.append(fk_constraint)
        
                # Combine column definitions and constraints
                all_defs = column_defs + constraint_defs
                schema_lines.extend(all_defs)
                schema_lines.append(");")
                
                # Join all lines to form the complete CREATE TABLE statement
                schema_strings.append("\n".join(schema_lines))
        
        return "\n\n".join(schema_strings)

    @staticmethod
    def _separate_column_definitions(column_definitions: str) -> List[str]:
        """Separate column definitions from a CREATE TABLE statement

        Args:
            column_definitions (str): The column definitions part of a CREATE TABLE statement

        Returns:
            List[str]: List of individual column definitions
        """
        definitions = []
        current_def = ""
        paren_count = 0
        
        for char in column_definitions:
            if char == '(' and not current_def.strip().lower().startswith("constraint"):
                paren_count += 1
            elif char == ')' and not current_def.strip().lower().startswith("constraint"):
                paren_count -= 1
            
            current_def += char
            
            if char == ',' and paren_count == 0:
                definitions.append(current_def[:-1].strip())
                current_def = ""
        
        if current_def.strip():
            definitions.append(current_def.strip())
        
        return definitions

    def _is_connection(self, table_name: str, column_name: str) -> bool:
        """
        Checks if a column is a connection (primary key or foreign key).

        Args:
            table_name (str): The name of the table.
            column_name (str): The name of the column.

        Returns:
            bool: True if the column is a connection, False otherwise.
        """
        column_info = self.CACHED_DB_SCHEMA[self.db_id].get_column_info(
            table_name, column_name
        )
        if column_info is None:
            return False
        if column_info.primary_key:
            return True
        for target_table, _ in column_info.foreign_keys:
            if self.schema_structure.get_table_info(target_table):
                return True
        for target_table, _ in column_info.referenced_by:
            if self.schema_structure.get_table_info(target_table):
                return True
        for target_table_name, table_schema in self.schema_structure.tables.items():
            if table_name.lower() == target_table_name.lower():
                continue
            for target_column_name, target_column_info in table_schema.columns.items():
                if (
                    target_column_name.lower() == column_name.lower()
                    and target_column_info.primary_key
                ):
                    return True
        return False

    def _get_connections(self) -> Dict[str, List[str]]:
        """
        Retrieves connections between tables in the schema.

        Returns:
            Dict[str, List[str]]: A dictionary mapping table names to lists of connected columns.
        """
        connections = {}
        for table_name, table_schema in self.schema_structure.tables.items():
            connections[table_name] = []
            for column_name, column_info in (
                self.CACHED_DB_SCHEMA[self.db_id].tables[table_name].columns.items()
            ):
                if self._is_connection(table_name, column_name):
                    connections[table_name].append(column_name)
        return connections

    def get_schema_with_connections(self) -> Dict[str, List[str]]:
        """
        Gets schema with connections included.

        Returns:
            Dict[str, List[str]]: The schema with connections included.
        """
        schema_structure_dict = self.schema_structure.to_dict()
        connections = self._get_connections()
        for table_name, connected_columns in connections.items():
            for column_name in connected_columns:
                if column_name.lower() not in [
                    col.lower() for col in schema_structure_dict[table_name]
                ]:
                    schema_structure_dict[table_name].append(column_name)
        return schema_structure_dict

    def _get_example_column_name_description(
        self, table_name: str, column_name: str, include_value_description: bool = True
    ) -> str:
        """
        Retrieves example values and descriptions for a column.

        Args:
            table_name (str): The name of the table.
            column_name (str): The name of the column.
            include_value_description (bool): Flag to include value description.

        Returns:
            str: The example values and descriptions for the column.
        """
        example_part = ""
        name_string = ""
        description_string = ""
        value_statics_string = ""
        value_description_string = ""

        column_info = self.schema_structure.get_column_info(table_name, column_name)
        if column_info:
            if column_info.examples:
                example_part = f" Example Values: {', '.join([f'`{str(x)}`' for x in column_info.examples])}"
            if column_info.value_statics:
                value_statics_string = f" Value Statics: {column_info.value_statics}"
            if column_info.column_name:
                if (column_info.column_name.lower() != column_name.lower()) and (
                    column_info.column_name.strip() != ""
                ):
                    name_string = f"| Column Name Meaning: {column_info.column_name}"
            if column_info.column_description:
                description_string = (
                    f"| Column Description: {column_info.column_description}"
                )
            if column_info.value_description and include_value_description:
                value_description_string = (
                    f"| Value Description: {column_info.value_description}"
                )

        description_part = (
            f"{name_string} {description_string} {value_description_string}"
        )
        joint_string = (
            f" --{example_part} |{value_statics_string} {description_part}"
            if example_part and description_part
            else f" --{example_part or description_part or value_statics_string}"
        )
        if joint_string == " --":
            joint_string = ""
        return joint_string.replace("\n", " ") if joint_string else ""

    def get_column_profiles(
        self, with_keys: bool = False, with_references: bool = False
    ) -> Dict[str, Dict[str, str]]:
        """
        Retrieves profiles for columns in the schema.
        The output is a dictionary with table names as keys mapping to dictionaries with column names as keys and column profiles as values.

        Args:
            with_keys (bool): Flag to include primary keys and foreign keys.
            with_references (bool): Flag to include referenced columns.

        Returns:
            Dict[str, Dict[str, str]]: The column profiles.
        """
        column_profiles = {}
        for table_name, table_schema in self.schema_structure.tables.items():
            column_profiles[table_name] = {}
            for column_name, column_info in table_schema.columns.items():
                if with_keys or not (
                    column_info.primary_key
                    or column_info.foreign_keys
                    or column_info.referenced_by
                ):
                    column_profile = f"Table name: `{table_name}`\nOriginal column name: `{column_name}`\n"
                    if (
                        column_info.column_name.lower().strip()
                        != column_name.lower().strip()
                    ) and (column_info.column_name.strip() != ""):
                        column_profile += (
                            f"Expanded column name: `{column_info.column_name}`\n"
                        )
                    if column_info.type:
                        column_profile += f"Data type: {column_info.type}\n"
                    if column_info.column_description:
                        column_profile += (
                            f"Description: {column_info.column_description}\n"
                        )
                    if column_info.value_description:
                        column_profile += (
                            f"Value description: {column_info.value_description}\n"
                        )
                    if column_info.examples:
                        column_profile += f"Example of values in the column: {', '.join([f'`{str(x)}`' for x in column_info.examples])}\n"
                    if column_info.primary_key:
                        column_profile += "This column is a primary key.\n"
                    if with_references:
                        if column_info.foreign_keys:
                            column_profile += (
                                "This column references the following columns:\n"
                            )
                            for target_table, target_column in column_info.foreign_keys:
                                column_profile += f"    Table: `{target_table}`, Column: `{target_column}`\n"
                        if column_info.referenced_by:
                            column_profile += (
                                "This column is referenced by the following columns:\n"
                            )
                            for (
                                source_table,
                                source_column,
                            ) in column_info.referenced_by:
                                column_profile += f"    Table: `{source_table}`, Column: `{source_column}`\n"
                    column_profiles[table_name][column_name] = column_profile
        return column_profiles

    def validate_schema_consistency(self) -> List[str]:
        """
        Validates the consistency between the schema in the generator and the database manager.
        
        Returns:
            List[str]: A list of validation error messages, empty if no errors.
        """
        errors = []
        
        # Skip validation if no database manager is provided
        if not self.db_manager:
            return ["No database manager provided for validation"]
        
        # Compare schema tables with database manager tables
        db_schema_dict = self.db_manager.get_schema_dict()
        for table_name in self.schema_structure.tables:
            if table_name not in db_schema_dict:
                errors.append(f"Table '{table_name}' exists in schema but not in database manager")
        
        # Validate foreign key references
        for table_name, table_schema in self.schema_structure.tables.items():
            for column_name, column_info in table_schema.columns.items():
                if column_info.foreign_keys:
                    for ref_table, ref_column in column_info.foreign_keys:
                        # Check if referenced table exists
                        if ref_table not in self.schema_structure.tables:
                            errors.append(f"Foreign key in {table_name}.{column_name} references non-existent table {ref_table}")
                            continue
                        
                        # Check if referenced column exists
                        if ref_column not in self.schema_structure.tables[ref_table].columns:
                            errors.append(f"Foreign key in {table_name}.{column_name} references non-existent column {ref_table}.{ref_column}")
        
        # Use the DatabaseSchema's validate_schema method if available
        if hasattr(self.schema_structure, 'validate_schema'):
            schema_errors = self.schema_structure.validate_schema()
            errors.extend(schema_errors)
        
        return errors