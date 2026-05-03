from __future__ import annotations

import csv
import io
import json
import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.listing import ExtractionError, IngestionRun, Listing, Source
from app.schemas.imports import ImportPreviewResult, ImportResult

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Column mapping: alias → schema field
# ---------------------------------------------------------------------------

COLUMN_MAP: dict[str, str] = {
    "title": "title",
    "titolo": "title",
    "price": "price",
    "prezzo": "price",
    "year": "year",
    "anno": "year",
    "mileage": "mileage_km",
    "km": "mileage_km",
    "chilometri": "mileage_km",
    "brand": "brand",
    "marca": "brand",
    "model": "model",
    "modello": "model",
    "version": "version",
    "versione": "version",
    "city": "city",
    "città": "city",
    "citta": "city",
    "province": "province",
    "provincia": "province",
    "region": "region",
    "regione": "region",
    "source_url": "source_url",
    "url": "source_url",
    "link": "source_url",
    "description": "description_raw",
    "descrizione": "description_raw",
    "description_raw": "description_raw",
    "seller_name": "seller_name",
    "venditore": "seller_name",
    "seller_type": "seller_type",
    "tipo_venditore": "seller_type",
    "fuel": "fuel_type",
    "carburante": "fuel_type",
    "fuel_type": "fuel_type",
    "transmission": "transmission",
    "cambio": "transmission",
    "layout_type": "layout_type",
    "tipo": "layout_type",
    "length_mm": "length_mm",
    "lunghezza_mm": "length_mm",
    "seats_sleeping": "seats_sleeping",
    "posti_letto": "seats_sleeping",
    "seats_travel": "seats_travel",
    "posti_viaggio": "seats_travel",
}

# Known Italian regions (lower-case for comparison)
ITALIAN_REGIONS = {
    "abruzzo", "basilicata", "calabria", "campania", "emilia-romagna",
    "friuli-venezia giulia", "lazio", "liguria", "lombardia", "marche",
    "molise", "piemonte", "puglia", "sardegna", "sicilia", "toscana",
    "trentino-alto adige", "umbria", "valle d'aosta", "veneto",
}

_URL_RE = re.compile(r"^https?://", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def _validate_price(raw: Any) -> tuple[float | None, str | None]:
    if raw is None or str(raw).strip() == "":
        return None, None
    try:
        v = float(str(raw).replace(",", ".").replace("€", "").strip())
        if v < 0:
            return None, f"price must be non-negative, got {v!r}"
        return v, None
    except (ValueError, TypeError):
        return None, f"invalid price value: {raw!r}"


def _validate_year(raw: Any) -> tuple[int | None, str | None]:
    if raw is None or str(raw).strip() == "":
        return None, None
    try:
        v = int(str(raw).strip())
        if not (1990 <= v <= 2030):
            return None, f"year {v} not in range 1990-2030"
        return v, None
    except (ValueError, TypeError):
        return None, f"invalid year value: {raw!r}"


def _validate_mileage(raw: Any) -> tuple[int | None, str | None]:
    if raw is None or str(raw).strip() == "":
        return None, None
    try:
        v = int(str(raw).replace(".", "").replace(",", "").strip())
        if v < 0:
            return None, f"mileage must be non-negative, got {v!r}"
        return v, None
    except (ValueError, TypeError):
        return None, f"invalid mileage value: {raw!r}"


def _validate_url(raw: Any) -> tuple[str | None, str | None]:
    if raw is None or str(raw).strip() == "":
        return None, None
    s = str(raw).strip()
    if not _URL_RE.match(s):
        return None, f"source_url must start with http:// or https://, got {s!r}"
    parsed = urlparse(s)
    if not parsed.scheme or not parsed.netloc:
        return None, f"invalid URL: {s!r}"
    return s, None


# ---------------------------------------------------------------------------
# Row processor
# ---------------------------------------------------------------------------


def _map_columns(raw_row: dict[str, Any]) -> dict[str, str]:
    """Return {schema_field: raw_value} by resolving column aliases."""
    mapped: dict[str, str] = {}
    for col, val in raw_row.items():
        normalized = col.strip().lower().replace(" ", "_")
        schema_field = COLUMN_MAP.get(normalized)
        if schema_field and schema_field not in mapped:
            mapped[schema_field] = val
    return mapped


def _process_row(
    raw_row: dict[str, Any],
    row_num: int,
) -> tuple[dict[str, Any] | None, list[str]]:
    """Map, validate, and coerce a single raw row.

    Returns (cleaned_dict, errors).  If cleaned_dict is None the row should be
    skipped entirely.
    """
    errors: list[str] = []
    mapped = _map_columns(raw_row)

    # title is required
    title = mapped.get("title", "").strip()
    if not title:
        errors.append(f"row {row_num}: missing required field 'title'")
        return None, errors

    cleaned: dict[str, Any] = {"title": title}

    if "price" in mapped:
        price, err = _validate_price(mapped["price"])
        if err:
            errors.append(f"row {row_num}: {err}")
        else:
            cleaned["price"] = price

    if "year" in mapped:
        year, err = _validate_year(mapped["year"])
        if err:
            errors.append(f"row {row_num}: {err}")
        else:
            cleaned["year"] = year

    if "mileage_km" in mapped:
        km, err = _validate_mileage(mapped["mileage_km"])
        if err:
            errors.append(f"row {row_num}: {err}")
        else:
            cleaned["mileage_km"] = km

    if "source_url" in mapped:
        url, err = _validate_url(mapped["source_url"])
        if err:
            errors.append(f"row {row_num}: {err}")
        else:
            cleaned["source_url"] = url

    # Simple string pass-throughs
    for field in (
        "brand", "model", "version", "fuel_type", "transmission",
        "layout_type", "seller_name", "seller_type", "city",
        "province", "region", "description_raw",
    ):
        if field in mapped and str(mapped[field]).strip():
            cleaned[field] = str(mapped[field]).strip()

    # Optional region warn
    if "region" in cleaned:
        if cleaned["region"].lower() not in ITALIAN_REGIONS:
            errors.append(
                f"row {row_num}: region '{cleaned['region']}' not a recognised Italian region (warning only)"
            )

    return cleaned, errors


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------


def _detect_column_mapping(columns: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for col in columns:
        normalized = col.strip().lower().replace(" ", "_")
        target = COLUMN_MAP.get(normalized)
        if target:
            mapping[col] = target
    return mapping


async def preview_csv(content: bytes) -> ImportPreviewResult:
    text = content.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    rows: list[dict] = []
    warnings: list[str] = []

    for i, row in enumerate(reader, start=1):
        rows.append(dict(row))
        if i >= 10:
            break

    # Count total rows (re-parse)
    total = sum(1 for _ in csv.DictReader(io.StringIO(text)))

    columns = list(reader.fieldnames or [])
    column_mapping = _detect_column_mapping(columns)

    if "title" not in column_mapping.values() and "titolo" not in [
        c.lower() for c in columns
    ]:
        warnings.append("No 'title' column detected – import may skip all rows")

    return ImportPreviewResult(
        columns_detected=columns,
        column_mapping=column_mapping,
        preview_rows=rows,
        total_rows=total,
        validation_warnings=warnings,
    )


async def import_csv(
    session: AsyncSession,
    content: bytes,
    source_id: int,
    source_name: str,
) -> ImportResult:
    text = content.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)

    run = IngestionRun(
        source_id=source_id,
        run_type="csv",
        status="running",
        total_found=len(rows),
        started_at=datetime.now(timezone.utc),
    )
    session.add(run)
    await session.flush()

    imported = 0
    skipped = 0
    error_msgs: list[str] = []
    now = datetime.now(timezone.utc)

    for i, raw_row in enumerate(rows, start=1):
        cleaned, errs = _process_row(raw_row, i)
        error_msgs.extend(errs)
        if cleaned is None:
            skipped += 1
            # Persist first 100 extraction errors
            if len(error_msgs) <= 100:
                session.add(
                    ExtractionError(
                        ingestion_run_id=run.id,
                        error_type="validation",
                        error_message="; ".join(errs),
                        raw_data=json.dumps(raw_row),
                    )
                )
            continue

        listing = Listing(
            source_id=source_id,
            source_name=source_name,
            source_type="csv",
            first_seen_at=now,
            last_seen_at=now,
            raw_data=raw_row,
            **cleaned,
        )
        session.add(listing)
        imported += 1

    run.total_imported = imported
    run.total_skipped = skipped
    run.total_errors = len([e for e in error_msgs if "warning" not in e.lower()])
    run.status = "completed"
    run.finished_at = datetime.now(timezone.utc)
    await session.flush()

    return ImportResult(
        ingestion_run_id=run.id,
        total_found=len(rows),
        total_imported=imported,
        total_skipped=skipped,
        total_errors=run.total_errors,
        errors=error_msgs[:20],
    )


# ---------------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------------


async def preview_json(content: bytes) -> ImportPreviewResult:
    data = json.loads(content.decode("utf-8"))
    if isinstance(data, dict):
        # Support {listings: [...]} envelope
        for key in ("listings", "items", "data", "results"):
            if key in data and isinstance(data[key], list):
                data = data[key]
                break
        else:
            data = [data]

    if not isinstance(data, list):
        raise ValueError("JSON must be an array of objects (or envelope with array)")

    rows: list[dict] = data[:10]
    columns = sorted({k for row in data for k in row.keys()})
    column_mapping = _detect_column_mapping(columns)
    warnings: list[str] = []

    if "title" not in column_mapping.values():
        warnings.append("No 'title' field detected – import may skip all rows")

    return ImportPreviewResult(
        columns_detected=columns,
        column_mapping=column_mapping,
        preview_rows=rows,
        total_rows=len(data),
        validation_warnings=warnings,
    )


async def import_json(
    session: AsyncSession,
    content: bytes,
    source_id: int,
    source_name: str,
) -> ImportResult:
    data = json.loads(content.decode("utf-8"))
    if isinstance(data, dict):
        for key in ("listings", "items", "data", "results"):
            if key in data and isinstance(data[key], list):
                data = data[key]
                break
        else:
            data = [data]

    if not isinstance(data, list):
        raise ValueError("JSON must be an array of objects")

    run = IngestionRun(
        source_id=source_id,
        run_type="json",
        status="running",
        total_found=len(data),
        started_at=datetime.now(timezone.utc),
    )
    session.add(run)
    await session.flush()

    imported = 0
    skipped = 0
    error_msgs: list[str] = []
    now = datetime.now(timezone.utc)

    for i, raw_row in enumerate(data, start=1):
        if not isinstance(raw_row, dict):
            error_msgs.append(f"row {i}: not a JSON object, skipped")
            skipped += 1
            continue

        cleaned, errs = _process_row(raw_row, i)
        error_msgs.extend(errs)
        if cleaned is None:
            skipped += 1
            if len(error_msgs) <= 100:
                session.add(
                    ExtractionError(
                        ingestion_run_id=run.id,
                        error_type="validation",
                        error_message="; ".join(errs),
                        raw_data=json.dumps(raw_row),
                    )
                )
            continue

        listing = Listing(
            source_id=source_id,
            source_name=source_name,
            source_type="json",
            first_seen_at=now,
            last_seen_at=now,
            raw_data=raw_row,
            **cleaned,
        )
        session.add(listing)
        imported += 1

    run.total_imported = imported
    run.total_skipped = skipped
    run.total_errors = len([e for e in error_msgs if "warning" not in e.lower()])
    run.status = "completed"
    run.finished_at = datetime.now(timezone.utc)
    await session.flush()

    return ImportResult(
        ingestion_run_id=run.id,
        total_found=len(data),
        total_imported=imported,
        total_skipped=skipped,
        total_errors=run.total_errors,
        errors=error_msgs[:20],
    )
