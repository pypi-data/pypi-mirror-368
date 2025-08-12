"""
DataFrame utilities for converting Neurolabs SDK data models to pandas DataFrames and Spark DataFrames.

This module provides functions to convert NLIRResult objects to pandas DataFrames
for data analysis and processing. It matches categories with annotations using
the category_id and creates flat DataFrames with all attributes for each detected item.

Usage:
    from zia.utils import ir_results_to_dataframe, ir_results_to_summary_dataframe

    # Convert results to DataFrame
    df = ir_results_to_dataframe(results)

    # Create summary DataFrame
    df_summary = ir_results_to_summary_dataframe(results)
"""

from typing import TYPE_CHECKING, Any

import pandas as pd

if TYPE_CHECKING:
    try:
        from pyspark.sql.types import StructType
    except ImportError:
        StructType = None


def get_dynamic_spark_schema(df: pd.DataFrame) -> 'StructType | None':
    """
    Dynamically generate a Spark schema based on the actual DataFrame structure.

    This function analyzes the pandas DataFrame and creates a matching Spark schema,
    ensuring no mismatches between the DataFrame columns and schema fields.

    Args:
        df: pandas DataFrame created by ir_results_to_dataframe()

    Returns:
        pyspark.sql.types.StructType schema that matches the DataFrame exactly

    Raises:
        ImportError: If pyspark is not installed
    """
    try:
        from pyspark.sql.types import (
            ArrayType,
            BooleanType,
            DoubleType,
            FloatType,
            IntegerType,
            StringType,
            StructField,
            StructType,
            TimestampType,
        )
        from pyspark.sql.types import StructType as SparkStructType
    except ImportError:
        raise ImportError(
            "pyspark is required for Spark schema generation. "
            "Install it with: pip install pyspark"
        )

    fields = []

    for column_name, dtype in df.dtypes.items():
        # Handle different pandas dtypes
        if dtype == 'object':
            # Check if it's a datetime column
            if column_name in ['result_created_at', 'result_updated_at']:
                spark_type = TimestampType()
            # Check if it's the alternative_predictions column (list of dicts)
            elif column_name == 'alternative_predictions':
                # Define schema for alternative prediction items
                alt_pred_schema = SparkStructType([
                    StructField("category_id", IntegerType(), True),
                    StructField("category_name", StringType(), True),
                    StructField("score", FloatType(), True),
                ])
                spark_type = ArrayType(alt_pred_schema)
            else:
                spark_type = StringType()
        elif dtype == 'int64':
            spark_type = IntegerType()
        elif dtype == 'float64':
            spark_type = FloatType()
        elif dtype == 'bool':
            spark_type = BooleanType()
        elif dtype == 'datetime64[ns]':
            spark_type = TimestampType()
        else:
            # Default to string for unknown types
            spark_type = StringType()

        fields.append(StructField(column_name, spark_type, True))

    return StructType(fields)


def get_spark_schema_from_dataframe(df: pd.DataFrame) -> 'StructType | None':
    """
    Generate Spark schema directly from the DataFrame structure.

    This is the recommended approach to ensure perfect schema matching.

    Args:
        df: pandas DataFrame created by ir_results_to_dataframe()

    Returns:
        pyspark.sql.types.StructType schema that matches the DataFrame exactly

    Raises:
        ImportError: If pyspark is not installed
    """
    return get_dynamic_spark_schema(df)


def ir_results_to_dataframe(
    results: list[Any],
    include_bbox: bool = True,
    include_alternative_predictions: bool = True,
) -> pd.DataFrame:
    """
    Convert a list of NLIRResult objects to a pandas DataFrame.

    This function matches categories with annotations using the category_id
    and creates a flat DataFrame with all attributes for each detected item.

    Args:
        results: List of NLIRResult objects (from zia.models)
        include_bbox: Whether to include bounding box coordinates as separate columns
        include_alternative_predictions: Whether to include alternative predictions

    Returns:
        pandas DataFrame with one row per detected item

    Example:
        >>> from zia.utils import ir_results_to_dataframe
        >>> results = await client.image_recognition.get_all_task_results(task_uuid)
        >>> df = ir_results_to_dataframe(results)
        >>> print(df.head())

    Raises:
        ImportError: If pandas is not installed
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for DataFrame operations. "
            "Install it with: pip install pandas"
        )

    rows = []

    for result in results:
        if not result.coco or result.status.value != "PROCESSED":
            continue

        # Create a mapping of category_id to category for quick lookup
        category_map = {cat.id: cat for cat in result.coco.categories}

        for annotation in result.coco.annotations:
            # Get the corresponding category
            category = category_map.get(annotation.category_id)
            if not category:
                continue

            # Base row with result-level information
            row = {
                # Result-level information
                "result_uuid": result.uuid,
                "task_uuid": result.task_uuid,
                "image_url": result.image_url,
                "result_status": result.status.value,
                "result_duration": result.duration,
                "result_created_at": result.created_at,
                "result_updated_at": result.updated_at,
                "confidence_score": result.confidence_score,
                # Image information
                "image_id": annotation.image_id,
                "image_width": next(
                    (
                        img.width
                        for img in result.coco.images
                        if img.id == annotation.image_id
                    ),
                    None,
                ),
                "image_height": next(
                    (
                        img.height
                        for img in result.coco.images
                        if img.id == annotation.image_id
                    ),
                    None,
                ),
                "image_filename": next(
                    (
                        img.file_name
                        for img in result.coco.images
                        if img.id == annotation.image_id
                    ),
                    None,
                ),
                # Annotation information
                "annotation_id": annotation.id,
                "category_id": annotation.category_id,
                "area": annotation.area,
                "iscrowd": annotation.iscrowd,
                "detection_score": annotation.neurolabs.score,
                # Category information
                "category_name": category.name,
                "category_supercategory": category.supercategory,
            }

            # Add bounding box coordinates if requested
            if include_bbox and annotation.bbox:
                row.update(
                    {
                        "bbox_x": annotation.bbox[0],
                        "bbox_y": annotation.bbox[1],
                        "bbox_width": annotation.bbox[2],
                        "bbox_height": annotation.bbox[3],
                    }
                )

            # Add Neurolabs category information
            if category.neurolabs:
                row.update(
                    {
                        "product_uuid": category.neurolabs.productUuid,
                        "product_name": category.neurolabs.name,
                        "product_brand": category.neurolabs.brand,
                        "product_barcode": category.neurolabs.barcode,
                        "product_custom_id": category.neurolabs.customId,
                        "product_label": category.neurolabs.label,
                    }
                )

            # Add alternative predictions if requested
            if (
                include_alternative_predictions
                and annotation.neurolabs.alternative_predictions
            ):
                alt_predictions = []
                for alt_pred in annotation.neurolabs.alternative_predictions:
                    alt_category = category_map.get(alt_pred.category_id)
                    alt_predictions.append(
                        {
                            "category_id": alt_pred.category_id,
                            "category_name": alt_category.name
                            if alt_category
                            else f"Unknown_{alt_pred.category_id}",
                            "score": alt_pred.score,
                        }
                    )
                row["alternative_predictions"] = alt_predictions

            # Add modalities if present
            if annotation.neurolabs.modalities:
                for (
                    modality_name,
                    modality_value,
                ) in annotation.neurolabs.modalities.items():
                    row[f"modality_{modality_name}"] = modality_value

            rows.append(row)

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    # Convert datetime columns
    datetime_columns = ["result_created_at", "result_updated_at"]
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])

    return df


def ir_results_to_summary_dataframe(results: list[Any]) -> pd.DataFrame:
    """
    Create a summary DataFrame with aggregated statistics per result.

    Args:
        results: List of NLIRResult objects (from zia.models)

    Returns:
        pandas DataFrame with one row per result and summary statistics

    Raises:
        ImportError: If pandas is not installed
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for DataFrame operations. "
            "Install it with: pip install pandas"
        )

    summary_rows = []

    for result in results:
        row = {
            "result_uuid": result.uuid,
            "task_uuid": result.task_uuid,
            "image_url": result.image_url,
            "status": result.status.value,
            "duration": result.duration,
            "created_at": result.created_at,
            "updated_at": result.updated_at,
            "confidence_score": result.confidence_score,
            "total_detections": 0,
            "unique_products": 0,
            "avg_detection_score": 0.0,
            "max_detection_score": 0.0,
            "min_detection_score": 0.0,
        }

        if result.coco and result.status.value == "PROCESSED":
            annotations = result.coco.annotations
            if annotations:
                scores = [ann.neurolabs.score for ann in annotations]
                unique_products = len(set(ann.category_id for ann in annotations))

                row.update(
                    {
                        "total_detections": len(annotations),
                        "unique_products": unique_products,
                        "avg_detection_score": sum(scores) / len(scores),
                        "max_detection_score": max(scores),
                        "min_detection_score": min(scores),
                    }
                )

        summary_rows.append(row)

    if not summary_rows:
        return pd.DataFrame()

    df = pd.DataFrame(summary_rows)

    # Convert datetime columns
    datetime_columns = ["created_at", "updated_at"]
    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])

    return df


def analyze_results_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    """
    Analyze a DataFrame created from NLIRResults and return summary statistics.

    Args:
        df: DataFrame created by ir_results_to_dataframe()

    Returns:
        Dictionary with analysis results

    Raises:
        ImportError: If pandas is not installed
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for DataFrame operations. "
            "Install it with: pip install pandas"
        )

    if df.empty:
        return {"error": "DataFrame is empty"}

    analysis = {
        "total_detections": len(df),
        "unique_products": df["product_name"].nunique() if "product_name" in df.columns else 0,
        "unique_images": df["result_uuid"].nunique(),
        "score_stats": {
            "mean": df["detection_score"].mean(),
            "std": df["detection_score"].std(),
            "min": df["detection_score"].min(),
            "max": df["detection_score"].max(),
            "median": df["detection_score"].median(),
        }
    }

    # Product analysis
    if "product_name" in df.columns:
        product_counts = df["product_name"].value_counts()
        analysis["top_products"] = product_counts.head(10).to_dict()
        analysis["product_detection_counts"] = {
            "single_detection": (product_counts == 1).sum(),
            "multiple_detections": (product_counts > 1).sum(),
        }

    # Score distribution
    score_ranges = {
        "high_confidence": len(df[df["detection_score"] >= 0.9]),
        "medium_confidence": len(df[(df["detection_score"] >= 0.7) & (df["detection_score"] < 0.9)]),
        "low_confidence": len(df[df["detection_score"] < 0.7]),
    }
    analysis["score_distribution"] = score_ranges

    # Bounding box analysis (if available)
    if "bbox_width" in df.columns and "bbox_height" in df.columns:
        analysis["bbox_stats"] = {
            "avg_width": df["bbox_width"].mean(),
            "avg_height": df["bbox_height"].mean(),
            "avg_area": df["area"].mean(),
        }

    return analysis


def filter_high_confidence_detections(df: pd.DataFrame, threshold: float = 0.9) -> pd.DataFrame:
    """
    Filter DataFrame to include only high-confidence detections.

    Args:
        df: DataFrame created by ir_results_to_dataframe()
        threshold: Minimum confidence score (default: 0.9)

    Returns:
        Filtered DataFrame

    Raises:
        ImportError: If pandas is not installed
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for DataFrame operations. "
            "Install it with: pip install pandas"
        )

    return df[df["detection_score"] >= threshold]


def get_product_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a product summary from the detailed DataFrame.

    Args:
        df: DataFrame created by ir_results_to_dataframe()

    Returns:
        DataFrame with one row per product and aggregated statistics

    Raises:
        ImportError: If pandas is not installed
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for DataFrame operations. "
            "Install it with: pip install pandas"
        )

    if df.empty:
        return pd.DataFrame()

    product_summary = df.groupby([
        "product_uuid", "product_name", "product_brand", "product_barcode", "product_custom_id"
    ]).agg({
        "result_uuid": "count",  # Number of detections
        "detection_score": ["mean", "max", "min", "std"],
        "task_uuid": "nunique",  # Number of tasks this product appears in
        "result_uuid": "nunique",  # Number of images this product appears in
    }).reset_index()

    # Flatten column names
    product_summary.columns = [
        "product_uuid", "product_name", "product_brand", "product_barcode", "product_custom_id",
        "total_detections", "avg_score", "max_score", "min_score", "score_std",
        "num_tasks", "num_images"
    ]

    return product_summary


def to_spark_dataframe(
    results: list[Any],
    spark_session,
    include_bbox: bool = True,
    include_alternative_predictions: bool = True,
):
    """
    Convert NLIRResult objects to a Spark DataFrame.

    Args:
        results: List of NLIRResult objects
        spark_session: Active Spark session
        include_bbox: Whether to include bounding box fields
        include_alternative_predictions: Whether to include alternative predictions

    Returns:
        Spark DataFrame

    Raises:
        ImportError: If pyspark is not installed
    """
    try:
        from pyspark.sql import SparkSession
    except ImportError:
        raise ImportError(
            "pyspark is required for Spark DataFrame operations. "
            "Install it with: pip install pyspark"
        )

    # Convert to pandas DataFrame first
    pdf = ir_results_to_dataframe(
        results,
        include_bbox=include_bbox,
        include_alternative_predictions=include_alternative_predictions
    )

    if pdf.empty:
        return spark_session.createDataFrame([], spark_session.sparkContext.emptyRDD())

    # Generate schema from the pandas DataFrame
    schema = get_spark_schema_from_dataframe(pdf)

    # Convert to Spark DataFrame
    return spark_session.createDataFrame(pdf, schema=schema)
