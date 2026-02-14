from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import DateTime, Enum as SAEnum, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class ValidationStatus(str, Enum):
    PENDING = "Pending"
    VALIDATED = "Validated"
    REVIEW = "Needs Review"


class ProviderRecord(Base):
    __tablename__ = "provider_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    provider_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    specialty: Mapped[str | None] = mapped_column(String(120), nullable=True)
    npi: Mapped[str | None] = mapped_column(String(32), index=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)

    risk_level: Mapped[RiskLevel] = mapped_column(
        SAEnum(RiskLevel), default=RiskLevel.LOW, nullable=False
    )
    validation_status: Mapped[ValidationStatus] = mapped_column(
        SAEnum(ValidationStatus), default=ValidationStatus.PENDING, nullable=False
    )
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    primary_issue: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_file: Mapped[str | None] = mapped_column(String(255), nullable=True)

    owner_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    owner = relationship("User", back_populates="providers")
