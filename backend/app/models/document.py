from typing import List, Optional
from sqlalchemy import String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(50), default="STANDARD")  # STANDARD, QCO, MANUAL, GAZETTE
    file_hash_sha256: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    standards: Mapped[List["Standard"]] = relationship("Standard", back_populates="document")
    citations: Mapped[List["Citation"]] = relationship("Citation", back_populates="document")
