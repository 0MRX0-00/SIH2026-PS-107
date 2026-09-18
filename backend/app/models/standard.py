import uuid
from typing import List, Optional
from sqlalchemy import String, Text, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Standard(Base, TimestampMixin):
    __tablename__ = "standards"

    document_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    standard_number: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False) # e.g. "IS 1293:2019"
    title: Mapped[str] = mapped_column(Text, nullable=False)
    division: Mapped[str] = mapped_column(String(100), index=True, nullable=False) # e.g. "Electrotechnical"
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE") # ACTIVE, UNDER_REVISION, WITHDRAWN
    is_qco_mandatory: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    qco_order_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    scope_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    document: Mapped[Optional["Document"]] = relationship("Document", back_populates="standards")
    sections: Mapped[List["StandardSection"]] = relationship("StandardSection", back_populates="standard", cascade="all, delete-orphan")
    citations: Mapped[List["Citation"]] = relationship("Citation", back_populates="standard")


class StandardSection(Base, TimestampMixin):
    __tablename__ = "standard_sections"

    standard_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("standards.id", ondelete="CASCADE"), nullable=False)
    clause_number: Mapped[str] = mapped_column(String(50), index=True, nullable=False) # e.g. "4.1", "Annex A"
    clause_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    standard: Mapped["Standard"] = relationship("Standard", back_populates="sections")
    citations: Mapped[List["Citation"]] = relationship("Citation", back_populates="section")
