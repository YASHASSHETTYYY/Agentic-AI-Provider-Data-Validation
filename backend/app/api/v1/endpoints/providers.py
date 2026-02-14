from __future__ import annotations

import csv
import io

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud.provider import (
    create_provider_batch,
    get_provider,
    list_providers,
    revalidate_all_for_owner,
    revalidate_provider,
    summary,
)
from app.db.session import get_db
from app.models.provider import RiskLevel
from app.models.user import User
from app.schemas.provider import (
    BatchValidationResult,
    ImportResult,
    ProviderListResponse,
    ProviderRead,
    ProviderSummary,
)

router = APIRouter(prefix="/providers", tags=["providers"])

REQUIRED_COLUMNS = {"provider_name", "specialty", "npi", "phone", "address"}


def _parse_csv(content: bytes) -> list[dict[str, str]]:
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    if not reader.fieldnames:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="CSV has no headers.")

    normalized_headers = {header.strip().lower() for header in reader.fieldnames}
    missing = REQUIRED_COLUMNS - normalized_headers
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"CSV is missing required columns: {missing_list}.",
        )

    rows: list[dict[str, str]] = []
    for row in reader:
        normalized_row = {key.strip().lower(): (value or "").strip() for key, value in row.items() if key}
        rows.append(
            {
                "provider_name": normalized_row.get("provider_name", ""),
                "specialty": normalized_row.get("specialty", ""),
                "npi": normalized_row.get("npi", ""),
                "phone": normalized_row.get("phone", ""),
                "address": normalized_row.get("address", ""),
            }
        )
    return rows


@router.post("/import-csv", response_model=ImportResult, status_code=status.HTTP_201_CREATED)
async def import_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ImportResult:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload a CSV file.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

    rows = _parse_csv(content)
    records = create_provider_batch(
        db, owner_id=current_user.id, rows=rows, source_file=file.filename
    )
    return ImportResult(imported=len(records), source_file=file.filename)


@router.get("", response_model=ProviderListResponse)
def list_all(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    risk_level: RiskLevel | None = Query(None),
    min_confidence: float | None = Query(None, ge=0.0, le=1.0),
    search: str | None = Query(None, max_length=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProviderListResponse:
    items, total = list_providers(
        db=db,
        owner_id=current_user.id,
        page=page,
        page_size=page_size,
        risk_level=risk_level,
        min_confidence=min_confidence,
        search=search,
    )
    return ProviderListResponse(
        items=[ProviderRead.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/summary", response_model=ProviderSummary)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProviderSummary:
    result = summary(db, owner_id=current_user.id)
    return ProviderSummary(**result)


@router.post("/validate-all", response_model=BatchValidationResult)
def validate_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BatchValidationResult:
    processed = revalidate_all_for_owner(db, owner_id=current_user.id)
    return BatchValidationResult(processed=processed)


@router.get("/export/csv")
def export_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    items, _ = list_providers(
        db=db,
        owner_id=current_user.id,
        page=1,
        page_size=10000,
        risk_level=None,
        min_confidence=None,
        search=None,
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "provider_name",
            "specialty",
            "npi",
            "phone",
            "address",
            "risk_level",
            "validation_status",
            "confidence_score",
            "primary_issue",
        ]
    )
    for item in items:
        writer.writerow(
            [
                item.provider_name,
                item.specialty or "",
                item.npi or "",
                item.phone or "",
                item.address or "",
                item.risk_level.value,
                item.validation_status.value,
                f"{item.confidence_score:.2f}",
                item.primary_issue or "",
            ]
        )

    headers = {"Content-Disposition": 'attachment; filename="validated_providers.csv"'}
    return Response(content=output.getvalue(), media_type="text/csv", headers=headers)


@router.get("/{provider_id}", response_model=ProviderRead)
def get_one(
    provider_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProviderRead:
    provider = get_provider(db, provider_id=provider_id, owner_id=current_user.id)
    if not provider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found.")
    return ProviderRead.model_validate(provider)


@router.post("/{provider_id}/validate", response_model=ProviderRead)
def validate_one(
    provider_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProviderRead:
    provider = get_provider(db, provider_id=provider_id, owner_id=current_user.id)
    if not provider:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found.")
    provider = revalidate_provider(db, provider=provider)
    return ProviderRead.model_validate(provider)
