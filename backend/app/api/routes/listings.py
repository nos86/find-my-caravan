from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.listing import (
    ListingCreate,
    ListingRead,
    ListingSearchResult,
    ListingUpdate,
    ManualUrlCreate,
)
from app.services import listing_service

router = APIRouter(tags=["listings"])


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


@router.get("/listings", response_model=ListingSearchResult)
async def search_listings(
    q: Optional[str] = Query(None, description="Full-text search"),
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
    features: list[str] = Query(default=[]),
    exclude_features: list[str] = Query(default=[]),
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
    sort_by: str = Query(default="last_seen"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> ListingSearchResult:
    return await listing_service.search_listings(
        session,
        q=q,
        source_type=source_type,
        region=region,
        province=province,
        city=city,
        price_min=price_min,
        price_max=price_max,
        year_min=year_min,
        year_max=year_max,
        mileage_min=mileage_min,
        mileage_max=mileage_max,
        brand=brand,
        model=model,
        vehicle_type=vehicle_type,
        seller_type=seller_type,
        features=features or None,
        exclude_features=exclude_features or None,
        length_max_mm=length_max_mm,
        sleeping_min=sleeping_min,
        travel_seats_min=travel_seats_min,
        has_rear_garage=has_rear_garage,
        garage_size=garage_size,
        license_category=license_category,
        only_with_coords=only_with_coords,
        only_active=only_active,
        min_extraction_confidence=min_extraction_confidence,
        min_enrichment_confidence=min_enrichment_confidence,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )


# ---------------------------------------------------------------------------
# Individual listing CRUD
# ---------------------------------------------------------------------------


@router.get("/listings/{listing_id}", response_model=ListingRead)
async def get_listing(
    listing_id: int, session: AsyncSession = Depends(get_session)
) -> ListingRead:
    obj = await listing_service.get_listing(session, listing_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    return ListingRead.model_validate(obj)


@router.patch("/listings/{listing_id}", response_model=ListingRead)
async def update_listing(
    listing_id: int,
    data: ListingUpdate,
    session: AsyncSession = Depends(get_session),
) -> ListingRead:
    obj = await listing_service.update_listing(session, listing_id, data)
    if obj is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    return ListingRead.model_validate(obj)


@router.delete("/listings/{listing_id}", status_code=204)
async def delete_listing(
    listing_id: int, session: AsyncSession = Depends(get_session)
) -> None:
    deleted = await listing_service.delete_listing(session, listing_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Listing not found")


@router.post("/listings/{listing_id}/mark-sold", response_model=ListingRead)
async def mark_sold(
    listing_id: int, session: AsyncSession = Depends(get_session)
) -> ListingRead:
    obj = await listing_service.mark_sold(session, listing_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    return ListingRead.model_validate(obj)


# ---------------------------------------------------------------------------
# Manual creation
# ---------------------------------------------------------------------------


@router.post("/manual-listings", response_model=ListingRead, status_code=201)
async def create_manual_listing(
    data: ListingCreate, session: AsyncSession = Depends(get_session)
) -> ListingRead:
    obj = await listing_service.create_listing(session, data)
    return ListingRead.model_validate(obj)


@router.post("/manual-urls", status_code=201)
async def register_manual_url(
    data: ManualUrlCreate,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Register a URL for future ingestion. Validates scheme to prevent SSRF."""
    from urllib.parse import urlparse
    from app.core.config import settings

    parsed = urlparse(data.url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(
            status_code=422,
            detail="URL must use http or https scheme",
        )
    if not parsed.netloc:
        raise HTTPException(status_code=422, detail="Invalid URL")

    if settings.ALLOWED_DOMAINS:
        host = parsed.hostname or ""
        if host not in settings.ALLOWED_DOMAINS:
            raise HTTPException(
                status_code=422,
                detail=f"Domain '{host}' is not in the allowed domains list",
            )

    return {"registered": True, "url": data.url}
