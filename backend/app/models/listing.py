from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Source
# ---------------------------------------------------------------------------


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(
        String(64), nullable=False
    )  # manual/csv/json/saved_html/dealer_website/authorized_feed
    base_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    allowed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    robots_checked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    terms_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rate_limit_seconds: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    listings: Mapped[list["Listing"]] = relationship(
        "Listing", back_populates="source", lazy="noload"
    )
    ingestion_runs: Mapped[list["IngestionRun"]] = relationship(
        "IngestionRun", back_populates="source", lazy="noload"
    )


# ---------------------------------------------------------------------------
# Listing
# ---------------------------------------------------------------------------


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sources.id", ondelete="RESTRICT"), nullable=False
    )
    source_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)

    title: Mapped[str] = mapped_column(String(512), nullable=False)
    brand: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    version: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mileage_km: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fuel_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    transmission: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    engine_power_kw: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    engine_displacement_cc: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    emission_class: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    length_mm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    width_mm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height_mm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mass_kg: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    driving_license_category: Mapped[Optional[str]] = mapped_column(
        String(8), nullable=True
    )
    seats_travel: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    seats_sleeping: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    layout_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    bed_types: Mapped[Optional[list[str]]] = mapped_column(JSONB, nullable=True)
    has_rear_garage: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    garage_size_category: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True
    )  # none/small/medium/large/unknown
    has_bunk_beds: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_double_floor: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    bathroom_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    heating_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    air_conditioning: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    solar_panel: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    tow_bar: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    seller_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    seller_type: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True
    )  # private/dealer/unknown
    address_raw: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    province: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    description_raw: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    images: Mapped[Optional[list[str]]] = mapped_column(JSONB, nullable=True)

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(16), default="active", nullable=False
    )  # active/inactive/sold/unknown

    extraction_confidence: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    enrichment_confidence: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    raw_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    source: Mapped["Source"] = relationship(
        "Source", back_populates="listings", lazy="noload"
    )
    features: Mapped[list["ListingFeature"]] = relationship(
        "ListingFeature",
        back_populates="listing",
        cascade="all, delete-orphan",
        lazy="noload",
    )


# ---------------------------------------------------------------------------
# FeatureDefinition
# ---------------------------------------------------------------------------


class FeatureDefinition(Base):
    __tablename__ = "feature_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )


# ---------------------------------------------------------------------------
# ListingFeature
# ---------------------------------------------------------------------------


class ListingFeature(Base):
    __tablename__ = "listing_features"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("listings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    feature_key: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    listing: Mapped["Listing"] = relationship(
        "Listing", back_populates="features", lazy="noload"
    )


# ---------------------------------------------------------------------------
# IngestionRun
# ---------------------------------------------------------------------------


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sources.id", ondelete="SET NULL"), nullable=True
    )
    run_type: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # csv/json/saved_html/manual/connector
    status: Mapped[str] = mapped_column(
        String(16), nullable=False
    )  # running/completed/failed
    total_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_imported: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_skipped: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_errors: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    source: Mapped[Optional["Source"]] = relationship(
        "Source", back_populates="ingestion_runs", lazy="noload"
    )
    extraction_errors: Mapped[list["ExtractionError"]] = relationship(
        "ExtractionError",
        back_populates="ingestion_run",
        cascade="all, delete-orphan",
        lazy="noload",
    )


# ---------------------------------------------------------------------------
# ExtractionError
# ---------------------------------------------------------------------------


class ExtractionError(Base):
    __tablename__ = "extraction_errors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ingestion_run_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("ingestion_runs.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    error_type: Mapped[str] = mapped_column(String(64), nullable=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    raw_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    ingestion_run: Mapped[Optional["IngestionRun"]] = relationship(
        "IngestionRun", back_populates="extraction_errors", lazy="noload"
    )
