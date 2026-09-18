from typing import Optional, Any
from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class CertificationScheme(Base, TimestampMixin):
    __tablename__ = "certification_schemes"

    scheme_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False) # e.g. "SCHEME_I_ISI"
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    applicable_sectors: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    application_procedure_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    required_documents_checklist: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    fee_structure_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
