from __future__ import annotations

import re
from dataclasses import dataclass

from app.models.provider import RiskLevel, ValidationStatus

NPI_REGEX = re.compile(r"^\d{10}$")


@dataclass
class ValidationOutcome:
    confidence_score: float
    risk_level: RiskLevel
    validation_status: ValidationStatus
    primary_issue: str | None


def _normalize_phone(phone: str | None) -> str:
    if not phone:
        return ""
    return "".join(char for char in phone if char.isdigit())


def evaluate_provider(
    provider_name: str,
    specialty: str | None,
    npi: str | None,
    phone: str | None,
    address: str | None,
) -> ValidationOutcome:
    score = 1.0
    issues: list[str] = []

    if not provider_name or len(provider_name.strip()) < 3:
        score -= 0.25
        issues.append("Provider name is incomplete.")

    if not specialty:
        score -= 0.05
        issues.append("Specialty is missing.")

    if not npi:
        score -= 0.25
        issues.append("NPI is missing.")
    elif not NPI_REGEX.match(npi):
        score -= 0.2
        issues.append("NPI format is invalid.")

    normalized_phone = _normalize_phone(phone)
    if not normalized_phone:
        score -= 0.1
        issues.append("Phone number is missing.")
    elif len(normalized_phone) != 10:
        score -= 0.1
        issues.append("Phone number format is invalid.")

    if not address:
        score -= 0.15
        issues.append("Address is missing.")
    elif len(address.strip()) < 8:
        score -= 0.1
        issues.append("Address appears incomplete.")

    bounded_score = max(0.0, min(1.0, score))
    risk_level = RiskLevel.LOW
    status = ValidationStatus.VALIDATED

    if len(issues) >= 3 or bounded_score < 0.65:
        risk_level = RiskLevel.HIGH
        status = ValidationStatus.REVIEW
    elif issues or bounded_score < 0.85:
        risk_level = RiskLevel.MEDIUM
        status = ValidationStatus.REVIEW

    return ValidationOutcome(
        confidence_score=bounded_score,
        risk_level=risk_level,
        validation_status=status,
        primary_issue=issues[0] if issues else None,
    )
