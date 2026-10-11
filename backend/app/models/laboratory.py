from typing import Optional, Any
from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class Laboratory(Base, TimestampMixin):
    __tablename__ = "laboratories"

    lab_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    lab_code: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True, index=True)
    recognition_type: Mapped[str] = mapped_column(String(100), default="BIS_RECOGNIZED", index=True) # BIS_RECOGNIZED, BIS_EMPANELLED, BIS_CENTRAL, BIS_BRANCH, NABL_ACCREDITED
    city: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    district: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    state: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    contact_details: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    validity_date: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(50), default="ACTIVE", index=True) # ACTIVE, EXPIRED, SUSPENDED
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    scope_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    testing_scope_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    accredited_standards: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True) # List of IS numbers tested
    last_verified_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
