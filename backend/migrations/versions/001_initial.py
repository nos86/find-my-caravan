"""initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("source_type", sa.String(64), nullable=False),
        sa.Column("base_url", sa.String(2048), nullable=True),
        sa.Column("allowed", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("robots_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("terms_notes", sa.Text(), nullable=True),
        sa.Column("rate_limit_seconds", sa.Integer(), nullable=False, server_default=sa.text("5")),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "listings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("source_name", sa.String(255), nullable=True),
        sa.Column("source_type", sa.String(64), nullable=True),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("brand", sa.String(128), nullable=True),
        sa.Column("model", sa.String(128), nullable=True),
        sa.Column("version", sa.String(128), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("mileage_km", sa.Integer(), nullable=True),
        sa.Column("fuel_type", sa.String(64), nullable=True),
        sa.Column("transmission", sa.String(64), nullable=True),
        sa.Column("engine_power_kw", sa.Float(), nullable=True),
        sa.Column("engine_displacement_cc", sa.Integer(), nullable=True),
        sa.Column("emission_class", sa.String(16), nullable=True),
        sa.Column("length_mm", sa.Integer(), nullable=True),
        sa.Column("width_mm", sa.Integer(), nullable=True),
        sa.Column("height_mm", sa.Integer(), nullable=True),
        sa.Column("mass_kg", sa.Integer(), nullable=True),
        sa.Column("driving_license_category", sa.String(8), nullable=True),
        sa.Column("seats_travel", sa.Integer(), nullable=True),
        sa.Column("seats_sleeping", sa.Integer(), nullable=True),
        sa.Column("layout_type", sa.String(64), nullable=True),
        sa.Column("bed_types", postgresql.JSONB(), nullable=True),
        sa.Column("has_rear_garage", sa.Boolean(), nullable=True),
        sa.Column("garage_size_category", sa.String(16), nullable=True),
        sa.Column("has_bunk_beds", sa.Boolean(), nullable=True),
        sa.Column("has_double_floor", sa.Boolean(), nullable=True),
        sa.Column("bathroom_type", sa.String(64), nullable=True),
        sa.Column("heating_type", sa.String(64), nullable=True),
        sa.Column("air_conditioning", sa.Boolean(), nullable=True),
        sa.Column("solar_panel", sa.Boolean(), nullable=True),
        sa.Column("tow_bar", sa.Boolean(), nullable=True),
        sa.Column("seller_name", sa.String(255), nullable=True),
        sa.Column("seller_type", sa.String(32), nullable=True),
        sa.Column("address_raw", sa.String(512), nullable=True),
        sa.Column("city", sa.String(128), nullable=True),
        sa.Column("province", sa.String(128), nullable=True),
        sa.Column("region", sa.String(128), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("description_raw", sa.Text(), nullable=True),
        sa.Column("images", postgresql.JSONB(), nullable=True),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("status", sa.String(16), nullable=False, server_default=sa.text("'active'")),
        sa.Column("extraction_confidence", sa.Float(), nullable=True),
        sa.Column("enrichment_confidence", sa.Float(), nullable=True),
        sa.Column("raw_data", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_listings_source_id", "listings", ["source_id"])
    op.create_index("ix_listings_status", "listings", ["status"])
    op.create_index("ix_listings_region", "listings", ["region"])
    op.create_index("ix_listings_brand", "listings", ["brand"])
    op.create_index("ix_listings_year", "listings", ["year"])
    op.create_index("ix_listings_price", "listings", ["price"])

    op.create_table(
        "feature_definitions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("key", sa.String(128), nullable=False, unique=True),
        sa.Column("label", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_feature_definitions_key", "feature_definitions", ["key"], unique=True)

    op.create_table(
        "listing_features",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("listing_id", sa.Integer(), sa.ForeignKey("listings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("feature_key", sa.String(128), nullable=False),
        sa.Column("value", sa.String(255), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
    )
    op.create_index("ix_listing_features_listing_id", "listing_features", ["listing_id"])
    op.create_index("ix_listing_features_feature_key", "listing_features", ["feature_key"])

    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id", ondelete="SET NULL"), nullable=True),
        sa.Column("run_type", sa.String(32), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("total_found", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_imported", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_skipped", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_errors", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "extraction_errors",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ingestion_run_id", sa.Integer(), sa.ForeignKey("ingestion_runs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source_url", sa.String(2048), nullable=True),
        sa.Column("error_type", sa.String(64), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("raw_data", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("extraction_errors")
    op.drop_table("ingestion_runs")
    op.drop_index("ix_listing_features_feature_key", "listing_features")
    op.drop_index("ix_listing_features_listing_id", "listing_features")
    op.drop_table("listing_features")
    op.drop_index("ix_feature_definitions_key", "feature_definitions")
    op.drop_table("feature_definitions")
    op.drop_index("ix_listings_price", "listings")
    op.drop_index("ix_listings_year", "listings")
    op.drop_index("ix_listings_brand", "listings")
    op.drop_index("ix_listings_region", "listings")
    op.drop_index("ix_listings_status", "listings")
    op.drop_index("ix_listings_source_id", "listings")
    op.drop_table("listings")
    op.drop_table("sources")
