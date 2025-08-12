#!/usr/bin/env python3
"""
Tests for DataFrame workflows and Spark integration.
"""

from unittest.mock import AsyncMock, Mock

import pandas as pd
import pytest

from zia.utils.dataframe import (
    get_spark_schema_from_dataframe,
    ir_results_to_dataframe,
    to_spark_dataframe,
)
from zia.models.image_recognition import NLIRResult 
from typing import List


class TestDataframe:
    """Test DataFrame conversion and analysis workflows."""

    def test_ir_results_to_dataframe_basic(self, sample_ir_results_list_data):
        """Test basic DataFrame conversion."""
        
        results = [NLIRResult.model_validate(result) for result in sample_ir_results_list_data["items"]]
        df = ir_results_to_dataframe(results)

        # Check DataFrame structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert not df.empty

        # Check required columns
        required_columns = [
            "result_uuid", "task_uuid", "image_url", "result_status",
            "annotation_id", "category_id", "detection_score",
            "category_name", "product_name", "product_brand"
        ]

        for col in required_columns:
            assert col in df.columns, f"Missing column: {col}"

    def test_get_spark_schema_from_dataframe(self, sample_ir_results_list_data):
        """Test Spark schema generation from DataFrame."""

        results = [NLIRResult.model_validate(result) for result in sample_ir_results_list_data["items"]]
        df = ir_results_to_dataframe(results)

        df = ir_results_to_dataframe(results)
        schema = get_spark_schema_from_dataframe(df)

        # Check schema structure
        assert schema is not None
        assert hasattr(schema, "fields")

        # Check schema fields
        field_names = [field.name for field in schema.fields]
        expected_fields = ["result_uuid", "task_uuid", "detection_score", "category_name"]

        for field in expected_fields:
            assert field in field_names, f"Missing schema field: {field}"

    def test_to_spark_dataframe(self, sample_ir_results_list_data):
        """Test conversion to Spark DataFrame."""
        # TODO: Add correct spark test

        results = [NLIRResult.model_validate(result) for result in sample_ir_results_list_data["items"]]

        # Create pandas DataFrame first to get the expected row count
        pdf = ir_results_to_dataframe(results)
        expected_row_count = len(pdf)

        # Mock Spark session with proper count method
        mock_spark = Mock()
        mock_spark_df = Mock()
        mock_spark_df.count.return_value = expected_row_count
        mock_spark.createDataFrame.return_value = mock_spark_df
        mock_spark.sparkContext.emptyRDD.return_value = Mock()

        spark_df = to_spark_dataframe(results, mock_spark)

        # Check that createDataFrame was called
        mock_spark.createDataFrame.assert_called_once()

        assert spark_df.count() == expected_row_count

