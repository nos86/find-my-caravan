from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.analytics import (
    PriceByBrandEntry,
    PriceByRegionEntry,
    PriceDistributionBucket,
    PriceYearPoint,
)
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/price-year", response_model=list[PriceYearPoint])
async def price_year(
    session: AsyncSession = Depends(get_session),
) -> list[PriceYearPoint]:
    return await analytics_service.price_year_scatter(session)


@router.get("/price-distribution", response_model=list[PriceDistributionBucket])
async def price_distribution(
    session: AsyncSession = Depends(get_session),
) -> list[PriceDistributionBucket]:
    return await analytics_service.price_distribution(session)


@router.get("/price-by-brand", response_model=list[PriceByBrandEntry])
async def price_by_brand(
    session: AsyncSession = Depends(get_session),
) -> list[PriceByBrandEntry]:
    return await analytics_service.price_by_brand(session)


@router.get("/price-by-region", response_model=list[PriceByRegionEntry])
async def price_by_region(
    session: AsyncSession = Depends(get_session),
) -> list[PriceByRegionEntry]:
    return await analytics_service.price_by_region(session)
