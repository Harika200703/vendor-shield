from pydantic import BaseModel


class UploadResponse(BaseModel):
    message: str
    vendors_loaded: int
    transactions_loaded: int
    changes_loaded: int
    employees_loaded: int