from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RawListing:
    url: Optional[str]
    raw_data: dict
    source_name: str
    source_type: str


@dataclass
class ParsedListing:
    title: Optional[str] = None
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
    source_url: Optional[str] = None
    extraction_confidence: Optional[float] = None
    extra: dict = field(default_factory=dict)


class SourceConnector(ABC):
    source_name: str
    source_type: str
    allowed: bool = True

    @abstractmethod
    async def fetch_listing_urls(self, criteria: dict) -> list[str]:
        """Return a list of listing URLs matching the given search criteria."""
        ...

    @abstractmethod
    async def fetch_listing_detail(self, url: str) -> RawListing:
        """Fetch the raw data for a single listing URL."""
        ...

    @abstractmethod
    async def parse_listing(self, raw: RawListing) -> ParsedListing:
        """Parse a RawListing into a structured ParsedListing."""
        ...
