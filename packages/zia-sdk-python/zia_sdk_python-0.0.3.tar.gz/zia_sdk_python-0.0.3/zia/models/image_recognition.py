"""
Image recognition models for the Neurolabs SDK.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class NLIRResultStatus(str, Enum):
    """Status values for image recognition results."""

    IN_PROGRESS = "IN_PROGRESS"
    FAILED = "FAILED"
    PROCESSED = "PROCESSED"


class NLIRTaskStatus(str, Enum):
    """Status values for image recognition tasks."""

    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class NLIRTask(BaseModel):
    """Model representing an image recognition task."""

    uuid: str = Field(..., description="Unique identifier for the task")
    name: str = Field(..., description="Name of the task")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    compute_realogram: bool = Field(
        default=False, description="Whether to compute realogram"
    )
    compute_shares: bool = Field(default=False, description="Whether to compute shares")


class NLIRTaskCreate(BaseModel):
    """Model for creating a new image recognition task."""

    name: str = Field(..., description="Name of the task")
    catalog_items: list[str] = Field(
        default=[], description="List of catalog item UUIDs"
    )
    compute_realogram: bool = Field(
        default=False, description="Whether to compute realogram"
    )
    compute_shares: bool = Field(default=False, description="Whether to compute shares")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate task name."""
        if not v or not v.strip():
            raise ValueError("Task name cannot be empty")
        return v.strip()

    @field_validator("catalog_items")
    @classmethod
    def validate_catalog_items(cls, v: list[str]) -> list[str]:
        """Validate catalog items list."""
        if not v:
            raise ValueError("At least one catalog item must be specified")
        return v


class NLIRTaskCreateWithAllCatalogItems(NLIRTaskCreate):
    # TODO: Add all catalog items to the task by default
    # raise NotImplementedError("This is not implemented yet")
    pass


# COCO Format Models
class NLIRCOCOInfo(BaseModel):
    """Model representing COCO info section."""

    url: str = Field(default="", description="URL (usually empty)")
    year: str = Field(..., description="Year of the dataset")
    version: str = Field(..., description="Version of the dataset")
    contributor: str = Field(default="", description="Contributor information")
    description: str = Field(default="", description="Dataset description")
    date_created: str = Field(..., description="Date when the dataset was created")


class NLIRCOCOImage(BaseModel):
    """Model representing a COCO image entry."""

    id: int = Field(..., description="Unique image ID")
    width: Optional[int] = Field(None, description="Image width")
    height: Optional[int] = Field(None, description="Image height")
    license: int = Field(..., description="License ID")
    coco_url: str = Field(default="", description="COCO URL")
    file_name: str = Field(..., description="Image file name/URL")
    flickr_url: str = Field(default="", description="Flickr URL")
    date_captured: str = Field(default="", description="Date when image was captured")


class NLIRCOCONeurolabsCategory(BaseModel):
    """Model representing Neurolabs-specific category information."""

    barcode: Optional[str] = Field(None, description="Product barcode")
    customId: Optional[str] = Field(..., description="Custom product ID")
    label: Optional[str] = Field(..., description="Product label")
    productUuid: str = Field(..., description="Product UUID")
    brand: Optional[str] = Field(..., description="Product brand")
    name: str = Field(..., description="Product name")


class NLIRCOCOCategory(BaseModel):
    """Model representing a COCO category entry."""

    id: int = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    neurolabs: Optional[NLIRCOCONeurolabsCategory] = Field(
        None, description="Neurolabs-specific category data"
    )
    supercategory: Optional[str] = Field(default="", description="Super category name")


class NLIRCOCOAlternativePrediction(BaseModel):
    """Model representing an alternative prediction in COCO annotations."""

    category_id: int = Field(..., description="Alternative category ID")
    score: float = Field(..., description="Alternative prediction score")


class NLIRCOCONeurolabsAnnotation(BaseModel):
    """Model representing Neurolabs-specific annotation information."""

    modalities: dict[str, Any] = Field(
        default_factory=dict, description="Modality information"
    )
    score: float = Field(..., description="Recognition score")
    alternative_predictions: list[NLIRCOCOAlternativePrediction] = Field(
        default_factory=list, description="Alternative predictions"
    )


class NLIRCOCOAnnotation(BaseModel):
    """Model representing a COCO annotation entry."""

    id: int = Field(..., description="Annotation ID")
    area: float = Field(..., description="Area of the detection")
    bbox: list[float] = Field(
        ..., description="Bounding box coordinates [x, y, width, height]"
    )
    iscrowd: int = Field(..., description="Whether the annotation is a crowd")
    image_id: int = Field(..., description="Image ID this annotation belongs to")
    neurolabs: NLIRCOCONeurolabsAnnotation = Field(
        ..., description="Neurolabs-specific annotation data"
    )
    category_id: int = Field(
        ..., description="Category ID of the recognised catalog item"
    )
    segmentation: Optional[list[list[float]]] = Field(
        default_factory=list, description="Segmentation polygon"
    )


class NLIRCOCOLicense(BaseModel):
    """Model representing a COCO license entry."""

    id: int = Field(..., description="License ID")
    url: str = Field(default="", description="License URL")
    name: str = Field(default="", description="License name")


class NLIRCOCOResult(BaseModel):
    """Model representing the complete COCO format detection results."""

    info: NLIRCOCOInfo = Field(..., description="COCO dataset info")
    images: list[NLIRCOCOImage] = Field(..., description="List of images")
    licenses: list[NLIRCOCOLicense] = Field(..., description="List of licenses")
    neurolabs: dict[str, Any] = Field(
        default_factory=dict, description="Neurolabs-specific data"
    )
    categories: list[NLIRCOCOCategory] = Field(..., description="List of categories")
    annotations: list[NLIRCOCOAnnotation] = Field(
        ..., description="List of annotations"
    )


class NLIRResult(BaseModel):
    """Model representing an image recognition result."""

    uuid: str = Field(..., description="Unique identifier for the IR result")
    task_uuid: str = Field(..., description="UUID of the parent task")
    image_url: str = Field(..., description="URL of the processed image")
    status: NLIRResultStatus = Field(..., description="Current status of the result")
    failure_reason: Optional[str] = Field(
        default="", description="Failure reason if status is FAILED"
    )
    duration: Optional[float] = Field(
        None, description="Processing duration in seconds"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    postprocessing_results: Optional[dict[str, Any]] = Field(
        None, description="Postprocessing results"
    )
    coco: Optional[NLIRCOCOResult] = Field(
        None, description="COCO format detection results"
    )
    confidence_score: Optional[float] = Field(
        None, description="Overall confidence score"
    )


class NLIRResults(BaseModel):
    """Model for representing all IR Results from a task"""

    task_uuid: str = Field(..., description="UUID of the parent task")
    results: list[NLIRResult] = Field(
        default_factory=list, description="All IR Results attached to a task"
    )
    total: int = Field(..., description="Total number of IR Results")
    limit: int = Field(..., description="Limit of IR Results")
    offset: int = Field(..., description="Offset of IR Results")
