from __future__ import annotations

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.listing import Listing
from app.schemas.analytics import (
    PriceByBrandEntry,
    PriceByRegionEntry,
    PriceDistributionBucket,
    PriceYearPoint,
)


async def price_year_scatter(session: AsyncSession) -> list[PriceYearPoint]:
    stmt = (
        select(
            Listing.id,
            Listing.year,
            Listing.price,
            Listing.brand,
            Listing.title,
            Listing.city,
        )
        .where(
            Listing.status == "active",
            Listing.price.isnot(None),
            Listing.year.isnot(None),
        )
        .order_by(Listing.year)
    )
    rows = (await session.execute(stmt)).all()
    return [
        PriceYearPoint(
            id=r.id,
            year=r.year,
            price=r.price,
            brand=r.brand,
            title=r.title,
            city=r.city,
        )
        for r in rows
    ]


async def price_distribution(
    session: AsyncSession, bucket_size: float = 5000.0
) -> list[PriceDistributionBucket]:
    stmt = select(Listing.price).where(
        Listing.status == "active",
        Listing.price.isnot(None),
        Listing.price > 0,
    )
    prices = [r[0] for r in (await session.execute(stmt)).all()]
    if not prices:
        return []

    min_p = min(prices)
    max_p = max(prices)
    import math

    num_buckets = max(1, math.ceil((max_p - min_p) / bucket_size))
    buckets: list[PriceDistributionBucket] = []
    for i in range(num_buckets):
        lo = min_p + i * bucket_size
        hi = lo + bucket_size
        count = sum(1 for p in prices if lo <= p < hi)
        if i == num_buckets - 1:
            count = sum(1 for p in prices if p >= lo)
        buckets.append(
            PriceDistributionBucket(bucket_min=lo, bucket_max=hi, count=count)
        )
    return buckets


async def price_by_brand(session: AsyncSession) -> list[PriceByBrandEntry]:
    stmt = (
        select(
            Listing.brand,
            func.avg(Listing.price).label("avg_price"),
            func.count(Listing.id).label("count"),
        )
        .where(
            Listing.status == "active",
            Listing.price.isnot(None),
            Listing.brand.isnot(None),
        )
        .group_by(Listing.brand)
        .order_by(func.count(Listing.id).desc())
    )
    rows = (await session.execute(stmt)).all()
    return [
        PriceByBrandEntry(
            brand=r.brand,
            avg_price=round(r.avg_price, 2),
            median_price=None,  # median requires window function or post-processing
            count=r.count,
        )
        for r in rows
    ]


async def price_by_region(session: AsyncSession) -> list[PriceByRegionEntry]:
    stmt = (
        select(
            Listing.region,
            func.avg(Listing.price).label("avg_price"),
            func.count(Listing.id).label("count"),
        )
        .where(
            Listing.status == "active",
            Listing.price.isnot(None),
            Listing.region.isnot(None),
        )
        .group_by(Listing.region)
        .order_by(func.avg(Listing.price).desc())
    )
    rows = (await session.execute(stmt)).all()
    return [
        PriceByRegionEntry(
            region=r.region,
            avg_price=round(r.avg_price, 2),
            count=r.count,
        )
        for r in rows
    ]
