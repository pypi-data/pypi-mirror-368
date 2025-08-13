"""Data generation module using Faker and configuration."""

import logging
import random
from collections import defaultdict
from typing import Any

import pandas as pd
from faker import Faker

from cloe_synthetic_data_generator.config import ColumnConfig, DataGenConfig

logger = logging.getLogger(__name__)


def get_reference_values(column: ColumnConfig, dataframe_cache: dict | None = None) -> list[Any]:
    """Get reference values from an external table.

    Args:
        column: Column configuration with reference_table
        dataframe_cache: Dictionary of cached DataFrames by table path

    Returns:
        List of distinct values from the reference table

    Raises:
        ValueError: If reference table cannot be accessed or is empty
    """
    if not column.reference_table:
        msg = f"No reference table specified for column '{column.name}'"
        raise ValueError(msg)

    ref_table = column.reference_table
    table_path = f"{ref_table.catalog}.{ref_table.schema_name}.{ref_table.table}"

    # Try cached DataFrame first
    if dataframe_cache and table_path in dataframe_cache:
        logger.info("Using cached DataFrame for reference values from %s.%s", table_path, ref_table.key_column)
        df = dataframe_cache[table_path]

        if ref_table.key_column not in df.columns:
            msg = f"Column '{ref_table.key_column}' not found in cached DataFrame for {table_path}"
            raise ValueError(msg)

        values = df[ref_table.key_column].dropna().unique().tolist()

        if not values:
            msg = f"No values found in cached DataFrame {table_path}.{ref_table.key_column}"
            raise ValueError(msg)

        logger.info("Found %d reference values from cached %s", len(values), table_path)
        return list(values)

    logger.error("Error querying reference table %s", table_path)
    raise ValueError("Reference table lookup failed")


def _generate_unique_reference_value(
    reference_values: list[Any], column: ColumnConfig, unique_values: dict[str, set]
) -> Any:
    """Generate a unique value from reference table values."""
    available_values = [v for v in reference_values if v not in unique_values[column.name]]

    if not available_values:
        msg = f"No more unique reference values available for column '{column.name}'"
        raise ValueError(msg)

    chosen_value = random.choice(available_values)
    unique_values[column.name].add(chosen_value)
    return chosen_value


def _generate_unique_faker_value(faker: Faker, column: ColumnConfig, unique_values: dict[str, set]) -> Any:
    """Generate a unique value using faker with retry logic."""
    max_attempts = 1000
    for _ in range(max_attempts):
        if not column.faker_function:
            msg = f"No faker_function specified for unique column '{column.name}'"
            raise ValueError(msg)

        faker_method = getattr(faker, column.faker_function)
        value = faker_method(**column.faker_options) if column.faker_options else faker_method()

        if value not in unique_values[column.name]:
            unique_values[column.name].add(value)
            return value

    msg = f"Could not generate unique value for column '{column.name}' after {max_attempts} attempts"
    raise ValueError(msg)


def _generate_regular_faker_value(faker: Faker, column: ColumnConfig) -> Any:
    """Generate a regular faker value."""
    if not column.faker_function:
        msg = f"No faker_function specified for column '{column.name}'"
        raise ValueError(msg)

    faker_method = getattr(faker, column.faker_function)
    return faker_method(**column.faker_options) if column.faker_options else faker_method()


def generate_fake_value(
    faker: Faker,
    column: ColumnConfig,
    unique_values: dict[str, set] | None = None,
    dataframe_cache: dict | None = None,
) -> Any:
    """Generate a fake value for a column based on its configuration.

    Args:
        faker: Faker instance
        column: Column configuration
        unique_values: Dictionary tracking unique values per column
        dataframe_cache: Dictionary of cached DataFrames by table path

    Returns:
        Generated fake value
    """
    # Handle reference table columns (no dependency)
    if column.reference_table and not column.depends_on:
        reference_values = get_reference_values(column, dataframe_cache)

        if column.unique:
            if unique_values is None:
                unique_values = defaultdict(set)
            return _generate_unique_reference_value(reference_values, column, unique_values)

        return random.choice(reference_values)

    # Handle nullable columns
    if column.nullable and faker.boolean(chance_of_getting_true=10):
        return None

    # Initialize unique_values if needed
    if column.unique and unique_values is None:
        unique_values = defaultdict(set)

    # Handle unique constraint
    if column.unique and unique_values is not None:
        return _generate_unique_faker_value(faker, column, unique_values)

    # Generate regular value
    return _generate_regular_faker_value(faker, column)


def _lookup_dependent_reference_table(parent_value: Any, column: ColumnConfig, dataframe_cache: dict) -> Any:
    """Lookup dependent value from reference table."""
    ref_table = column.reference_table
    if not ref_table:
        raise ValueError("No reference table specified")

    table_path = f"{ref_table.catalog}.{ref_table.schema_name}.{ref_table.table}"

    if table_path not in dataframe_cache:
        logger.error("Error querying reference table %s", table_path)
        raise ValueError("Reference table lookup failed")

    logger.info("Using cached DataFrame for dependent lookup from %s", table_path)
    df = dataframe_cache[table_path]

    if column.depends_on not in df.columns or ref_table.key_column not in df.columns:
        msg = (
            f"Required columns '{column.depends_on}' or '{ref_table.key_column}' "
            f"not found in cached DataFrame for {table_path}"
        )
        raise ValueError(msg)

    # Filter by parent value and get distinct target column values
    filtered_df = df[df[column.depends_on] == parent_value]
    values = filtered_df[ref_table.key_column].dropna().unique().tolist()

    if not values:
        msg = f"No values found in cached DataFrame {table_path} for parent value '{parent_value}'"
        raise ValueError(msg)

    return random.choice(values)


def _lookup_dependent_reference_mapping(parent_value: Any, column: ColumnConfig) -> Any:
    """Lookup dependent value from reference mapping."""
    if not column.reference_mapping:
        msg = f"No reference mapping found for dependent column '{column.name}'"
        raise ValueError(msg)

    if parent_value not in column.reference_mapping:
        msg = f"Parent value '{parent_value}' not found in reference mapping for column '{column.name}'"
        raise ValueError(msg)

    mapped_value = column.reference_mapping[parent_value]

    # AIDEV-NOTE: Handle one-to-many mappings by random selection from list
    if isinstance(mapped_value, list):
        if not mapped_value:
            msg = f"Empty list in reference mapping for parent value '{parent_value}' in column '{column.name}'"
            raise ValueError(msg)
        return random.choice(mapped_value)

    return mapped_value


def generate_dependent_value(parent_value: Any, column: ColumnConfig, dataframe_cache: dict | None = None) -> Any:
    """Generate a dependent value based on parent column value and reference mapping or table.

    Args:
        parent_value: Value from the parent column
        column: Column configuration with reference mapping or reference table
        dataframe_cache: Dictionary of cached DataFrames by table path

    Returns:
        Dependent value based on reference mapping or table lookup

    Raises:
        ValueError: If parent value not found in reference mapping or table query fails
    """
    if column.reference_table:
        if dataframe_cache is None:
            raise ValueError("Dataframe cache is required for reference table lookup")
        return _lookup_dependent_reference_table(parent_value, column, dataframe_cache)

    return _lookup_dependent_reference_mapping(parent_value, column)


def _generate_column_value(
    column: ColumnConfig,
    record: dict[str, Any],
    faker: Faker,
    unique_values: dict[str, set],
    dataframe_cache: dict | None,
) -> Any:
    """Generate value for a single column."""
    if column.depends_on:
        parent_value = record.get(column.depends_on)
        if parent_value is None:
            msg = f"Parent column '{column.depends_on}' has null value for dependent column '{column.name}'"
            raise ValueError(msg)
        return generate_dependent_value(parent_value, column, dataframe_cache)

    return generate_fake_value(faker, column, unique_values, dataframe_cache)


def _generate_single_record(
    sorted_columns: list[ColumnConfig], faker: Faker, unique_values: dict[str, set], dataframe_cache: dict | None
) -> dict[str, Any]:
    """Generate a single data record."""
    record: dict[str, Any] = {}
    for column in sorted_columns:
        try:
            record[column.name] = _generate_column_value(column, record, faker, unique_values, dataframe_cache)
        except Exception as e:
            logger.error("Error generating value for column %s: %s", column.name, e)
            raise
    return record


def generate_fake_data_from_config(config: DataGenConfig, dataframe_cache: dict | None = None) -> pd.DataFrame:
    """Generate fake data based on configuration.

    Args:
        config: Data generation configuration
        dataframe_cache: Dictionary of cached DataFrames by table path

    Returns:
        pandas DataFrame with fake data
    """
    faker = Faker()
    data = []
    unique_values: dict[str, set] = defaultdict(set)

    logger.info("Generating %d fake records...", config.num_records)
    sorted_columns = config.get_dependency_sorted_columns()

    for i in range(config.num_records):
        if i % 100 == 0:
            logger.debug("Generated %d records...", i)

        record = _generate_single_record(sorted_columns, faker, unique_values, dataframe_cache)
        data.append(record)

    logger.info("Successfully generated %d records", config.num_records)
    return pd.DataFrame(data)
