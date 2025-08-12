"""Generation module for synthetic data generation and Unity Catalog writing."""

from .data_processor import (
    process_multiple_configs,
    process_single_config,
)
from .unity_catalog_writer import (
    connect_to_databricks,
    write_and_verify,
)

__all__ = [
    "process_single_config",
    "process_multiple_configs",
    "connect_to_databricks",
    "write_and_verify",
]
