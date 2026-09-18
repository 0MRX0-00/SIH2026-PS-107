import uuid
from typing import Optional
from sqlalchemy import String, Text, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Citation(Base, TimestampMixin):
    __tablename__ = "citations"

    message_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    standard_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("standards.id", ondelete="SET NULL"), nullable=True)
    section_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("standard_sections.id", ondelete="SET NULL"), nullable=True)
    document_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)

    # De-normalized fast lookup fields for citation cards
    standard_number: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. "IS 1293:2019"
    clause_ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # e.g. "Clause 8.1"
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    retrieved_chunk_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True) # Vector point ID
    snippet_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    message: Mapped["Message"] = relationship("Message", back_populates="citations")
    standard: Mapped[Optional["Standard"]] = relationship("Standard", back_populates="citations")
    section: Mapped[Optional["StandardSection"]] = relationship("StandardSection", back_populates="citations")
    document: Mapped[Optional["Document"]] = relationship("Document", back_populates="citations")
