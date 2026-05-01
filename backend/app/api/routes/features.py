from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.feature import (
    FeatureDefinitionCreate,
    FeatureDefinitionRead,
    FeatureSearchRequest,
)
from app.schemas.listing import ListingSearchResult
from app.services import feature_service

router = APIRouter(prefix="/features", tags=["features"])


@router.get("", response_model=list[FeatureDefinitionRead])
async def list_features(
    session: AsyncSession = Depends(get_session),
) -> list[FeatureDefinitionRead]:
    return await feature_service.list_feature_definitions(session)


@router.post(
    "", response_model=FeatureDefinitionRead, status_code=status.HTTP_201_CREATED
)
async def create_feature(
    data: FeatureDefinitionCreate,
    session: AsyncSession = Depends(get_session),
) -> FeatureDefinitionRead:
    return await feature_service.create_feature_definition(session, data)


@router.post("/search", response_model=ListingSearchResult)
async def search_by_features(
    req: FeatureSearchRequest,
    session: AsyncSession = Depends(get_session),
) -> ListingSearchResult:
    return await feature_service.search_by_features(
        session,
        features=req.features,
        exclude_features=req.exclude_features,
        page=req.page,
        page_size=req.page_size,
    )
