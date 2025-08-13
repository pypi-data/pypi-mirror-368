"""Command Line Interface using Typer."""

import logging
from pathlib import Path
from typing import Annotated

import pandas as pd
import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from cloe_synthetic_data_generator.config import DataGenConfig, resolve_table_generation_order
from cloe_synthetic_data_generator.config_loader import load_config, load_configs_from_directory
from cloe_synthetic_data_generator.generate.data_generator import generate_fake_data_from_config
from cloe_synthetic_data_generator.spark_utils import (
    create_spark_dataframe_from_config,
    verify_table_write,
    write_to_unity_catalog,
)

# Initialize Typer app and Rich console
app = typer.Typer(
    name="cloe-synthetic-data-generator",
    help="Generate synthetic data and write to Unity Catalog using YAML configuration.",
    rich_markup_mode="rich",
)
console = Console()

# Global logger
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Setup rich logging configuration.

    Args:
        verbose: Enable debug level logging if True
    """
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


def process_single_config(config: DataGenConfig, dataframe_cache: dict | None = None) -> None:
    """Process a single configuration to generate and write data.

    Args:
        config: Data generation configuration
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Show config info
        table = Table(title=f"Configuration: {config.name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Target Table", config.get_table_path())
        table.add_row("Columns", str(len(config.columns)))
        table.add_row("Records", str(config.num_records))
        table.add_row("Write Mode", config.target.write_mode)

        console.print(table)

        # Initialize Databricks Connect session
        task = progress.add_task("Connecting to Databricks...", total=None)
        logger.info("Initializing Databricks Connect session...")

        try:
            from databricks.connect import DatabricksSession

            spark = DatabricksSession.builder.getOrCreate()
            progress.update(task, description="✅ Connected to Databricks!")
            logger.info("Successfully connected to Databricks!")
        except Exception as e:
            progress.stop()
            console.print(f"[red]❌ Failed to connect to Databricks: {e}[/red]")
            raise typer.Exit(1) from e

        # Generate fake data
        progress.update(task, description="Generating fake data...")
        if dataframe_cache is None:
            dataframe_cache = {}
        pandas_df = generate_fake_data_from_config(config, dataframe_cache)

        # Convert to Spark DataFrame
        progress.update(task, description="Converting to Spark DataFrame...")
        spark_df = create_spark_dataframe_from_config(pandas_df, config, spark)

        # Show sample data
        progress.update(task, description="Preparing sample data...")
        console.print("\n[bold]Sample generated data:[/bold]")
        spark_df.show(5, truncate=False)

        # Write to Unity Catalog
        progress.update(task, description="Writing to Unity Catalog...")
        write_to_unity_catalog(
            spark_df, config.target.catalog, config.target.schema_name, config.target.table, config.target.write_mode
        )

        # Verify the write
        progress.update(task, description="Verifying write...")
        verify_table_write(spark, config.target.catalog, config.target.schema_name, config.target.table)

        # Cache the generated data for dependent tables
        if dataframe_cache is not None:
            progress.update(task, description="Caching data for dependent tables...")
            table_path = config.get_table_path()
            # Store the pandas DataFrame in cache for faster reference lookups
            dataframe_cache[table_path] = pandas_df
            logger.info("Cached %d records for table %s", len(pandas_df), table_path)

        progress.update(task, description="✅ Completed successfully!")

    console.print(
        f"\n[green]🎉 Successfully generated {config.num_records} records "
        f"and wrote to {config.get_table_path()}[/green]"
    )


@app.command()
def generate(
    config: Annotated[
        Path | None,
        typer.Option(
            "--config",
            "-c",
            help="Path to YAML configuration file",
            exists=True,
            file_okay=True,
            dir_okay=False,
        ),
    ] = None,
    config_dir: Annotated[
        Path | None,
        typer.Option(
            "--config-dir",
            "-d",
            help="Path to directory containing YAML configuration files",
            exists=True,
            file_okay=False,
            dir_okay=True,
        ),
    ] = None,
    num_records: Annotated[
        int | None,
        typer.Option(
            "--num-records",
            "-n",
            help="Override number of records from config",
            min=1,
        ),
    ] = None,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose (debug) logging")] = False,
) -> None:
    """Generate fake data from YAML configuration and write to Unity Catalog."""

    # Validate input - exactly one of config or config_dir must be provided
    if not config and not config_dir:
        console.print("[red]Error: Must provide either --config or --config-dir[/red]")
        raise typer.Exit(1)

    if config and config_dir:
        console.print("[red]Error: Cannot use both --config and --config-dir[/red]")
        raise typer.Exit(1)

    # Setup logging
    setup_logging(verbose)

    try:
        configs = []

        if config:
            # Load single configuration
            console.print(f"[blue]Loading configuration from {config}...[/blue]")
            config_obj = load_config(config)

            # Override num_records if provided
            if num_records:
                config_obj.num_records = num_records

            configs = [config_obj]

        elif config_dir:
            # Load all configurations from directory
            console.print(f"[blue]Loading configurations from directory {config_dir}...[/blue]")
            configs = load_configs_from_directory(config_dir)

            # Show loaded configs
            table = Table(title="Loaded Configurations")
            table.add_column("Name", style="cyan")
            table.add_column("Target Table", style="green")
            table.add_column("Records", style="yellow")

            for cfg in configs:
                table.add_row(cfg.name, cfg.get_table_path(), str(cfg.num_records))

            console.print(table)

            # Override num_records for all configs if provided
            if num_records:
                for cfg in configs:
                    cfg.num_records = num_records
                console.print(f"[yellow]Overriding record count to {num_records} for all configurations[/yellow]")

        # AIDEV-NOTE: Resolve table dependencies and process in correct order
        if len(configs) > 1:
            try:
                console.print("\n[blue]Analyzing table dependencies...[/blue]")
                ordered_configs = resolve_table_generation_order(configs)

                # Show dependency order if it changed
                if ordered_configs != configs:
                    dep_table = Table(title="Resolved Generation Order")
                    dep_table.add_column("Order", style="cyan", justify="right")
                    dep_table.add_column("Table", style="green")
                    dep_table.add_column("Dependencies", style="yellow")

                    for idx, cfg in enumerate(ordered_configs, 1):
                        deps = cfg.get_table_dependencies()
                        dep_str = ", ".join(deps) if deps else "None"
                        dep_table.add_row(str(idx), cfg.get_table_path(), dep_str)

                    console.print(dep_table)
                    console.print("[green]✅ Dependencies resolved successfully![/green]")
                else:
                    console.print("[dim]No table dependencies found, using original order[/dim]")
            except ValueError as e:
                console.print(f"[red]❌ Dependency resolution failed: {e}[/red]")
                raise typer.Exit(1) from e
        else:
            ordered_configs = configs

        # Process each configuration in dependency order with shared cache
        dataframe_cache: dict[str, pd.DataFrame] = {}
        for i, config_obj in enumerate(ordered_configs, 1):
            if len(ordered_configs) > 1:
                console.print(f"\n[bold blue]=== Processing configuration {i}/{len(ordered_configs)} ===[/bold blue]")

            process_single_config(config_obj, dataframe_cache)

            if len(ordered_configs) > 1 and i < len(ordered_configs):
                console.print("\n[dim]--- Moving to next configuration ---[/dim]")

        if len(configs) > 1:
            console.print(f"\n[green]🎉 All {len(configs)} configurations processed successfully![/green]")

    except Exception as e:
        logger.error("Error: %s", e)
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def test_connection() -> None:
    """Test Databricks Connect connection."""
    setup_logging(False)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Testing Databricks Connect connection...", total=None)

        try:
            from databricks.connect import DatabricksSession

            spark = DatabricksSession.builder.getOrCreate()

            progress.update(task, description="✅ Connected! Reading sample data...")

            df = spark.read.table("samples.nyctaxi.trips")
            row_count = df.count()

            progress.update(task, description="✅ Connection test completed!")

            console.print("\n[green]✅ Successfully connected to Databricks![/green]")
            console.print(f"[blue]Sample table 'samples.nyctaxi.trips' contains {row_count:,} rows[/blue]")

            console.print("\n[bold]Sample data:[/bold]")
            df.show(5)

        except Exception as e:
            progress.stop()
            console.print(f"[red]❌ Connection failed: {e}[/red]")
            raise typer.Exit(1) from e


@app.command()
def list_configs(
    config_dir: Annotated[
        Path,
        typer.Argument(
            help="Path to directory containing YAML configuration files",
            exists=True,
            file_okay=False,
            dir_okay=True,
        ),
    ],
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Show detailed configuration information")] = False,
) -> None:
    """List all YAML configuration files in a directory."""
    setup_logging(False)

    try:
        configs = load_configs_from_directory(config_dir)

        if not verbose:
            # Simple table
            table = Table(title=f"Configurations in {config_dir}")
            table.add_column("Name", style="cyan")
            table.add_column("Target Table", style="green")
            table.add_column("Records", style="yellow", justify="right")
            table.add_column("Columns", style="blue", justify="right")

            for config in configs:
                table.add_row(config.name, config.get_table_path(), str(config.num_records), str(len(config.columns)))
        else:
            # Detailed table
            table = Table(title=f"Detailed Configurations in {config_dir}")
            table.add_column("Name", style="cyan")
            table.add_column("Target", style="green")
            table.add_column("Records", style="yellow", justify="right")
            table.add_column("Columns", style="blue", justify="right")
            table.add_column("Write Mode", style="magenta")
            table.add_column("Column Names", style="dim")

            for config in configs:
                column_names = ", ".join([col.name for col in config.columns[:5]])
                if len(config.columns) > 5:
                    column_names += f", ... (+{len(config.columns) - 5} more)"

                table.add_row(
                    config.name,
                    config.get_table_path(),
                    str(config.num_records),
                    str(len(config.columns)),
                    config.target.write_mode,
                    column_names,
                )

        console.print(table)
        console.print(f"\n[blue]Found {len(configs)} configuration(s)[/blue]")

    except Exception as e:
        console.print(f"[red]❌ Error listing configurations: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def validate_config(
    config: Annotated[
        Path,
        typer.Argument(
            help="Path to YAML configuration file to validate",
            exists=True,
            file_okay=True,
            dir_okay=False,
        ),
    ],
) -> None:
    """Validate a YAML configuration file."""
    setup_logging(False)

    try:
        config_obj = load_config(config)

        console.print(f"[green]✅ Configuration '{config}' is valid![/green]")

        # Show configuration details
        table = Table(title="Configuration Details")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Name", config_obj.name)
        table.add_row("Target Table", config_obj.get_table_path())
        table.add_row("Write Mode", config_obj.target.write_mode)
        table.add_row("Records", str(config_obj.num_records))
        table.add_row("Batch Size", str(config_obj.batch_size))
        table.add_row("Columns", str(len(config_obj.columns)))

        console.print(table)

        # Show column details
        if config_obj.columns:
            columns_table = Table(title="Column Definitions")
            columns_table.add_column("Name", style="cyan")
            columns_table.add_column("Type", style="green")
            columns_table.add_column("Nullable", style="yellow")
            columns_table.add_column("Faker Function", style="blue")

            for col in config_obj.columns:
                columns_table.add_row(
                    col.name, col.data_type.value, "Yes" if col.nullable else "No", col.faker_function
                )

            console.print(columns_table)

    except Exception as e:
        console.print(f"[red]❌ Configuration validation failed: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def discover(
    catalog: Annotated[
        str,
        typer.Option(
            "--catalog",
            "-c",
            help="Target catalog name in Unity Catalog",
        ),
    ],
    schema: Annotated[
        str,
        typer.Option(
            "--schema",
            "-s",
            help="Target schema name within the catalog",
        ),
    ],
    table_regex: Annotated[
        str | None,
        typer.Option(
            "--table-regex",
            "-t",
            help="Optional regex pattern to filter table names (if not provided, all tables are processed)",
        ),
    ] = None,
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            "-o",
            help="Directory where to write the generated YAML config files",
        ),
    ] = Path("./discovered_configs"),
    num_records: Annotated[
        int,
        typer.Option(
            "--num-records",
            "-n",
            help="Number of records to generate for each table",
            min=1,
        ),
    ] = 1000,
    write_mode: Annotated[
        str,
        typer.Option(
            "--write-mode",
            "-w",
            help="Write mode for the tables",
        ),
    ] = "overwrite",
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Enable verbose logging",
        ),
    ] = False,
) -> None:
    """Discover existing tables and auto-generate YAML configurations.

    This command connects to Databricks, discovers tables in the specified catalog and schema,
    and generates YAML configuration files with intelligent faker function guessing based on
    column names and data types.
    """
    setup_logging(verbose)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Initialize Databricks Connect session
        task = progress.add_task("Connecting to Databricks...", total=None)
        logger.info("Initializing Databricks Connect session...")

        try:
            from databricks.connect import DatabricksSession

            spark = DatabricksSession.builder.getOrCreate()
            progress.update(task, description="✅ Connected to Databricks!")
            logger.info("Successfully connected to Databricks!")
        except Exception as e:
            progress.stop()
            console.print(f"[red]❌ Failed to connect to Databricks: {e}[/red]")
            raise typer.Exit(1) from e

        # Discover tables
        progress.update(task, description="Discovering tables...")
        from cloe_synthetic_data_generator.discovery import (
            discover_tables,
            generate_config_from_table,
            write_configs_to_directory,
        )

        try:
            discovered_tables = discover_tables(spark, catalog, schema, table_regex)

            if not discovered_tables:
                progress.stop()
                console.print("[yellow]⚠️  No tables found matching the criteria[/yellow]")
                return

            progress.update(task, description=f"Found {len(discovered_tables)} tables...")

            # Show discovered tables
            tables_table = Table(title=f"Discovered Tables in {catalog}.{schema}")
            tables_table.add_column("Table Name", style="cyan")
            tables_table.add_column("Columns", style="green")
            tables_table.add_column("Full Path", style="blue")

            for table_info in discovered_tables:
                tables_table.add_row(table_info.table, str(len(table_info.columns)), table_info.full_name)

            console.print(tables_table)

            # Generate configurations
            progress.update(task, description="Generating YAML configurations...")
            configs = []
            for table_info in discovered_tables:
                config = generate_config_from_table(table_info, num_records, write_mode)
                configs.append(config)

            # Write configurations to files
            progress.update(task, description="Writing YAML files...")
            written_files = write_configs_to_directory(
                configs, output_dir, filename_template="{catalog}_{schema_name}_{table_name}_config.yaml"
            )

            progress.update(task, description="✅ Discovery completed!")

        except Exception as e:
            progress.stop()
            console.print(f"[red]❌ Error during discovery: {e}[/red]")
            raise typer.Exit(1) from e

    # Show results
    results_table = Table(title="Discovery Results")
    results_table.add_column("Property", style="cyan")
    results_table.add_column("Value", style="green")

    results_table.add_row("Tables Discovered", str(len(discovered_tables)))
    results_table.add_row("Configs Generated", str(len(configs)))
    results_table.add_row("Output Directory", str(output_dir))
    results_table.add_row("Records per Table", str(num_records))
    results_table.add_row("Write Mode", write_mode)

    console.print(results_table)

    # Show generated files
    files_table = Table(title="Generated Configuration Files")
    files_table.add_column("File", style="cyan")
    files_table.add_column("Table", style="blue")

    for _, (file_path, config) in enumerate(zip(written_files, configs, strict=False)):
        files_table.add_row(str(file_path.name), config.get_table_path())

    console.print(files_table)

    console.print(
        f"\n[green]🎉 Successfully discovered {len(discovered_tables)} tables and "
        f"generated {len(configs)} YAML configuration files in {output_dir}[/green]"
    )


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
