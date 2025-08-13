"""Table discovery module for connecting to Databricks and finding existing tables."""

import logging
import re
from dataclasses import dataclass

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType

logger = logging.getLogger(__name__)


@dataclass
class TableInfo:
    """Information about a discovered table."""

    catalog: str
    schema: str
    table: str
    columns: list[dict]  # Column info with name, type, nullable

    @property
    def full_name(self) -> str:
        """Get the full table name."""
        return f"{self.catalog}.{self.schema}.{self.table}"


def discover_tables(spark: SparkSession, catalog: str, schema: str, table_regex: str | None = None) -> list[TableInfo]:
    """Discover tables in a given catalog and schema.

    Args:
        spark: Databricks Spark session
        catalog: Target catalog name
        schema: Target schema name
        table_regex: Optional regex pattern to filter table names

    Returns:
        List of discovered table information
    """
    logger.info("Discovering tables in %s.%s", catalog, schema)

    try:
        # Get all tables in the schema
        tables_df = spark.sql(f"SHOW TABLES IN {catalog}.{schema}")
        table_names = [row.tableName for row in tables_df.collect()]

        # Filter by regex if provided
        if table_regex:
            pattern = re.compile(table_regex, re.IGNORECASE)
            table_names = [name for name in table_names if pattern.search(name)]
            logger.info("Filtered %d tables matching pattern: %s", len(table_names), table_regex)

        logger.info("Found %d tables to process", len(table_names))

        # Get detailed info for each table
        discovered_tables = []
        for table_name in table_names:
            table_info = get_table_info(spark, catalog, schema, table_name)
            if table_info:
                discovered_tables.append(table_info)

        logger.info("Successfully discovered %d tables", len(discovered_tables))
        return discovered_tables

    except Exception as e:
        logger.error("Error discovering tables: %s", e)
        raise


def get_table_info(spark: SparkSession, catalog: str, schema: str, table: str) -> TableInfo | None:
    """Get detailed information about a specific table.

    Args:
        spark: Databricks Spark session
        catalog: Catalog name
        schema: Schema name
        table: Table name

    Returns:
        Table information or None if error
    """
    try:
        full_table_name = f"{catalog}.{schema}.{table}"
        logger.debug("Getting info for table: %s", full_table_name)

        # Get table schema
        table_df = spark.read.table(full_table_name)
        spark_schema: StructType = table_df.schema

        # Convert to our format
        columns = []
        for field in spark_schema.fields:
            column_info = {
                "name": field.name,
                "type": str(field.dataType),
                "nullable": field.nullable,
                "spark_type": field.dataType,
            }
            columns.append(column_info)

        return TableInfo(catalog=catalog, schema=schema, table=table, columns=columns)

    except Exception as e:
        logger.error("Error getting info for table %s.%s.%s: %s", catalog, schema, table, e)
        return None
