from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class PriceYearPoint(BaseModel):
    id: int
    year: Optional[int]
    price: Optional[float]
    brand: Optional[str]
    title: str
    city: Optional[str]


class PriceDistributionBucket(BaseModel):
    bucket_min: float
    bucket_max: float
    count: int


class PriceByBrandEntry(BaseModel):
    brand: str
    avg_price: float
    median_price: Optional[float]
    count: int


class PriceByRegionEntry(BaseModel):
    region: str
    avg_price: float
    count: int
