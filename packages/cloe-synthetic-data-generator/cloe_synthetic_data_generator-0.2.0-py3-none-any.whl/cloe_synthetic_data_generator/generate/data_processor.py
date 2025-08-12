"""Data processing module for generating and managing synthetic data workflows."""

import logging

from rich.console import Console
from rich.progress import Progress
from rich.table import Table

from cloe_synthetic_data_generator.config import DataGenConfig
from cloe_synthetic_data_generator.generate.data_generator import generate_fake_data_from_config
from cloe_synthetic_data_generator.spark_utils import create_spark_dataframe_from_config

from .unity_catalog_writer import connect_to_databricks, write_and_verify

logger = logging.getLogger(__name__)
console = Console()


def process_single_config(
    config: DataGenConfig, progress: Progress, show_sample: bool = True, dataframe_cache: dict | None = None
) -> None:
    """Process a single configuration to generate and write data.

    Args:
        config: Data generation configuration
        progress: Rich progress instance for status updates
        show_sample: Whether to show sample data output
    """
    # Show config info
    table = Table(title=f"Configuration: {config.name}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Target Table", config.get_table_path())
    table.add_row("Columns", str(len(config.columns)))
    table.add_row("Records", str(config.num_records))
    table.add_row("Write Mode", config.target.write_mode)

    console.print(table)

    # Connect to Databricks
    task = progress.add_task("Connecting to Databricks...", total=None)
    spark = connect_to_databricks(progress, task)

    # Generate fake data
    progress.update(task, description="Generating fake data...")
    pandas_df = generate_fake_data_from_config(config, dataframe_cache)

    # Add to cache for future reference by other configs
    if dataframe_cache is not None:
        table_path = config.get_table_path()
        dataframe_cache[table_path] = pandas_df
        logger.info("Cached DataFrame for %s (%d rows)", table_path, len(pandas_df))

    # Convert to Spark DataFrame
    progress.update(task, description="Converting to Spark DataFrame...")
    spark_df = create_spark_dataframe_from_config(pandas_df, config, spark)

    # Show sample data
    if show_sample:
        progress.update(task, description="Preparing sample data...")
        console.print("\n[bold]Sample generated data:[/bold]")
        spark_df.show(5, truncate=False)

    # Write and verify
    write_and_verify(spark_df, config, progress, task)

    progress.update(task, description="✅ Completed successfully!")

    console.print(
        f"\n[green]🎉 Successfully generated {config.num_records} records "
        f"and wrote to {config.get_table_path()}[/green]"
    )


def process_multiple_configs(configs: list[DataGenConfig], progress: Progress, show_sample: bool = True) -> None:
    """Process multiple configurations sequentially.

    Args:
        configs: List of data generation configurations
        progress: Rich progress instance for status updates
        show_sample: Whether to show sample data output
    """
    logger.info("Processing %d configurations...", len(configs))

    # Create session-scoped cache for DataFrame references
    dataframe_cache: dict[str, object] = {}

    for i, config in enumerate(configs, 1):
        if len(configs) > 1:
            console.print(f"\n[bold cyan]--- Processing configuration {i}/{len(configs)} ---[/bold cyan]")

        process_single_config(config, progress, show_sample, dataframe_cache)

        if len(configs) > 1 and i < len(configs):
            console.print("[dim]Moving to next configuration...[/dim]")

    console.print(f"\n[green]🎉 All {len(configs)} configurations processed successfully![/green]")
