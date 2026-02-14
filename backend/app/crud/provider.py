from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models.provider import ProviderRecord, RiskLevel
from app.services.validation import evaluate_provider


def create_provider_batch(
    db: Session, owner_id: str, rows: Sequence[dict[str, str]], source_file: str
) -> list[ProviderRecord]:
    records: list[ProviderRecord] = []
    for row in rows:
        outcome = evaluate_provider(
            provider_name=row.get("provider_name", ""),
            specialty=row.get("specialty"),
            npi=row.get("npi"),
            phone=row.get("phone"),
            address=row.get("address"),
        )
        record = ProviderRecord(
            owner_id=owner_id,
            provider_name=row.get("provider_name", "Unknown Provider"),
            specialty=row.get("specialty"),
            npi=row.get("npi"),
            phone=row.get("phone"),
            address=row.get("address"),
            risk_level=outcome.risk_level,
            validation_status=outcome.validation_status,
            confidence_score=outcome.confidence_score,
            primary_issue=outcome.primary_issue,
            source_file=source_file,
        )
        records.append(record)

    db.add_all(records)
    db.commit()
    for record in records:
        db.refresh(record)
    return records


def _list_query(
    owner_id: str,
    risk_level: RiskLevel | None,
    min_confidence: float | None,
    search: str | None,
) -> Select[tuple[ProviderRecord]]:
    query = select(ProviderRecord).where(ProviderRecord.owner_id == owner_id)
    if risk_level is not None:
        query = query.where(ProviderRecord.risk_level == risk_level)
    if min_confidence is not None:
        query = query.where(ProviderRecord.confidence_score >= min_confidence)
    if search:
        needle = f"%{search.lower()}%"
        query = query.where(
            or_(
                func.lower(ProviderRecord.provider_name).like(needle),
                func.lower(func.coalesce(ProviderRecord.specialty, "")).like(needle),
                func.lower(func.coalesce(ProviderRecord.npi, "")).like(needle),
            )
        )
    return query


def list_providers(
    db: Session,
    owner_id: str,
    page: int,
    page_size: int,
    risk_level: RiskLevel | None,
    min_confidence: float | None,
    search: str | None,
) -> tuple[list[ProviderRecord], int]:
    base_query = _list_query(
        owner_id=owner_id,
        risk_level=risk_level,
        min_confidence=min_confidence,
        search=search,
    )

    count_query = select(func.count()).select_from(base_query.subquery())
    total = int(db.scalar(count_query) or 0)

    query = (
        base_query.order_by(ProviderRecord.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list(db.scalars(query).all())
    return items, total


def summary(db: Session, owner_id: str) -> dict[str, float | int]:
    total = int(
        db.scalar(select(func.count(ProviderRecord.id)).where(ProviderRecord.owner_id == owner_id))
        or 0
    )
    high_risk = int(
        db.scalar(
            select(func.count(ProviderRecord.id)).where(
                ProviderRecord.owner_id == owner_id, ProviderRecord.risk_level == RiskLevel.HIGH
            )
        )
        or 0
    )
    medium_risk = int(
        db.scalar(
            select(func.count(ProviderRecord.id)).where(
                ProviderRecord.owner_id == owner_id, ProviderRecord.risk_level == RiskLevel.MEDIUM
            )
        )
        or 0
    )
    avg_confidence = float(
        db.scalar(
            select(func.avg(ProviderRecord.confidence_score)).where(ProviderRecord.owner_id == owner_id)
        )
        or 0.0
    )
    return {
        "total_providers": total,
        "high_risk_count": high_risk,
        "medium_risk_count": medium_risk,
        "avg_confidence": avg_confidence,
        "requires_review": high_risk + medium_risk,
    }


def get_provider(db: Session, provider_id: str, owner_id: str) -> ProviderRecord | None:
    return db.scalar(
        select(ProviderRecord).where(ProviderRecord.id == provider_id, ProviderRecord.owner_id == owner_id)
    )


def revalidate_provider(db: Session, provider: ProviderRecord) -> ProviderRecord:
    outcome = evaluate_provider(
        provider_name=provider.provider_name,
        specialty=provider.specialty,
        npi=provider.npi,
        phone=provider.phone,
        address=provider.address,
    )
    provider.risk_level = outcome.risk_level
    provider.validation_status = outcome.validation_status
    provider.confidence_score = outcome.confidence_score
    provider.primary_issue = outcome.primary_issue
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider


def revalidate_all_for_owner(db: Session, owner_id: str) -> int:
    providers = db.scalars(select(ProviderRecord).where(ProviderRecord.owner_id == owner_id)).all()
    for provider in providers:
        outcome = evaluate_provider(
            provider_name=provider.provider_name,
            specialty=provider.specialty,
            npi=provider.npi,
            phone=provider.phone,
            address=provider.address,
        )
        provider.risk_level = outcome.risk_level
        provider.validation_status = outcome.validation_status
        provider.confidence_score = outcome.confidence_score
        provider.primary_issue = outcome.primary_issue
        db.add(provider)
    db.commit()
    return len(providers)
