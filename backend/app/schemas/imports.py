from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ImportPreviewResult(BaseModel):
    columns_detected: list[str]
    column_mapping: dict[str, str]  # detected → schema field
    preview_rows: list[dict]  # first 10 rows as dicts
    total_rows: int
    validation_warnings: list[str]


class ImportResult(BaseModel):
    ingestion_run_id: int
    total_found: int
    total_imported: int
    total_skipped: int
    total_errors: int
    errors: list[str]  # first 20 error messages


class ManualListingCreate(BaseModel):
    """Thin wrapper used by the manual listing endpoint."""

    source_id: Optional[int] = None  # if None a default "manual" source is used
    title: str
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    price: Optional[float] = None
    mileage_km: Optional[int] = None
    fuel_type: Optional[str] = None
    seller_name: Optional[str] = None
    seller_type: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    region: Optional[str] = None
    source_url: Optional[str] = None
    description_raw: Optional[str] = None
