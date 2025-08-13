"""YAML output module for writing generated configurations to files."""

import logging
from pathlib import Path

import yaml

from cloe_synthetic_data_generator.config import DataGenConfig

logger = logging.getLogger(__name__)


def write_config_to_yaml(config: DataGenConfig, output_path: Path) -> None:
    """Write a DataGenConfig to a YAML file.

    Args:
        config: Configuration to write
        output_path: Path where to write the YAML file
    """
    logger.info("Writing config to: %s", output_path)

    # AIDEV-NOTE: Use Pydantic's model_dump() with exclude to maintain consistency with model structure
    # Exclude fields that shouldn't be in the output YAML
    config_dict = config.model_dump(
        mode="json",
        exclude={
            "batch_size": True,  # Internal processing parameter
            "columns": {
                "__all__": {
                    "description",
                    "unique",
                    "depends_on",
                    "reference_mapping",
                    "reference_table",
                }
            },
        },
    )

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False, indent=2)

    logger.info("✅ Successfully wrote config to %s", output_path)


def write_configs_to_directory(
    configs: list[DataGenConfig], output_dir: Path, filename_template: str = "{table_name}_config.yaml"
) -> list[Path]:
    """Write multiple configurations to YAML files in a directory.

    Args:
        configs: List of configurations to write
        output_dir: Directory where to write the YAML files
        filename_template: Template for filenames (can use {table_name}, {catalog}, {schema_name})

    Returns:
        List of paths where files were written
    """
    logger.info("Writing %d configs to directory: %s", len(configs), output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    written_files = []

    for config in configs:
        # Generate filename from template
        filename = filename_template.format(
            table_name=config.target.table,
            catalog=config.target.catalog,
            schema_name=config.target.schema_name,
        )

        output_path = output_dir / filename

        # Avoid overwriting files without confirmation
        if output_path.exists():
            logger.warning("File already exists, overwriting: %s", output_path)

        write_config_to_yaml(config, output_path)
        written_files.append(output_path)

    logger.info("✅ Successfully wrote %d config files", len(written_files))
    return written_files
