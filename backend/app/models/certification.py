from typing import Optional, Any
from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class CertificationScheme(Base, TimestampMixin):
    __tablename__ = "certification_schemes"

    scheme_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False) # e.g. "SCHEME_I_ISI_NORMAL"
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    classification: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    manufacturer_scope: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # DOMESTIC, FOREIGN, DOMESTIC_AND_FOREIGN, ORGANIZATIONS_AND_LABS
    legal_act_and_regulation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    official_reference_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_verification_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    data_confidence: Mapped[Optional[str]] = mapped_column(String(50), default="OFFICIAL_STATUTORY_VERIFIED", nullable=True)
    last_reviewed: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    applicable_sectors: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    application_procedure_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    required_documents_checklist: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    fee_structure_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

