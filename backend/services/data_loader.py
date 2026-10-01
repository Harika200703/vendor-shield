from pathlib import Path
from typing import Dict

import pandas as pd
from sqlalchemy.orm import Session

from backend.models import (
    Vendor,
    Employee,
    Transaction,
    VendorChange,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"


# ============================================================
# REQUIRED CSV COLUMNS
# ============================================================

REQUIRED_COLUMNS = {
    "vendors": [
        "vendor_id",
        "legal_name",
        "normalized_name",
        "gstin",
        "pan",
        "bank_account",
        "bank_account_masked",
        "bank_ifsc",
        "phone",
        "email",
        "address",
        "normalized_address",
        "status",
        "created_at",
    ],
    "employees": [
        "employee_id",
        "name",
        "email",
        "role",
    ],
    "transactions": [
        "transaction_id",
        "vendor_id",
        "amount",
        "invoice_no",
        "transaction_date",
        "status",
        "approved_by",
        "initiated_by",
    ],
    "vendor_changes": [
        "change_id",
        "vendor_id",
        "field_changed",
        "old_value",
        "new_value",
        "changed_at",
        "changed_by",
    ],
}


# ============================================================
# BASIC CLEANING HELPERS
# ============================================================

def clean_string(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    if value == "":
        return None

    return value


def normalize_name(name):
    if not name:
        return None

    return (
        str(name)
        .upper()
        .replace(".", "")
        .replace(",", "")
        .replace("-", "")
        .replace(" ", "")
    )


def normalize_address(address):
    if not address:
        return None

    return (
        str(address)
        .upper()
        .replace(",", "")
        .replace(".", "")
        .replace("-", "")
        .replace(" ", "")
    )


# ============================================================
# VALIDATION HELPERS
# ============================================================

def validate_columns(df, dataset_name):

    required = set(
        REQUIRED_COLUMNS[dataset_name]
    )

    actual = set(df.columns)

    missing = required - actual

    if missing:
        raise ValueError(
            f"{dataset_name}.csv is missing required "
            f"columns: {sorted(missing)}"
        )


def validate_unique_ids(
    df,
    column,
    dataset_name
):

    if df[column].duplicated().any():

        duplicates = (
            df.loc[
                df[column].duplicated(),
                column
            ]
            .astype(str)
            .tolist()
        )

        raise ValueError(
            f"{dataset_name}.csv contains duplicate "
            f"{column} values: {duplicates[:10]}"
        )


# ============================================================
# READ CSV FILES
# ============================================================

def read_csv_files(
    data_dir: Path = DATA_DIR
):

    vendors_path = data_dir / "vendors.csv"
    employees_path = data_dir / "employees.csv"
    transactions_path = data_dir / "transactions.csv"
    changes_path = data_dir / "vendor_changes.csv"

    required_files = [
        vendors_path,
        employees_path,
        transactions_path,
        changes_path,
    ]

    missing_files = [
        path.name
        for path in required_files
        if not path.exists()
    ]

    if missing_files:
        raise FileNotFoundError(
            "Missing required CSV files: "
            + ", ".join(missing_files)
        )

    # Keep IDs and financial identifiers as strings.
    vendors_df = pd.read_csv(
        vendors_path,
        dtype={
            "vendor_id": str,
            "gstin": str,
            "pan": str,
            "bank_account": str,
            "bank_account_masked": str,
            "bank_ifsc": str,
            "phone": str,
            "email": str,
        },
    )

    employees_df = pd.read_csv(
        employees_path,
        dtype=str,
    )

    transactions_df = pd.read_csv(
        transactions_path,
        dtype={
            "transaction_id": str,
            "vendor_id": str,
            "invoice_no": str,
            "approved_by": str,
            "initiated_by": str,
        },
    )

    changes_df = pd.read_csv(
        changes_path,
        dtype={
            "change_id": str,
            "vendor_id": str,
            "changed_by": str,
        },
    )

    return (
        vendors_df,
        employees_df,
        transactions_df,
        changes_df,
    )


# ============================================================
# VALIDATE DATA
# ============================================================

def validate_dataframes(
    vendors_df,
    employees_df,
    transactions_df,
    changes_df,
):

    validate_columns(
        vendors_df,
        "vendors"
    )

    validate_columns(
        employees_df,
        "employees"
    )

    validate_columns(
        transactions_df,
        "transactions"
    )

    validate_columns(
        changes_df,
        "vendor_changes"
    )

    validate_unique_ids(
        vendors_df,
        "vendor_id",
        "vendors"
    )

    validate_unique_ids(
        employees_df,
        "employee_id",
        "employees"
    )

    validate_unique_ids(
        transactions_df,
        "transaction_id",
        "transactions"
    )

    validate_unique_ids(
        changes_df,
        "change_id",
        "vendor_changes"
    )

    # --------------------------------------------------------
    # Vendor references
    # --------------------------------------------------------

    vendor_ids = set(
        vendors_df["vendor_id"]
        .dropna()
        .astype(str)
    )

    transaction_vendor_ids = set(
        transactions_df["vendor_id"]
        .dropna()
        .astype(str)
    )

    missing_transaction_vendors = (
        transaction_vendor_ids - vendor_ids
    )

    if missing_transaction_vendors:
        raise ValueError(
            "transactions.csv contains vendor IDs "
            "that do not exist in vendors.csv: "
            f"{sorted(missing_transaction_vendors)[:10]}"
        )

    change_vendor_ids = set(
        changes_df["vendor_id"]
        .dropna()
        .astype(str)
    )

    missing_change_vendors = (
        change_vendor_ids - vendor_ids
    )

    if missing_change_vendors:
        raise ValueError(
            "vendor_changes.csv contains vendor IDs "
            "that do not exist in vendors.csv: "
            f"{sorted(missing_change_vendors)[:10]}"
        )

    # --------------------------------------------------------
    # Employee references
    # --------------------------------------------------------

    employee_ids = set(
        employees_df["employee_id"]
        .dropna()
        .astype(str)
    )

    initiated_by_ids = set(
        transactions_df["initiated_by"]
        .dropna()
        .astype(str)
    )

    missing_initiators = (
        initiated_by_ids - employee_ids
    )

    if missing_initiators:
        raise ValueError(
            "transactions.csv contains initiated_by "
            "employee IDs that do not exist: "
            f"{sorted(missing_initiators)[:10]}"
        )

    approved_by_ids = set(
        transactions_df["approved_by"]
        .dropna()
        .astype(str)
    )

    missing_approvers = (
        approved_by_ids - employee_ids
    )

    if missing_approvers:
        raise ValueError(
            "transactions.csv contains approved_by "
            "employee IDs that do not exist: "
            f"{sorted(missing_approvers)[:10]}"
        )

    changed_by_ids = set(
        changes_df["changed_by"]
        .dropna()
        .astype(str)
    )

    missing_change_employees = (
        changed_by_ids - employee_ids
    )

    if missing_change_employees:
        raise ValueError(
            "vendor_changes.csv contains changed_by "
            "employee IDs that do not exist: "
            f"{sorted(missing_change_employees)[:10]}"
        )

    # --------------------------------------------------------
    # Amount validation
    # --------------------------------------------------------

    amounts = pd.to_numeric(
        transactions_df["amount"],
        errors="coerce"
    )

    if amounts.isna().any():
        raise ValueError(
            "transactions.csv contains invalid "
            "transaction amounts."
        )

    if (amounts < 0).any():
        raise ValueError(
            "transactions.csv contains negative amounts."
        )


# ============================================================
# CLEAN EMPLOYEES
# ============================================================

def clean_employees(df):

    for column in [
        "employee_id",
        "name",
        "email",
        "role",
    ]:
        df[column] = df[column].apply(
            clean_string
        )

    return df


# ============================================================
# CLEAN VENDORS
# ============================================================

def clean_vendors(df):

    for column in [
        "vendor_id",
        "legal_name",
        "gstin",
        "pan",
        "bank_account",
        "bank_account_masked",
        "bank_ifsc",
        "phone",
        "email",
        "address",
        "status",
    ]:
        df[column] = df[column].apply(
            clean_string
        )

    # Recalculate normalized fields.
    df["normalized_name"] = (
        df["legal_name"]
        .apply(normalize_name)
    )

    df["normalized_address"] = (
        df["address"]
        .apply(normalize_address)
    )

    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce"
    )

    if df["created_at"].isna().any():
        raise ValueError(
            "vendors.csv contains invalid created_at dates."
        )

    return df


# ============================================================
# CLEAN TRANSACTIONS
# ============================================================

def clean_transactions(df):

    for column in [
        "transaction_id",
        "vendor_id",
        "invoice_no",
        "status",
        "approved_by",
        "initiated_by",
    ]:
        df[column] = df[column].apply(
            clean_string
        )

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    )

    if df["amount"].isna().any():
        raise ValueError(
            "transactions.csv contains invalid "
            "transaction amounts."
        )

    if (df["amount"] < 0).any():
        raise ValueError(
            "transactions.csv contains negative amounts."
        )

    # Supports both:
    # 2026-09-11 14:30:00
    # 2025-12-06

    df["transaction_date"] = pd.to_datetime(
    df["transaction_date"].astype(str).str.strip(),
    format="mixed",
    errors="coerce"
)

    if df["transaction_date"].isna().any():

        raise ValueError(
            "transactions.csv contains invalid "
            "transaction_date values."
        )

    return df


# ============================================================
# CLEAN VENDOR CHANGES
# ============================================================

def clean_vendor_changes(df):

    for column in [
        "vendor_id",
        "field_changed",
        "old_value",
        "new_value",
        "changed_by",
    ]:
        df[column] = df[column].apply(
            clean_string
        )

    df["change_id"] = pd.to_numeric(
        df["change_id"],
        errors="coerce"
    )

    if df["change_id"].isna().any():
        raise ValueError(
            "vendor_changes.csv contains invalid change_id values."
        )

    df["change_id"] = (
        df["change_id"]
        .astype(int)
    )

    df["changed_at"] = pd.to_datetime(
        df["changed_at"].astype(str).str.strip(),
        errors="coerce"
    )

    if df["changed_at"].isna().any():
        raise ValueError(
            "vendor_changes.csv contains invalid changed_at dates."
        )

    return df


# ============================================================
# LOAD INTO DATABASE
# ============================================================

def load_data_to_database(
    db: Session,
    vendors_df,
    employees_df,
    transactions_df,
    changes_df,
):

    # --------------------------------------------------------
    # Clear old demo data.
    # Child tables first.
    # --------------------------------------------------------

    db.query(VendorChange).delete(
        synchronize_session=False
    )

    db.query(Transaction).delete(
        synchronize_session=False
    )

    db.query(Vendor).delete(
        synchronize_session=False
    )

    db.query(Employee).delete(
        synchronize_session=False
    )

    # --------------------------------------------------------
    # Employees
    # --------------------------------------------------------

    employee_objects = []

    for row in employees_df.to_dict(
        orient="records"
    ):

        employee_objects.append(
            Employee(
                employee_id=row["employee_id"],
                name=row["name"],
                email=row["email"],
                role=row["role"],
            )
        )

    db.add_all(employee_objects)

    # --------------------------------------------------------
    # Vendors
    # --------------------------------------------------------

    vendor_objects = []

    for row in vendors_df.to_dict(
        orient="records"
    ):

        vendor_objects.append(
            Vendor(
                vendor_id=row["vendor_id"],
                legal_name=row["legal_name"],
                normalized_name=row["normalized_name"],
                gstin=row["gstin"],
                pan=row["pan"],
                bank_account=row["bank_account"],
                bank_account_masked=row["bank_account_masked"],
                bank_ifsc=row["bank_ifsc"],
                phone=row["phone"],
                email=row["email"],
                address=row["address"],
                normalized_address=row["normalized_address"],
                status=row["status"],
                created_at=row["created_at"],
            )
        )

    db.add_all(vendor_objects)

    # --------------------------------------------------------
    # Transactions
    # --------------------------------------------------------

    transaction_objects = []

    for row in transactions_df.to_dict(
        orient="records"
    ):

        transaction_objects.append(
            Transaction(
                transaction_id=row["transaction_id"],
                vendor_id=row["vendor_id"],
                amount=float(row["amount"]),
                invoice_no=row["invoice_no"],
                transaction_date=row["transaction_date"],
                status=row["status"],
                approved_by=row["approved_by"],
                initiated_by=row["initiated_by"],
            )
        )

    db.add_all(transaction_objects)

    # --------------------------------------------------------
    # Vendor Changes
    # --------------------------------------------------------

    change_objects = []

    for row in changes_df.to_dict(
        orient="records"
    ):

        change_objects.append(
            VendorChange(
                change_id=int(row["change_id"]),
                vendor_id=row["vendor_id"],
                field_changed=row["field_changed"],
                old_value=row["old_value"],
                new_value=row["new_value"],
                changed_at=row["changed_at"],
                changed_by=row["changed_by"],
            )
        )

    db.add_all(change_objects)

    # Force SQLAlchemy to send the records to SQLite
    # before returning.

    db.flush()

    return {
        "employees_loaded": len(
            employee_objects
        ),
        "vendors_loaded": len(
            vendor_objects
        ),
        "transactions_loaded": len(
            transaction_objects
        ),
        "changes_loaded": len(
            change_objects
        ),
    }


# ============================================================
# MAIN LOADER
# ============================================================

def load_demo_data(
    db: Session,
    data_dir: Path = DATA_DIR,
) -> Dict:

    (
        vendors_df,
        employees_df,
        transactions_df,
        changes_df,
    ) = read_csv_files(data_dir)

    # Validate before modifying database.
    validate_dataframes(
        vendors_df,
        employees_df,
        transactions_df,
        changes_df,
    )

    # Clean.
    employees_df = clean_employees(
        employees_df
    )

    vendors_df = clean_vendors(
        vendors_df
    )

    transactions_df = clean_transactions(
        transactions_df
    )

    changes_df = clean_vendor_changes(
        changes_df
    )

    # Load.
    return load_data_to_database(
        db=db,
        vendors_df=vendors_df,
        employees_df=employees_df,
        transactions_df=transactions_df,
        changes_df=changes_df,
    )