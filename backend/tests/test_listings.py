from __future__ import annotations

import pytest

from app.models.listing import Listing, Source
from app.schemas.listing import ListingCreate, ListingUpdate
from app.services.listing_service import (
    create_listing,
    delete_listing,
    get_listing,
    mark_sold,
    search_listings,
    update_listing,
)


async def _make_source(session, name: str = "test_source") -> Source:
    src = Source(name=name, source_type="manual")
    session.add(src)
    await session.flush()
    return src


async def _make_listing(session, source_id: int, **kwargs) -> Listing:
    defaults = dict(
        source_id=source_id,
        title="Test Camper",
        price=20000.0,
        year=2018,
        region="Lombardia",
        city="Milano",
        brand="Fiat",
    )
    defaults.update(kwargs)
    data = ListingCreate(**defaults)
    return await create_listing(session, data)


# ---------------------------------------------------------------------------
# Basic CRUD
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_listing(session):
    src = await _make_source(session)
    listing = await _make_listing(session, src.id)
    assert listing.id is not None
    assert listing.title == "Test Camper"
    assert listing.price == 20000.0
    assert listing.status == "active"


@pytest.mark.asyncio
async def test_get_listing(session):
    src = await _make_source(session, "src_get")
    listing = await _make_listing(session, src.id)
    fetched = await get_listing(session, listing.id)
    assert fetched is not None
    assert fetched.id == listing.id


@pytest.mark.asyncio
async def test_get_listing_not_found(session):
    result = await get_listing(session, 99999)
    assert result is None


@pytest.mark.asyncio
async def test_update_listing(session):
    src = await _make_source(session, "src_upd")
    listing = await _make_listing(session, src.id)
    updated = await update_listing(
        session, listing.id, ListingUpdate(price=18000.0, city="Torino")
    )
    assert updated is not None
    assert updated.price == 18000.0
    assert updated.city == "Torino"


@pytest.mark.asyncio
async def test_delete_listing(session):
    src = await _make_source(session, "src_del")
    listing = await _make_listing(session, src.id)
    listing_id = listing.id
    deleted = await delete_listing(session, listing_id)
    assert deleted is True
    await session.flush()
    session.expire_all()
    assert await get_listing(session, listing_id) is None


@pytest.mark.asyncio
async def test_mark_sold(session):
    src = await _make_source(session, "src_sold")
    listing = await _make_listing(session, src.id)
    result = await mark_sold(session, listing.id)
    assert result is not None
    assert result.status == "sold"


# ---------------------------------------------------------------------------
# Search / filter
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_by_text(session):
    src = await _make_source(session, "src_txt")
    await _make_listing(session, src.id, title="Mansardato Adria Matrix")
    await _make_listing(session, src.id, title="Integrato Knaus")

    result = await search_listings(session, q="Adria", only_active=True)
    assert result.total >= 1
    assert any("Adria" in item.title for item in result.items)


@pytest.mark.asyncio
async def test_search_by_brand(session):
    src = await _make_source(session, "src_brand")
    await _make_listing(session, src.id, brand="Hobby", title="Hobby 600")
    await _make_listing(session, src.id, brand="Eriba", title="Eriba Nova")

    result = await search_listings(session, brand="Hobby")
    assert all(item.brand == "Hobby" for item in result.items)


@pytest.mark.asyncio
async def test_filter_price_range(session):
    src = await _make_source(session, "src_price")
    await _make_listing(session, src.id, price=5000.0, title="Budget Camper")
    await _make_listing(session, src.id, price=50000.0, title="Premium Camper")

    result = await search_listings(session, price_min=10000, price_max=60000)
    prices = [item.price for item in result.items if item.price is not None]
    assert all(10000 <= p <= 60000 for p in prices)


@pytest.mark.asyncio
async def test_filter_by_region(session):
    src = await _make_source(session, "src_region")
    await _make_listing(session, src.id, region="Toscana", title="Toscana Camper")
    await _make_listing(session, src.id, region="Sicilia", title="Sicilia Camper")

    result = await search_listings(session, region="Toscana")
    assert result.total >= 1
    assert all("oscana" in (item.region or "") for item in result.items)


@pytest.mark.asyncio
async def test_pagination(session):
    src = await _make_source(session, "src_page")
    for i in range(15):
        await _make_listing(session, src.id, title=f"Camper Page {i}", brand="PageTest")

    page1 = await search_listings(session, brand="PageTest", page=1, page_size=5)
    page2 = await search_listings(session, brand="PageTest", page=2, page_size=5)
    page3 = await search_listings(session, brand="PageTest", page=3, page_size=5)

    assert len(page1.items) == 5
    assert len(page2.items) == 5
    assert len(page3.items) == 5
    assert page1.total >= 15
    assert page1.pages >= 3

    ids1 = {item.id for item in page1.items}
    ids2 = {item.id for item in page2.items}
    assert ids1.isdisjoint(ids2)


@pytest.mark.asyncio
async def test_only_active_filter(session):
    src = await _make_source(session, "src_active")
    active = await _make_listing(session, src.id, title="Active Camper", brand="ActiveBrand")
    sold = await _make_listing(session, src.id, title="Sold Camper", brand="ActiveBrand")
    await mark_sold(session, sold.id)

    result = await search_listings(session, brand="ActiveBrand", only_active=True)
    ids = {item.id for item in result.items}
    assert active.id in ids
    assert sold.id not in ids


@pytest.mark.asyncio
async def test_sort_price_asc(session):
    src = await _make_source(session, "src_sort")
    await _make_listing(session, src.id, price=30000.0, title="Sort C", brand="SortBrand")
    await _make_listing(session, src.id, price=10000.0, title="Sort A", brand="SortBrand")
    await _make_listing(session, src.id, price=20000.0, title="Sort B", brand="SortBrand")

    result = await search_listings(session, brand="SortBrand", sort_by="price_asc")
    prices = [item.price for item in result.items if item.price is not None]
    assert prices == sorted(prices)
