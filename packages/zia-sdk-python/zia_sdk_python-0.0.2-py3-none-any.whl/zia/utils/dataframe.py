"""
Utilities for converting Neurolabs SDK data models to pandas DataFrames.
"""

import pandas as pd
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models import NLIRResult, NLIRResults, NLIRCOCOResult


def ir_results_to_dataframe(
    results: List[NLIRResult],
    include_bbox: bool = True,
    include_alternative_predictions: bool = True,
) -> pd.DataFrame:
    """
    Convert a list of NLIRResult objects to a pandas DataFrame.

    This function matches categories with annotations using the category_id
    and creates a flat DataFrame with all attributes for each detected item.

    Args:
        results: List of NLIRResult objects
        include_bbox: Whether to include bounding box coordinates as separate columns
        include_alternative_predictions: Whether to include alternative predictions

    Returns:
        pandas DataFrame with one row per detected item

    Example:
        >>> results = await client.image_recognition.get_all_task_results(task_uuid)
        >>> df = ir_results_to_dataframe(results)
        >>> print(df.head())
    """
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


def ir_results_to_summary_dataframe(results: List[NLIRResult]) -> pd.DataFrame:
    """
    Create a summary DataFrame with aggregated statistics per result.

    Args:
        results: List of NLIRResult objects

    Returns:
        pandas DataFrame with one row per result and summary statistics
    """
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
