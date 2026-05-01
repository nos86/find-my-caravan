from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, MappedColumn, mapped_column


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""

    # Subclasses may override; only listed here so IDEs know the attribute exists.
    __abstract__ = True


class TimestampMixin:
    """Adds server-side created_at / updated_at columns."""

    created_at: MappedColumn[datetime] = mapped_column(
        default=_utcnow,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: MappedColumn[datetime] = mapped_column(
        default=_utcnow,
        server_default=func.now(),
        onupdate=_utcnow,
        nullable=False,
    )
