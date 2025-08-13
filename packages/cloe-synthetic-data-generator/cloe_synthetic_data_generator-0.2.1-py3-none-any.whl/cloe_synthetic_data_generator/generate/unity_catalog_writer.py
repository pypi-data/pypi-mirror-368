"""Unity Catalog writer module for handling Databricks connections and data writing."""

import logging
from typing import TYPE_CHECKING

from databricks.connect import DatabricksSession
from rich.console import Console
from rich.progress import Progress, TaskID

from cloe_synthetic_data_generator.config import DataGenConfig
from cloe_synthetic_data_generator.spark_utils import verify_table_write, write_to_unity_catalog

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession

logger = logging.getLogger(__name__)
console = Console()


def connect_to_databricks(progress: Progress, task_id: TaskID) -> "SparkSession":
    """
    Connect to Databricks using DatabricksSession.

    Args:
        progress: Progress tracker for UI updates
        task_id: Task ID for progress updates

    Returns:
        Configured Spark session

    Raises:
        Exception: If connection to Databricks fails
    """
    try:
        spark = DatabricksSession.builder.getOrCreate()
        progress.update(task_id, description="✅ Connected to Databricks")
        return spark
    except Exception as e:
        progress.update(task_id, description="❌ Failed to connect to Databricks")
        console.print(f"[red]Error connecting to Databricks: {e}[/red]")
        raise


def write_and_verify(spark_df: "DataFrame", config: DataGenConfig, progress: Progress, task_id: TaskID) -> None:
    """
    Write DataFrame to Unity Catalog and verify the write operation.

    Args:
        spark_df: Spark DataFrame to write
        config: Data generation configuration
        progress: Progress tracker for UI updates
        task_id: Task ID for progress updates

    Raises:
        Exception: If write or verification fails
    """
    try:
        # Write to Unity Catalog
        progress.update(task_id, description="Writing to Unity Catalog...")
        write_to_unity_catalog(
            spark_df, config.target.catalog, config.target.schema_name, config.target.table, config.target.write_mode
        )

        # Verify the write
        progress.update(task_id, description="Verifying write...")
        verify_table_write(spark_df.sparkSession, config.target.catalog, config.target.schema_name, config.target.table)

        progress.update(task_id, description="✅ Write and verification completed")

    except Exception as e:
        progress.update(task_id, description="❌ Failed to write to Unity Catalog")
        console.print(f"[red]Error writing to Unity Catalog: {e}[/red]")
        raise
