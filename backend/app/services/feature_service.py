from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.listing import FeatureDefinition, Listing, ListingFeature
from app.schemas.feature import FeatureDefinitionCreate, FeatureDefinitionRead
from app.schemas.listing import ListingRead, ListingSearchResult
from app.services.listing_service import _build_listing_select


async def list_feature_definitions(
    session: AsyncSession,
) -> list[FeatureDefinitionRead]:
    result = await session.execute(
        select(FeatureDefinition).order_by(FeatureDefinition.category, FeatureDefinition.key)
    )
    return [FeatureDefinitionRead.model_validate(r) for r in result.scalars().all()]


async def create_feature_definition(
    session: AsyncSession, data: FeatureDefinitionCreate
) -> FeatureDefinitionRead:
    obj = FeatureDefinition(**data.model_dump())
    session.add(obj)
    await session.flush()
    return FeatureDefinitionRead.model_validate(obj)


async def search_by_features(
    session: AsyncSession,
    features: list[str],
    exclude_features: list[str],
    page: int,
    page_size: int,
) -> ListingSearchResult:
    from app.services.listing_service import search_listings

    return await search_listings(
        session,
        features=features,
        exclude_features=exclude_features,
        page=page,
        page_size=page_size,
    )


async def assign_feature(
    session: AsyncSession,
    listing_id: int,
    feature_key: str,
    value: Optional[str] = None,
    confidence: Optional[float] = None,
) -> ListingFeature:
    obj = ListingFeature(
        listing_id=listing_id,
        feature_key=feature_key,
        value=value,
        confidence=confidence,
    )
    session.add(obj)
    await session.flush()
    return obj
