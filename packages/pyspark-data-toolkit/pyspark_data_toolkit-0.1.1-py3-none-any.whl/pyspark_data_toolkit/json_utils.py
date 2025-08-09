from typing import List, Dict, Any, Optional
from pyspark.sql import DataFrame
import pyspark.sql.functions as F
import logging
from logging_metrics import configure_basic_logging

__all__ = [
    "diff_dataframes",
    "diff_schemas",
    "summarize_diff",
    "tag_row_changes"
]

def get_logger() -> logging.Logger:
    """Initializes and returns a basic logger for file output.

    Returns:
        logging.Logger: A configured logger with file rotation.
    """
    return configure_basic_logging()


def diff_dataframes(df1: DataFrame, df2: DataFrame, keys: List[str]) -> DataFrame:
    """
    Identifies inserted and deleted rows between two DataFrames based on primary keys.

    Args:
        df1 (DataFrame): Original DataFrame.
        df2 (DataFrame): New DataFrame to compare.
        keys (List[str]): List of key columns used to match rows.

    Returns:
        DataFrame: DataFrame containing rows marked with '_change' column as 'inserted' or 'deleted'.
    """
    removed = (
        df1.join(df2, keys, how="left_anti")
           .withColumn("_change", F.lit("deleted"))
    )
    inserted = (
        df2.join(df1, keys, how="left_anti")
           .withColumn("_change", F.lit("inserted"))
    )
    return removed.unionByName(inserted)


def diff_schemas(df1: DataFrame, df2: DataFrame) -> Dict[str, Any]:
    """
    Compares schemas of two DataFrames and returns differences.

    Args:
        df1 (DataFrame): First DataFrame.
        df2 (DataFrame): Second DataFrame.

    Returns:
        Dict[str, Any]: Dictionary containing:
            - only_in_df1: Columns only in df1.
            - only_in_df2: Columns only in df2.
            - type_mismatches: Columns in both but with different data types.
    """
    s1 = {f.name: f.dataType for f in df1.schema.fields}
    s2 = {f.name: f.dataType for f in df2.schema.fields}

    only1 = set(s1) - set(s2)
    only2 = set(s2) - set(s1)
    mismatches = {
        col: (s1[col], s2[col])
        for col in set(s1).intersection(s2)
        if s1[col] != s2[col]
    }

    return {
        "only_in_df1": list(only1),
        "only_in_df2": list(only2),
        "type_mismatches": mismatches
    }


def summarize_diff(df1: DataFrame, df2: DataFrame, keys: List[str], log: Optional[logging.Logger] = None) -> Dict[str, int]:
    """
    Counts inserted, deleted, and updated rows between two DataFrames.

    Args:
        df1 (DataFrame): Original DataFrame.
        df2 (DataFrame): New DataFrame to compare.
        keys (List[str]): List of key columns used to match rows.

    Returns:
        Dict[str, int]: Dictionary with counts of 'inserted', 'deleted', and 'updated' rows.
    """
    logger = log or get_logger()
    try:
        removed_df = df1.join(df2, keys, how="left_anti")
        inserted_df = df2.join(df1, keys, how="left_anti")

        # Rename non-key columns for comparison
        non_keys = [c for c in df1.columns if c not in keys]
        df1_ren = df1
        df2_ren = df2
        for col in non_keys:
            df1_ren = df1_ren.withColumnRenamed(col, f"{col}_1")
            df2_ren = df2_ren.withColumnRenamed(col, f"{col}_2")

        common = df1_ren.join(df2_ren, keys, how="inner")

        cond = None
        for col in non_keys:
            diff = F.col(f"{col}_1") != F.col(f"{col}_2")
            cond = diff if cond is None else cond | diff

        updated_df = common.filter(cond) if cond is not None else common.limit(0)

        return {
            "inserted": inserted_df.count(),
            "deleted": removed_df.count(),
            "updated": updated_df.count()
        }
    except Exception as e:
        logger.exception(f"Error summarizing diff between DataFrames: {e}")
        raise


def tag_row_changes(
    df1: DataFrame,
    df2: DataFrame,
    keys: List[str],
    hash_cols: Optional[List[str]] = None,
    tag_col: str = "change_type",
    log: Optional[logging.Logger] = None
) -> DataFrame:
    """
    Tags each row in df2 as 'inserted', 'deleted', 'updated', or 'unchanged'
    based on a full outer join with df1 using primary keys and hash comparison.

    Args:
        df1 (DataFrame): Original DataFrame.
        df2 (DataFrame): New DataFrame to compare.
        keys (List[str]): List of primary key columns.
        hash_cols (Optional[List[str]]): Columns to use for hash comparison. Defaults to all df2 columns.
        tag_col (str): Name of the output column indicating change type.

    Returns:
        DataFrame: df2 with an additional column indicating the type of change.
    """
    logger = log or get_logger()

    try:
        cols = hash_cols if hash_cols is not None else df2.columns

        # Generate temporary column names to avoid conflicts
        df1_tmp_cols = [f"tmp1_{i}" for i in range(len(df1.columns))]
        df2_tmp_cols = [f"tmp2_{i}" for i in range(len(df2.columns))]
        df1_temp = df1.toDF(*df1_tmp_cols)
        df2_temp = df2.toDF(*df2_tmp_cols)

        # Create column mappings from original to temporary names
        df1_colmap = dict(zip(df1.columns, df1_tmp_cols))
        df2_colmap = dict(zip(df2.columns, df2_tmp_cols))

        # Add hash columns for comparison
        df1_temp = df1_temp.withColumn(
            "__hash_1",
            F.sha2(F.concat_ws("||", *[F.col(df1_colmap[c]) for c in cols]), 256)
        )
        df2_temp = df2_temp.withColumn(
            "__hash_2",
            F.sha2(F.concat_ws("||", *[F.col(df2_colmap[c]) for c in cols]), 256)
        )

        # Join using primary key columns
        join_cond = [df1_temp[df1_colmap[k]] == df2_temp[df2_colmap[k]] for k in keys]
        joined = df1_temp.join(df2_temp, join_cond, how="full_outer")

        # Define row change conditions
        is_insert = F.col(df2_colmap[keys[0]]).isNotNull() & F.col(df1_colmap[keys[0]]).isNull()
        is_delete = F.col(df1_colmap[keys[0]]).isNotNull() & F.col(df2_colmap[keys[0]]).isNull()
        is_update = (
            (F.col("__hash_1") != F.col("__hash_2")) &
            F.col("__hash_1").isNotNull() & F.col("__hash_2").isNotNull()
        )
        is_unchanged = (
            (F.col("__hash_1") == F.col("__hash_2")) &
            F.col("__hash_1").isNotNull()
        )

        # Add change type column
        result = joined.withColumn(
            tag_col,
            F.when(is_insert, F.lit("inserted"))
             .when(is_delete, F.lit("deleted"))
             .when(is_update, F.lit("updated"))
             .when(is_unchanged, F.lit("unchanged"))
        )

        # Select original columns from df2 + change tag
        select_cols = [F.col(df2_colmap[c]).alias(c) for c in df2.columns] + [F.col(tag_col)]
        return result.select(*select_cols)

    except Exception as e:
        logger.exception(f"Failed to tag row changes: {e}")
        raise
