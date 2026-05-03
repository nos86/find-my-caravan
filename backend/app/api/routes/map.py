from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.listing import Listing
from app.schemas.listing import MapListing

router = APIRouter(prefix="/map", tags=["map"])


@router.get("/listings", response_model=list[MapListing])
async def map_listings(
    session: AsyncSession = Depends(get_session),
) -> list[MapListing]:
    stmt = (
        select(
            Listing.id,
            Listing.title,
            Listing.price,
            Listing.year,
            Listing.latitude,
            Listing.longitude,
            Listing.seller_type,
            Listing.source_name,
        )
        .where(
            Listing.status == "active",
            Listing.latitude.isnot(None),
            Listing.longitude.isnot(None),
        )
        .order_by(Listing.id)
    )
    rows = (await session.execute(stmt)).all()
    return [
        MapListing(
            id=r.id,
            title=r.title,
            price=r.price,
            year=r.year,
            latitude=r.latitude,
            longitude=r.longitude,
            seller_type=r.seller_type,
            source_name=r.source_name,
        )
        for r in rows
    ]
