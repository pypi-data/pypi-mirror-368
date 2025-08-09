"""Pydantic models for Victoria Emergency GeoJSON feed."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CAPInfo(BaseModel):
    """Common Alerting Protocol information."""

    category: str | None = None
    event: str | None = None
    eventCode: str | None = None
    urgency: str | None = None
    severity: str | None = None
    certainty: str | None = None
    contact: str | None = None
    senderName: str | None = None
    responseType: str | None = None


class FeatureProperties(BaseModel):
    """Properties of a GeoJSON feature."""

    feedType: str
    sourceOrg: str
    sourceId: str | int  # Can be string or int
    sourceFeed: str
    sourceTitle: str | None = None
    id: str | int  # Can be string or int
    category1: str | None = None
    category2: str | None = None
    status: str | None = None
    name: str | None = None
    created: datetime | None = None
    updated: datetime | None = None  # Some features may not have this
    location: str | None = None
    size: float | str | None = None  # Can be numeric or "Small", etc
    sizeFmt: str | list[str] | None = None
    url: str | None = None
    webHeadline: str | None = None
    webBody: str | None = None
    text: str | None = None
    resources: list[str] | int | None = None  # Can be list or count
    mfbId: str | int | None = None
    cfaId: str | int | None = None
    eventId: str | int | None = None
    action: str | None = None
    statewide: str | None = None
    cap: CAPInfo | None = None
    incidentFeatures: list[Any] | None = None  # Nested features

    model_config = {"extra": "allow"}  # Allow additional fields


class Geometry(BaseModel):
    """GeoJSON geometry."""

    type: str
    coordinates: list[float] | list[list[float]] | list[list[list[float]]] | None = None
    geometries: list[dict[str, Any]] | None = None  # For GeometryCollection

    class Config:
        extra = "allow"


class Feature(BaseModel):
    """GeoJSON feature."""

    type: str = Field(default="Feature")
    properties: FeatureProperties
    geometry: Geometry | None = None


class FeedProperties(BaseModel):
    """Top-level feed properties."""

    generated: datetime | None = None
    lastUpdated: datetime | None = None
    authority: str | None = None
    conditions: dict[str, Any] | None = None
    forecast: dict[str, Any] | None = None
    featureCount: int | None = None

    class Config:
        extra = "allow"


class GeoJSONFeed(BaseModel):
    """Complete GeoJSON feed."""

    type: str = Field(default="FeatureCollection")
    features: list[Feature]
    properties: FeedProperties | None = None
    notices: list[Any] | None = None
    lastUpdated: datetime | None = None
    featureCount: int | None = None
