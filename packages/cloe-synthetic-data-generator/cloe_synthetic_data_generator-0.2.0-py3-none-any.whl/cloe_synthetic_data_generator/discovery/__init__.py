"""Discovery module for auto-generating YAML configs from existing Databricks tables."""

from .config_generator import (
    generate_config_from_table,
    guess_faker_options,
)
from .table_discovery import (
    TableInfo,
    discover_tables,
    get_table_info,
)
from .yaml_writer import (
    write_config_to_yaml,
    write_configs_to_directory,
)

__all__ = [
    "discover_tables",
    "get_table_info",
    "TableInfo",
    "generate_config_from_table",
    "guess_faker_options",
    "write_config_to_yaml",
    "write_configs_to_directory",
]
