"""Configuration loading utilities."""

import logging
from pathlib import Path

import yaml

from cloe_synthetic_data_generator.config import DataGenConfig

logger = logging.getLogger(__name__)


def load_config(config_path: str | Path) -> DataGenConfig:
    """Load configuration from YAML file.

    Args:
        config_path: Path to the YAML configuration file

    Returns:
        Parsed configuration object

    Raises:
        FileNotFoundError: If configuration file doesn't exist
        ValueError: If configuration is invalid
    """
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    logger.info("Loading configuration from %s", config_file)

    try:
        with config_file.open() as f:
            yaml_data = yaml.safe_load(f)

        config = DataGenConfig(**yaml_data)
        logger.info("Configuration loaded successfully: %s", config.name)
        return config

    except Exception as e:
        logger.error("Error loading configuration from %s: %s", config_file, e)
        raise


def load_configs_from_directory(directory_path: str | Path) -> list[DataGenConfig]:
    """Load all YAML configuration files from a directory.

    Args:
        directory_path: Path to directory containing YAML files

    Returns:
        List of parsed configuration objects

    Raises:
        FileNotFoundError: If directory doesn't exist
        ValueError: If no valid YAML files found
    """
    directory = Path(directory_path)
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")

    if not directory.is_dir():
        raise ValueError(f"Path is not a directory: {directory_path}")

    logger.info("Loading configurations from directory: %s", directory)

    # Find all YAML files
    yaml_files = list(directory.glob("*.yaml")) + list(directory.glob("*.yml"))

    if not yaml_files:
        raise ValueError(f"No YAML files found in directory: {directory_path}")

    configs = []
    for yaml_file in yaml_files:
        try:
            config = load_config(yaml_file)
            configs.append(config)
            logger.info("Loaded configuration: %s from %s", config.name, yaml_file.name)
        except Exception as e:
            logger.warning("Failed to load configuration from %s: %s", yaml_file, e)
            continue

    if not configs:
        raise ValueError(f"No valid configurations found in directory: {directory_path}")

    logger.info("Successfully loaded %d configurations", len(configs))
    return configs
