"""Configuration models for fake data generation using Pydantic v2."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SparkDataType(str, Enum):
    """Supported Spark SQL data types."""

    STRING = "string"
    INTEGER = "integer"
    LONG = "long"
    DOUBLE = "double"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    TIMESTAMP = "timestamp"
    DECIMAL = "decimal"


class ReferenceTable(BaseModel):
    """Configuration for referencing an external table."""

    model_config = ConfigDict(extra="forbid")

    catalog: str = Field(..., description="Unity Catalog catalog name")
    schema_name: str = Field(..., description="Schema name within the catalog")
    table: str = Field(..., description="Table name within the schema")
    key_column: str = Field(..., description="Column to reference for values")


class ColumnConfig(BaseModel):
    """Configuration for a single column."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Column name")
    data_type: SparkDataType = Field(..., description="Spark SQL data type")
    nullable: bool = Field(default=True, description="Whether column can be null")
    faker_function: str = Field(default="", description="Faker method to use (e.g., 'first_name', 'random_int')")
    faker_options: dict[str, Any] = Field(default_factory=dict, description="Options to pass to the Faker method")
    description: str | None = Field(default=None, description="Column description")
    unique: bool = Field(default=False, description="Whether values must be unique")
    depends_on: str | None = Field(default=None, description="Name of parent column this depends on")
    reference_mapping: dict[Any, Any | list[Any]] | None = Field(
        default=None, description="Mapping from parent values to child values"
    )
    reference_table: ReferenceTable | None = Field(default=None, description="External table to reference for values")

    @model_validator(mode="after")
    def validate_reference_fields(self) -> ColumnConfig:
        """Validate reference configuration."""
        has_reference_mapping = self.reference_mapping is not None
        has_reference_table = self.reference_table is not None

        # Cannot have both reference types
        if has_reference_mapping and has_reference_table:
            msg = "Cannot specify both reference_mapping and reference_table"
            raise ValueError(msg)

        # Validate faker_function requirements
        if not has_reference_table and not has_reference_mapping and not self.faker_function:
            msg = "faker_function is required when not using reference_table or reference_mapping"
            raise ValueError(msg)

        # For reference_table, faker_function should be empty
        if has_reference_table and self.faker_function:
            msg = "faker_function should be empty when using reference_table"
            raise ValueError(msg)

        # For depends_on, need either reference_mapping or reference_table
        if self.depends_on is not None and not has_reference_mapping and not has_reference_table:
            msg = "Either reference_mapping or reference_table is required when depends_on is specified"
            raise ValueError(msg)

        # reference_mapping needs depends_on, but reference_table can be used without depends_on
        if has_reference_mapping and self.depends_on is None:
            msg = "depends_on is required when reference_mapping is specified"
            raise ValueError(msg)

        return self

    @model_validator(mode="after")
    def validate_dependent_column_not_nullable(self) -> ColumnConfig:
        """Validate that dependent columns cannot be nullable for now."""
        # AIDEV-NOTE: For now, we don't allow dependent columns to be nullable for simplicity
        if self.depends_on is not None and self.nullable:
            msg = f"Dependent column '{self.name}' cannot be nullable"
            raise ValueError(msg)
        return self


class TableTarget(BaseModel):
    """Target table configuration."""

    model_config = ConfigDict(extra="forbid")

    catalog: str = Field(..., description="Unity Catalog catalog name")
    schema_name: str = Field(..., description="Schema name within the catalog")
    table: str = Field(..., description="Table name within the schema")
    write_mode: str = Field(default="overwrite", description="Write mode: overwrite, append, error, ignore")


class DataGenConfig(BaseModel):
    """Complete configuration for fake data generation."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Configuration name/description")
    target: TableTarget = Field(..., description="Target table configuration")
    columns: list[ColumnConfig] = Field(..., description="Column definitions")
    num_records: int = Field(default=1000, description="Number of records to generate")
    batch_size: int = Field(default=1000, description="Batch size for processing")

    @model_validator(mode="after")
    def validate_dependencies(self) -> DataGenConfig:
        """Validate column dependencies and detect circular references."""
        column_names = {col.name for col in self.columns}

        # Validate that parent columns exist
        for column in self.columns:
            if column.depends_on and column.depends_on not in column_names:
                msg = f"Column '{column.name}' depends on '{column.depends_on}' which does not exist"
                raise ValueError(msg)

        # Check for circular dependencies using DFS
        # AIDEV-NOTE: Use depth-first search to detect cycles in dependency graph
        visited = set()
        rec_stack = set()

        def has_cycle(col_name: str) -> bool:
            """Check if column has circular dependency using DFS."""
            if col_name in rec_stack:
                return True
            if col_name in visited:
                return False

            visited.add(col_name)
            rec_stack.add(col_name)

            # Find the column config
            col_config = next((c for c in self.columns if c.name == col_name), None)
            if col_config and col_config.depends_on and has_cycle(col_config.depends_on):
                return True

            rec_stack.remove(col_name)
            return False

        for column in self.columns:
            if column.name not in visited and has_cycle(column.name):
                msg = f"Circular dependency detected involving column '{column.name}'"
                raise ValueError(msg)

        return self

    def get_table_path(self) -> str:
        """Get the full table path."""
        return f"{self.target.catalog}.{self.target.schema_name}.{self.target.table}"

    def get_dependency_sorted_columns(self) -> list[ColumnConfig]:
        """Get columns sorted by dependencies (parents first).

        Returns:
            List of columns sorted topologically by dependencies
        """
        # AIDEV-NOTE: Topological sort to ensure parent columns are generated first
        sorted_columns = []
        visited = set()
        temp_mark = set()

        def visit(column: ColumnConfig) -> None:
            """Visit column in topological sort."""
            if column.name in temp_mark:
                msg = f"Circular dependency detected involving column '{column.name}'"
                raise ValueError(msg)
            if column.name in visited:
                return

            temp_mark.add(column.name)

            # Visit parent column first
            if column.depends_on:
                parent_col = next(c for c in self.columns if c.name == column.depends_on)
                visit(parent_col)

            temp_mark.remove(column.name)
            visited.add(column.name)
            sorted_columns.append(column)

        for column in self.columns:
            if column.name not in visited:
                visit(column)

        return sorted_columns

    def get_table_dependencies(self) -> list[str]:
        """Get list of table paths that this configuration depends on.

        Returns:
            List of fully qualified table names that this table references
        """
        dependencies = set()
        for column in self.columns:
            if column.reference_table:
                ref_table = column.reference_table
                table_path = f"{ref_table.catalog}.{ref_table.schema_name}.{ref_table.table}"
                dependencies.add(table_path)
        return list(dependencies)


def _has_dependency_in_group(config: DataGenConfig, current_group: list[DataGenConfig]) -> bool:
    """Check if a config has dependencies within the current group."""
    deps = config.get_table_dependencies()

    for dep in deps:
        for dep_config in current_group:
            if dep_config.get_table_path() == dep:
                return True
    return False


def _process_group_level(
    groups: dict[int, list[DataGenConfig]], level: int
) -> tuple[list[DataGenConfig], list[DataGenConfig]]:
    """Process a single group level and return next level and remaining configs."""
    current_group = groups.get(level - 1, [])
    next_level = []
    remaining_in_current = []

    for config in current_group:
        if _has_dependency_in_group(config, current_group):
            next_level.append(config)
        else:
            remaining_in_current.append(config)

    return next_level, remaining_in_current


def _flatten_groups(groups: dict[int, list[DataGenConfig]]) -> list[DataGenConfig]:
    """Flatten groups in dependency order."""
    result = []
    for level in sorted(groups.keys()):
        result.extend(groups[level])
    return result


def resolve_table_generation_order(configs: list[DataGenConfig]) -> list[DataGenConfig]:
    """Sort configurations by inter-table dependencies using grouping approach.

    Uses a simple grouping algorithm:
    1. All tables start in group 1 (no dependencies)
    2. Tables with references move to group 2
    3. Tables that reference other tables in their current group move to next group
    4. Continue until no more movement or max depth reached

    Args:
        configs: List of data generation configurations

    Returns:
        List of configurations sorted by dependencies (dependencies first)
    """
    # AIDEV-NOTE: Use grouping approach instead of complex topological sort to avoid false circular dependency detection
    if not configs:
        return []

    max_levels = 10
    groups = {1: list(configs)}

    # Iteratively move tables to higher groups based on dependencies
    for level in range(2, max_levels + 1):
        current_group = groups.get(level - 1, [])
        if not current_group:
            break

        next_level, remaining_in_current = _process_group_level(groups, level)

        groups[level] = next_level
        groups[level - 1] = remaining_in_current

        # If no tables moved, we're done
        if not groups[level]:
            break

    return _flatten_groups(groups)
