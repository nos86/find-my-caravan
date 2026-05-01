from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.listing import Source
from app.schemas.listing import SourceCreate, SourceRead, SourceUpdate

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=list[SourceRead])
async def list_sources(session: AsyncSession = Depends(get_session)) -> list[SourceRead]:
    rows = (await session.execute(select(Source).order_by(Source.id))).scalars().all()
    return [SourceRead.model_validate(r) for r in rows]


@router.post("", response_model=SourceRead, status_code=status.HTTP_201_CREATED)
async def create_source(
    data: SourceCreate, session: AsyncSession = Depends(get_session)
) -> SourceRead:
    obj = Source(**data.model_dump())
    session.add(obj)
    await session.flush()
    return SourceRead.model_validate(obj)


@router.patch("/{source_id}", response_model=SourceRead)
async def update_source(
    source_id: int,
    data: SourceUpdate,
    session: AsyncSession = Depends(get_session),
) -> SourceRead:
    obj = await session.get(Source, source_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Source not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await session.flush()
    return SourceRead.model_validate(obj)


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    source_id: int, session: AsyncSession = Depends(get_session)
) -> None:
    obj = await session.get(Source, source_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Source not found")
    await session.delete(obj)
