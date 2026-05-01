from __future__ import annotations

import pytest

from app.models.listing import Source
from app.schemas.feature import FeatureDefinitionCreate
from app.schemas.listing import ListingCreate
from app.services.feature_service import (
    assign_feature,
    create_feature_definition,
    list_feature_definitions,
    search_by_features,
)
from app.services.listing_service import create_listing


async def _make_source(session, name: str = "feat_src") -> Source:
    src = Source(name=name, source_type="manual")
    session.add(src)
    await session.flush()
    return src


async def _make_listing(session, source_id: int, title: str = "Feature Test Camper"):
    data = ListingCreate(source_id=source_id, title=title)
    return await create_listing(session, data)


# ---------------------------------------------------------------------------
# FeatureDefinition CRUD
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_feature_definition(session):
    fd = await create_feature_definition(
        session,
        FeatureDefinitionCreate(
            key="garage_grande",
            label="Garage Grande",
            description="Garage > 180cm",
            category="storage",
        ),
    )
    assert fd.id is not None
    assert fd.key == "garage_grande"
    assert fd.label == "Garage Grande"


@pytest.mark.asyncio
async def test_list_feature_definitions(session):
    await create_feature_definition(
        session,
        FeatureDefinitionCreate(key="solar_panel_hv", label="Solar 400W", category="energy"),
    )
    results = await list_feature_definitions(session)
    keys = [r.key for r in results]
    assert "solar_panel_hv" in keys


@pytest.mark.asyncio
async def test_duplicate_feature_key_raises(session):
    """Creating a feature definition with a duplicate key should raise an IntegrityError."""
    from sqlalchemy.exc import IntegrityError

    await create_feature_definition(
        session,
        FeatureDefinitionCreate(key="unique_feature_x", label="Unique"),
    )
    await session.flush()

    with pytest.raises(IntegrityError):
        await create_feature_definition(
            session,
            FeatureDefinitionCreate(key="unique_feature_x", label="Duplicate"),
        )
        await session.flush()


# ---------------------------------------------------------------------------
# Assign feature to listing
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_assign_feature(session):
    src = await _make_source(session, "feat_src_assign")
    listing = await _make_listing(session, src.id)

    feature = await assign_feature(
        session, listing.id, "mansardato", value="true", confidence=0.95
    )
    assert feature.id is not None
    assert feature.feature_key == "mansardato"
    assert feature.confidence == 0.95


@pytest.mark.asyncio
async def test_assign_multiple_features(session):
    src = await _make_source(session, "feat_src_multi")
    listing = await _make_listing(session, src.id, title="Multi Feature Camper")
    listing_id = listing.id

    await assign_feature(session, listing_id, "aria_condizionata")
    await assign_feature(session, listing_id, "pannello_solare")
    await assign_feature(session, listing_id, "doppio_pavimento")
    await session.flush()
    session.expire_all()

    # Reload the listing with features
    from app.services.listing_service import get_listing
    loaded = await get_listing(session, listing_id)
    assert loaded is not None
    feature_keys = {f.feature_key for f in loaded.features}
    assert "aria_condizionata" in feature_keys
    assert "pannello_solare" in feature_keys
    assert "doppio_pavimento" in feature_keys


# ---------------------------------------------------------------------------
# Search by features
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_filter_listings_by_feature(session):
    src = await _make_source(session, "feat_src_search")

    listing_with = await _make_listing(session, src.id, title="With Garage")
    listing_without = await _make_listing(session, src.id, title="Without Garage")

    await assign_feature(session, listing_with.id, "garage_posteriore")
    await session.flush()

    result = await search_by_features(
        session,
        features=["garage_posteriore"],
        exclude_features=[],
        page=1,
        page_size=20,
    )
    ids = {item.id for item in result.items}
    assert listing_with.id in ids
    assert listing_without.id not in ids


@pytest.mark.asyncio
async def test_exclude_feature(session):
    src = await _make_source(session, "feat_src_excl")

    listing_a = await _make_listing(session, src.id, title="Has Feature A")
    listing_b = await _make_listing(session, src.id, title="Does Not Have Feature A")

    await assign_feature(session, listing_a.id, "feature_to_exclude")
    await session.flush()

    result = await search_by_features(
        session,
        features=[],
        exclude_features=["feature_to_exclude"],
        page=1,
        page_size=100,
    )
    ids = {item.id for item in result.items}
    assert listing_a.id not in ids
    assert listing_b.id in ids


@pytest.mark.asyncio
async def test_filter_requires_all_features(session):
    """A listing must have ALL required features to appear in results."""
    src = await _make_source(session, "feat_src_all")

    listing_both = await _make_listing(session, src.id, title="Both Features")
    listing_one = await _make_listing(session, src.id, title="Only One Feature")

    await assign_feature(session, listing_both.id, "feature_alpha")
    await assign_feature(session, listing_both.id, "feature_beta")
    await assign_feature(session, listing_one.id, "feature_alpha")
    await session.flush()

    result = await search_by_features(
        session,
        features=["feature_alpha", "feature_beta"],
        exclude_features=[],
        page=1,
        page_size=20,
    )
    ids = {item.id for item in result.items}
    assert listing_both.id in ids
    assert listing_one.id not in ids
