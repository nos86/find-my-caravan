from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FeatureDefinitionCreate(BaseModel):
    key: str
    label: str
    description: Optional[str] = None
    category: Optional[str] = None


class FeatureDefinitionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str
    label: str
    description: Optional[str] = None
    category: Optional[str] = None
    created_at: datetime


class FeatureSearchRequest(BaseModel):
    features: list[str]
    exclude_features: list[str] = []
    page: int = 1
    page_size: int = 20
