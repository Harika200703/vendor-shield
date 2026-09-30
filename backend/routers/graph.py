from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.graph_engine import build_vendor_graph


router = APIRouter(
    prefix="/api/vendors",
    tags=["Relationship Graph"],
)


# ============================================================
# GET VENDOR RELATIONSHIP GRAPH
# ============================================================

@router.get("/{vendor_id}/relationships")
def get_vendor_relationships(
    vendor_id: str,
    db: Session = Depends(get_db),
):
    """
    Return the selected vendor's useful local relationship
    network.

    The graph contains only relevant nearby entities rather
    than the complete vendor database.
    """

    result = build_vendor_graph(
        session=db,
        vendor_id=vendor_id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Vendor {vendor_id} not found",
        )

    return result