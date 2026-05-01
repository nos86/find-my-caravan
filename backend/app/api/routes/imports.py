from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_session
from app.models.listing import Source
from app.schemas.imports import ImportPreviewResult, ImportResult
from app.services import import_service

router = APIRouter(prefix="/imports", tags=["imports"])

_DEFAULT_SOURCE_NAME = "manual_import"
_DEFAULT_SOURCE_TYPE = "csv"


async def _get_or_create_source(
    session: AsyncSession, source_name: str, source_type: str
) -> Source:
    result = await session.execute(
        select(Source).where(Source.name == source_name).limit(1)
    )
    obj = result.scalars().first()
    if obj is None:
        obj = Source(name=source_name, source_type=source_type)
        session.add(obj)
        await session.flush()
    return obj


def _check_size(file: UploadFile) -> None:
    """Validate that the uploaded file doesn't exceed the configured limit."""
    # Content-Length may not always be available; we check after reading.
    pass


@router.post("/csv/preview", response_model=ImportPreviewResult)
async def preview_csv(file: UploadFile = File(...)) -> ImportPreviewResult:
    content = await file.read()
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum upload size of {settings.MAX_UPLOAD_SIZE_MB} MB",
        )
    return await import_service.preview_csv(content)


@router.post("/csv", response_model=ImportResult, status_code=201)
async def import_csv(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
) -> ImportResult:
    content = await file.read()
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum upload size of {settings.MAX_UPLOAD_SIZE_MB} MB",
        )
    source = await _get_or_create_source(
        session, file.filename or _DEFAULT_SOURCE_NAME, "csv"
    )
    return await import_service.import_csv(
        session, content, source.id, source.name
    )


@router.post("/json/preview", response_model=ImportPreviewResult)
async def preview_json(file: UploadFile = File(...)) -> ImportPreviewResult:
    content = await file.read()
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum upload size of {settings.MAX_UPLOAD_SIZE_MB} MB",
        )
    try:
        return await import_service.preview_json(content)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/json", response_model=ImportResult, status_code=201)
async def import_json(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
) -> ImportResult:
    content = await file.read()
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum upload size of {settings.MAX_UPLOAD_SIZE_MB} MB",
        )
    try:
        source = await _get_or_create_source(
            session, file.filename or _DEFAULT_SOURCE_NAME, "json"
        )
        return await import_service.import_json(
            session, content, source.id, source.name
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
