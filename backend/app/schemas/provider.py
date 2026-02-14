from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.provider import RiskLevel, ValidationStatus


class ProviderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    provider_name: str
    specialty: str | None = None
    npi: str | None = None
    phone: str | None = None
    address: str | None = None
    risk_level: RiskLevel
    validation_status: ValidationStatus
    confidence_score: float = Field(ge=0.0, le=1.0)
    primary_issue: str | None = None
    source_file: str | None = None
    created_at: datetime
    updated_at: datetime


class ProviderListResponse(BaseModel):
    items: list[ProviderRead]
    total: int
    page: int
    page_size: int


class ProviderSummary(BaseModel):
    total_providers: int
    high_risk_count: int
    medium_risk_count: int
    avg_confidence: float = Field(ge=0.0, le=1.0)
    requires_review: int


class ImportResult(BaseModel):
    imported: int
    source_file: str


class BatchValidationResult(BaseModel):
    processed: int
