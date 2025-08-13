"""Configuration generator module for creating YAML configs from table information."""

import logging

from cloe_synthetic_data_generator.config import (
    ColumnConfig,
    DataGenConfig,
    SparkDataType,
    TableTarget,
)
from cloe_synthetic_data_generator.discovery.table_discovery import TableInfo

logger = logging.getLogger(__name__)


def spark_type_to_enum(spark_type: str) -> SparkDataType:
    """Convert Spark SQL type string to our enum.

    Args:
        spark_type: String representation of Spark type

    Returns:
        Corresponding SparkDataType enum value
    """
    type_mapping = {
        "StringType": SparkDataType.STRING,
        "IntegerType": SparkDataType.INTEGER,
        "LongType": SparkDataType.LONG,
        "DoubleType": SparkDataType.DOUBLE,
        "FloatType": SparkDataType.FLOAT,
        "BooleanType": SparkDataType.BOOLEAN,
        "DateType": SparkDataType.DATE,
        "TimestampType": SparkDataType.TIMESTAMP,
        "DecimalType": SparkDataType.DECIMAL,
    }

    # Handle complex types like DecimalType(10,2)
    base_type = spark_type.split("(")[0]
    return type_mapping.get(base_type, SparkDataType.STRING)


def guess_faker_options(column_name: str, data_type: SparkDataType) -> dict[str, str]:
    """Guess appropriate faker function and options based on column name and type.

    Args:
        column_name: Name of the column
        data_type: Data type of the column

    Returns:
        Dictionary with faker function and options
    """
    column_lower = column_name.lower()

    # Common patterns for different data types
    if data_type == SparkDataType.STRING:
        # Email patterns
        if any(pattern in column_lower for pattern in ["email", "mail"]):
            return {"function": "email"}

        # Name patterns
        if any(pattern in column_lower for pattern in ["first_name", "firstname", "fname"]):
            return {"function": "first_name"}
        if any(pattern in column_lower for pattern in ["last_name", "lastname", "lname", "surname"]):
            return {"function": "last_name"}
        if "full_name" in column_lower or column_lower in ["name", "full_name"]:
            return {"function": "name"}

        # Address patterns
        if any(pattern in column_lower for pattern in ["address", "street", "addr"]):
            return {"function": "address"}
        if any(pattern in column_lower for pattern in ["city", "town"]):
            return {"function": "city"}
        if any(pattern in column_lower for pattern in ["state", "province"]):
            return {"function": "state"}
        if any(pattern in column_lower for pattern in ["country", "nation"]):
            return {"function": "country"}
        if any(pattern in column_lower for pattern in ["zip", "postal", "postcode"]):
            return {"function": "zipcode"}

        # Phone patterns
        if any(pattern in column_lower for pattern in ["phone", "tel", "mobile", "cell"]):
            return {"function": "phone_number"}

        # Company patterns
        if any(pattern in column_lower for pattern in ["company", "organization", "org", "employer"]):
            return {"function": "company"}
        if any(pattern in column_lower for pattern in ["department", "dept"]):
            return {
                "function": "random_element",
                "elements": "['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations']",
            }
        if any(pattern in column_lower for pattern in ["job", "title", "position", "role"]):
            return {"function": "job"}

        # ID patterns
        if any(pattern in column_lower for pattern in ["id", "uuid", "guid"]):
            return {"function": "uuid4"}
        if "ssn" in column_lower or "social_security" in column_lower:
            return {"function": "ssn"}

        # Text patterns
        if any(pattern in column_lower for pattern in ["description", "comment", "note", "text"]):
            return {"function": "text", "max_nb_chars": "200"}
        if any(pattern in column_lower for pattern in ["url", "website", "link"]):
            return {"function": "url"}

        # Default for strings
        return {"function": "word"}

    if data_type == SparkDataType.INTEGER:
        # Age patterns
        if "age" in column_lower:
            return {"function": "random_int", "min": "18", "max": "80"}
        # Year patterns
        if "year" in column_lower:
            return {"function": "random_int", "min": "1990", "max": "2024"}
        # Count patterns
        if any(pattern in column_lower for pattern in ["count", "number", "qty", "quantity"]):
            return {"function": "random_int", "min": "1", "max": "1000"}
        # ID patterns
        if "id" in column_lower:
            return {"function": "random_int", "min": "1", "max": "999999"}
        # Default for integers
        return {"function": "random_int", "min": "1", "max": "100"}

    if data_type == SparkDataType.LONG:
        # Similar to integer but larger ranges
        if "id" in column_lower:
            return {"function": "random_int", "min": "1000000", "max": "9999999999"}
        return {"function": "random_int", "min": "1", "max": "10000"}

    if data_type in [SparkDataType.DOUBLE, SparkDataType.FLOAT]:
        # Positive patterns
        if any(
            pattern in column_lower for pattern in ["salary", "wage", "pay", "income", "price", "cost", "amount", "fee"]
        ):
            return {"function": "pyfloat", "left_digits": "5", "right_digits": "2", "positive": "true"}
        # Default for floats
        return {"function": "pyfloat", "left_digits": "2", "right_digits": "2"}

    if data_type == SparkDataType.BOOLEAN:
        return {"function": "pybool"}

    if data_type == SparkDataType.DATE:
        # Default for dates
        return {"function": "date_between", "start_date": "-5y", "end_date": "today"}

    if data_type == SparkDataType.TIMESTAMP:
        # Created/updated patterns
        if any(pattern in column_lower for pattern in ["created", "updated", "modified", "timestamp"]):
            return {"function": "date_time_between", "start_date": "-1y", "end_date": "now"}
        # Default for timestamps
        return {"function": "date_time_between", "start_date": "-30d", "end_date": "now"}

    if data_type == SparkDataType.DECIMAL:
        # Similar to float but for decimal types
        if any(
            pattern in column_lower for pattern in ["salary", "wage", "pay", "income", "price", "cost", "amount", "fee"]
        ):
            return {"function": "pydecimal", "left_digits": "5", "right_digits": "2", "positive": "true"}
        return {"function": "pydecimal", "left_digits": "2", "right_digits": "2"}

    # Fallback
    return {"function": "word"}


def generate_config_from_table(
    table_info: TableInfo, num_records: int = 1000, write_mode: str = "overwrite"
) -> DataGenConfig:
    """Generate a complete YAML configuration from table information.

    Args:
        table_info: Information about the table
        num_records: Number of records to generate
        write_mode: Write mode for the table

    Returns:
        Complete data generation configuration
    """
    logger.info("Generating config for table: %s", table_info.full_name)

    # Generate column configurations
    columns = []
    for col_info in table_info.columns:
        data_type = spark_type_to_enum(col_info["type"])
        faker_options = guess_faker_options(col_info["name"], data_type)

        column_config = ColumnConfig(
            name=col_info["name"],
            data_type=data_type,
            nullable=col_info["nullable"],
            faker_function=faker_options["function"],
            faker_options=faker_options,
        )
        columns.append(column_config)

        logger.debug("Column %s: %s with faker %s", col_info["name"], data_type, faker_options["function"])

    # Create target configuration
    target = TableTarget(
        catalog=table_info.catalog,
        schema_name=table_info.schema,
        table=table_info.table,
        write_mode=write_mode,
    )

    # Create complete configuration
    config = DataGenConfig(
        name=f"{table_info.table.title()} Data Generation", num_records=num_records, columns=columns, target=target
    )

    logger.info("Generated config with %d columns for %s", len(columns), table_info.full_name)
    return config
