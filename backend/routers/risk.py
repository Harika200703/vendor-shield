from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.risk_engine import get_vendor_risk


router = APIRouter(
    prefix="/api/vendors",
    tags=["Risk"],
)


# ============================================================
# GET VENDOR RISK
# ============================================================

@router.get("/{vendor_id}/risk")
def get_risk(
    vendor_id: str,
    db: Session = Depends(get_db),
):
    """
    Return the explainable risk score,
    risk level, Risk DNA and evidence signals
    for a single vendor.
    """

    result = get_vendor_risk(
        session=db,
        vendor_id=vendor_id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Vendor {vendor_id} not found",
        )

    return result


# ============================================================
# GET VENDOR RISK DNA
# ============================================================

@router.get("/{vendor_id}/dna")
def get_risk_dna(
    vendor_id: str,
    db: Session = Depends(get_db),
):
    """
    Return the Vendor DNA representation used by
    the frontend investigation experience.
    """

    result = get_vendor_risk(
        session=db,
        vendor_id=vendor_id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Vendor {vendor_id} not found",
        )

    return {
        "vendor_id": result["vendor_id"],
        "vendor_name": result["vendor_name"],
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "risk_dna": result["risk_dna"],
        "signals": result["signals"],
    }