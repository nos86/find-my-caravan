from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


# ---------------------------------------------------------------------------
# Source schemas
# ---------------------------------------------------------------------------


class SourceBase(BaseModel):
    name: str
    source_type: str
    base_url: Optional[str] = None
    allowed: bool = True
    terms_notes: Optional[str] = None
    rate_limit_seconds: int = 5
    enabled: bool = True


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    source_type: Optional[str] = None
    base_url: Optional[str] = None
    allowed: Optional[bool] = None
    terms_notes: Optional[str] = None
    rate_limit_seconds: Optional[int] = None
    enabled: Optional[bool] = None


class SourceRead(SourceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    robots_checked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Feature schemas (referenced by ListingRead)
# ---------------------------------------------------------------------------


class FeatureRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    listing_id: int
    feature_key: str
    value: Optional[str] = None
    confidence: Optional[float] = None


# ---------------------------------------------------------------------------
# Listing schemas
# ---------------------------------------------------------------------------


class ListingCreate(BaseModel):
    """Used for both manual creation and import pipelines."""

    source_id: int
    source_name: Optional[str] = None
    source_type: Optional[str] = None
    source_url: Optional[str] = None

    title: str
    brand: Optional[str] = None
    model: Optional[str] = None
    version: Optional[str] = None
    year: Optional[int] = None
    price: Optional[float] = None
    mileage_km: Optional[int] = None
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    engine_power_kw: Optional[float] = None
    engine_displacement_cc: Optional[int] = None
    emission_class: Optional[str] = None
    length_mm: Optional[int] = None
    width_mm: Optional[int] = None
    height_mm: Optional[int] = None
    mass_kg: Optional[int] = None
    driving_license_category: Optional[str] = None
    seats_travel: Optional[int] = None
    seats_sleeping: Optional[int] = None
    layout_type: Optional[str] = None
    bed_types: Optional[list[str]] = None
    has_rear_garage: Optional[bool] = None
    garage_size_category: Optional[str] = None
    has_bunk_beds: Optional[bool] = None
    has_double_floor: Optional[bool] = None
    bathroom_type: Optional[str] = None
    heating_type: Optional[str] = None
    air_conditioning: Optional[bool] = None
    solar_panel: Optional[bool] = None
    tow_bar: Optional[bool] = None
    seller_name: Optional[str] = None
    seller_type: Optional[str] = None
    address_raw: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description_raw: Optional[str] = None
    images: Optional[list[str]] = None
    status: str = "active"
    extraction_confidence: Optional[float] = None
    enrichment_confidence: Optional[float] = None
    raw_data: Optional[dict] = None

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not (1990 <= v <= 2030):
            raise ValueError("year must be between 1990 and 2030")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("price must be non-negative")
        return v

    @field_validator("mileage_km")
    @classmethod
    def validate_mileage(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("mileage_km must be non-negative")
        return v


class ListingUpdate(BaseModel):
    title: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    price: Optional[float] = None
    mileage_km: Optional[int] = None
    status: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description_raw: Optional[str] = None
    seller_name: Optional[str] = None
    seller_type: Optional[str] = None
    enrichment_confidence: Optional[float] = None


class ListingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_id: int
    source_name: Optional[str] = None
    source_type: Optional[str] = None
    source_url: Optional[str] = None
    title: str
    brand: Optional[str] = None
    model: Optional[str] = None
    version: Optional[str] = None
    year: Optional[int] = None
    price: Optional[float] = None
    mileage_km: Optional[int] = None
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    engine_power_kw: Optional[float] = None
    engine_displacement_cc: Optional[int] = None
    emission_class: Optional[str] = None
    length_mm: Optional[int] = None
    width_mm: Optional[int] = None
    height_mm: Optional[int] = None
    mass_kg: Optional[int] = None
    driving_license_category: Optional[str] = None
    seats_travel: Optional[int] = None
    seats_sleeping: Optional[int] = None
    layout_type: Optional[str] = None
    bed_types: Optional[list[str]] = None
    has_rear_garage: Optional[bool] = None
    garage_size_category: Optional[str] = None
    has_bunk_beds: Optional[bool] = None
    has_double_floor: Optional[bool] = None
    bathroom_type: Optional[str] = None
    heating_type: Optional[str] = None
    air_conditioning: Optional[bool] = None
    solar_panel: Optional[bool] = None
    tow_bar: Optional[bool] = None
    seller_name: Optional[str] = None
    seller_type: Optional[str] = None
    address_raw: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description_raw: Optional[str] = None
    images: Optional[list[str]] = None
    first_seen_at: datetime
    last_seen_at: datetime
    status: str
    extraction_confidence: Optional[float] = None
    enrichment_confidence: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    features: list[FeatureRead] = []


class ListingSearchResult(BaseModel):
    items: list[ListingRead]
    total: int
    page: int
    page_size: int
    pages: int


class ManualUrlCreate(BaseModel):
    url: str
    source_id: Optional[int] = None
    notes: Optional[str] = None


class MapListing(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    price: Optional[float] = None
    year: Optional[int] = None
    latitude: float
    longitude: float
    seller_type: Optional[str] = None
    source_name: Optional[str] = None
