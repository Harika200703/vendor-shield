from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import UploadResponse
from backend.services.data_loader import load_demo_data


router = APIRouter(
    prefix="/upload",
    tags=["Data Upload"],
)


@router.post(
    "",
    response_model=UploadResponse
)
def upload_demo_data(
    db: Session = Depends(get_db),
):
    """
    Load and validate the demo CSV dataset
    into the SQLite database.
    """

    try:
        counts = load_demo_data(db)

        db.commit()

        return {
            "message": "Data uploaded and validated",
            "vendors_loaded": counts[
                "vendors_loaded"
            ],
            "transactions_loaded": counts[
                "transactions_loaded"
            ],
            "changes_loaded": counts[
                "changes_loaded"
            ],
            "employees_loaded": counts[
                "employees_loaded"
            ],
        }

    except FileNotFoundError as exc:

        db.rollback()

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except ValueError as exc:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Data loading failed: {str(exc)}",
        )