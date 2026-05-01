from __future__ import annotations

import math
from typing import Optional

from sqlalchemy import Select, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.listing import Listing, ListingFeature, Source
from app.schemas.listing import (
    ListingCreate,
    ListingRead,
    ListingSearchResult,
    ListingUpdate,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _apply_text_search(stmt: Select, q: str) -> Select:
    pattern = f"%{q}%"
    return stmt.where(
        or_(
            Listing.title.ilike(pattern),
            Listing.brand.ilike(pattern),
            Listing.model.ilike(pattern),
            Listing.description_raw.ilike(pattern),
        )
    )


def _build_listing_select() -> Select:
    return select(Listing).options(selectinload(Listing.features))


# ---------------------------------------------------------------------------
# CRUD helpers
# ---------------------------------------------------------------------------


async def get_listing(session: AsyncSession, listing_id: int) -> Optional[Listing]:
    stmt = _build_listing_select().where(Listing.id == listing_id)
    result = await session.execute(stmt)
    return result.scalars().first()


async def create_listing(
    session: AsyncSession, data: ListingCreate
) -> Listing:
    obj = Listing(**data.model_dump())
    session.add(obj)
    await session.flush()
    # Reload with features eager-loaded
    return await get_listing(session, obj.id)  # type: ignore[return-value]


async def update_listing(
    session: AsyncSession, listing_id: int, data: ListingUpdate
) -> Optional[Listing]:
    obj = await get_listing(session, listing_id)
    if obj is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await session.flush()
    return obj


async def delete_listing(session: AsyncSession, listing_id: int) -> bool:
    obj = await session.get(Listing, listing_id)
    if obj is None:
        return False
    await session.delete(obj)
    return True


async def mark_sold(session: AsyncSession, listing_id: int) -> Optional[Listing]:
    obj = await get_listing(session, listing_id)
    if obj is None:
        return None
    obj.status = "sold"
    await session.flush()
    return obj


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


async def search_listings(
    session: AsyncSession,
    *,
    q: Optional[str] = None,
    source_type: Optional[str] = None,
    region: Optional[str] = None,
    province: Optional[str] = None,
    city: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    mileage_min: Optional[int] = None,
    mileage_max: Optional[int] = None,
    brand: Optional[str] = None,
    model: Optional[str] = None,
    vehicle_type: Optional[str] = None,
    seller_type: Optional[str] = None,
    features: Optional[list[str]] = None,
    exclude_features: Optional[list[str]] = None,
    length_max_mm: Optional[int] = None,
    sleeping_min: Optional[int] = None,
    travel_seats_min: Optional[int] = None,
    has_rear_garage: Optional[bool] = None,
    garage_size: Optional[str] = None,
    license_category: Optional[str] = None,
    only_with_coords: bool = False,
    only_active: bool = True,
    min_extraction_confidence: Optional[float] = None,
    min_enrichment_confidence: Optional[float] = None,
    sort_by: str = "last_seen",
    page: int = 1,
    page_size: int = 20,
) -> ListingSearchResult:
    stmt = _build_listing_select()

    # ---- filters ----
    if only_active:
        stmt = stmt.where(Listing.status == "active")
    if q:
        stmt = _apply_text_search(stmt, q)
    if source_type:
        stmt = stmt.where(Listing.source_type == source_type)
    if region:
        stmt = stmt.where(Listing.region.ilike(f"%{region}%"))
    if province:
        stmt = stmt.where(Listing.province.ilike(f"%{province}%"))
    if city:
        stmt = stmt.where(Listing.city.ilike(f"%{city}%"))
    if price_min is not None:
        stmt = stmt.where(Listing.price >= price_min)
    if price_max is not None:
        stmt = stmt.where(Listing.price <= price_max)
    if year_min is not None:
        stmt = stmt.where(Listing.year >= year_min)
    if year_max is not None:
        stmt = stmt.where(Listing.year <= year_max)
    if mileage_min is not None:
        stmt = stmt.where(Listing.mileage_km >= mileage_min)
    if mileage_max is not None:
        stmt = stmt.where(Listing.mileage_km <= mileage_max)
    if brand:
        stmt = stmt.where(Listing.brand.ilike(f"%{brand}%"))
    if model:
        stmt = stmt.where(Listing.model.ilike(f"%{model}%"))
    if vehicle_type:
        stmt = stmt.where(Listing.layout_type == vehicle_type)
    if seller_type:
        stmt = stmt.where(Listing.seller_type == seller_type)
    if length_max_mm is not None:
        stmt = stmt.where(Listing.length_mm <= length_max_mm)
    if sleeping_min is not None:
        stmt = stmt.where(Listing.seats_sleeping >= sleeping_min)
    if travel_seats_min is not None:
        stmt = stmt.where(Listing.seats_travel >= travel_seats_min)
    if has_rear_garage is not None:
        stmt = stmt.where(Listing.has_rear_garage == has_rear_garage)
    if garage_size:
        stmt = stmt.where(Listing.garage_size_category == garage_size)
    if license_category:
        stmt = stmt.where(Listing.driving_license_category == license_category)
    if only_with_coords:
        stmt = stmt.where(
            Listing.latitude.isnot(None), Listing.longitude.isnot(None)
        )
    if min_extraction_confidence is not None:
        stmt = stmt.where(
            Listing.extraction_confidence >= min_extraction_confidence
        )
    if min_enrichment_confidence is not None:
        stmt = stmt.where(
            Listing.enrichment_confidence >= min_enrichment_confidence
        )

    # ---- required features (inner join per key) ----
    if features:
        for fkey in features:
            alias = ListingFeature.__table__.alias()
            stmt = stmt.join(
                alias,
                (alias.c.listing_id == Listing.id)
                & (alias.c.feature_key == fkey),
            )

    # ---- excluded features (NOT EXISTS subquery) ----
    if exclude_features:
        for fkey in exclude_features:
            sub = (
                select(ListingFeature.id)
                .where(
                    ListingFeature.listing_id == Listing.id,
                    ListingFeature.feature_key == fkey,
                )
                .correlate(Listing)
            )
            stmt = stmt.where(~sub.exists())

    # ---- count ----
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total: int = (await session.execute(count_stmt)).scalar_one()

    # ---- sorting ----
    order_col = {
        "price_asc": Listing.price.asc(),
        "price_desc": Listing.price.desc(),
        "year_asc": Listing.year.asc(),
        "year_desc": Listing.year.desc(),
        "mileage_asc": Listing.mileage_km.asc(),
        "mileage_desc": Listing.mileage_km.desc(),
        "first_seen": Listing.first_seen_at.desc(),
        "last_seen": Listing.last_seen_at.desc(),
        "relevance": Listing.last_seen_at.desc(),
    }.get(sort_by, Listing.last_seen_at.desc())

    stmt = stmt.order_by(order_col)

    # ---- pagination ----
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)

    rows = (await session.execute(stmt)).scalars().unique().all()
    items = [ListingRead.model_validate(r) for r in rows]

    return ListingSearchResult(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if page_size else 0,
    )
