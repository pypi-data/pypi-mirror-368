"""Spark DataFrame operations module."""

import logging

import pandas as pd
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import (
    BooleanType,
    DateType,
    DecimalType,
    DoubleType,
    FloatType,
    IntegerType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

from cloe_synthetic_data_generator.config import DataGenConfig, SparkDataType

logger = logging.getLogger(__name__)


def get_spark_data_type(
    data_type: SparkDataType,
) -> (
    type[StringType]
    | type[IntegerType]
    | type[LongType]
    | type[DoubleType]
    | type[FloatType]
    | type[BooleanType]
    | type[DateType]
    | type[TimestampType]
    | type[DecimalType]
):
    """Convert SparkDataType enum to actual Spark SQL type.

    Args:
        data_type: The data type enum value

    Returns:
        Corresponding Spark SQL type class
    """
    type_mapping = {
        SparkDataType.STRING: StringType,
        SparkDataType.INTEGER: IntegerType,
        SparkDataType.LONG: LongType,
        SparkDataType.DOUBLE: DoubleType,
        SparkDataType.FLOAT: FloatType,
        SparkDataType.BOOLEAN: BooleanType,
        SparkDataType.DATE: DateType,
        SparkDataType.TIMESTAMP: TimestampType,
        SparkDataType.DECIMAL: DecimalType,
    }
    return type_mapping[data_type]


def create_spark_dataframe_from_config(
    pandas_df: pd.DataFrame, config: DataGenConfig, spark: SparkSession
) -> DataFrame:
    """Convert pandas DataFrame to Spark DataFrame with schema from config.

    Args:
        pandas_df: The pandas DataFrame to convert
        config: Data generation configuration containing schema info
        spark: Databricks Spark session

    Returns:
        Spark DataFrame with defined schema
    """
    # Build schema from configuration
    fields = []
    for column in config.columns:
        spark_type = get_spark_data_type(column.data_type)()
        field = StructField(column.name, spark_type, column.nullable)
        fields.append(field)

    schema = StructType(fields)

    logger.info("Converting pandas DataFrame to Spark DataFrame...")
    return spark.createDataFrame(pandas_df, schema=schema)  # type: ignore


def write_to_unity_catalog(df: DataFrame, catalog: str, schema: str, table: str, mode: str = "overwrite") -> None:
    """Write DataFrame to Unity Catalog table.

    Args:
        df: Spark DataFrame to write
        catalog: Unity Catalog catalog name
        schema: Schema name within the catalog
        table: Table name within the schema
        mode: Write mode ('overwrite', 'append', 'error', 'ignore')
    """
    table_path = f"{catalog}.{schema}.{table}"

    logger.info("Writing data to Unity Catalog table: %s", table_path)
    logger.info("Write mode: %s", mode)

    try:
        df.write.mode(mode).option("mergeSchema", "true").saveAsTable(table_path)

        logger.info("Successfully wrote %d records to %s", df.count(), table_path)

    except Exception as e:
        logger.error("Error writing to table %s: %s", table_path, e)
        raise


def verify_table_write(spark: SparkSession, catalog: str, schema: str, table: str) -> None:
    """Verify that data was written successfully to the table.

    Args:
        spark: Databricks Spark session
        catalog: Unity Catalog catalog name
        schema: Schema name
        table: Table name
    """
    table_path = f"{catalog}.{schema}.{table}"

    try:
        logger.info("Verifying data was written to %s...", table_path)
        verification_df = spark.read.table(table_path)  # type: ignore
        row_count = verification_df.count()

        logger.info("✅ Table %s contains %d rows", table_path, row_count)

        logger.info("Sample data from the table:")
        verification_df.show(3, truncate=False)

        logger.info("Schema:")
        verification_df.printSchema()

    except Exception as e:
        logger.error("❌ Error verifying table %s: %s", table_path, e)
        raise
