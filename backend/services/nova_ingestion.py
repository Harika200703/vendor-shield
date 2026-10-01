import os
from datetime import datetime
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import (
    NovaInvoice,
    NovaVendorBankAccount,
    NovaVendorPayment,
    NovaMasterDataChange,
    NovaApproval,
)

load_dotenv()

BASE_URL = os.getenv("NOVA_API_BASE_URL")
API_KEY = os.getenv("NOVA_API_KEY")


class NovaAPIError(Exception):
    pass


# ============================================================
# COMMON HELPERS
# ============================================================

def fetch_all(
    resource: str,
    page_size: int = 100,
) -> List[Dict[str, Any]]:

    if not BASE_URL:
        raise ValueError("NOVA_API_BASE_URL is not configured.")

    if not API_KEY:
        raise ValueError("NOVA_API_KEY is not configured.")

    url = f"{BASE_URL}/{resource}"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json",
    }

    records = []
    offset = 0

    while True:
        response = requests.get(
            url,
            headers=headers,
            params={
                "limit": page_size,
                "offset": offset,
            },
            timeout=30,
        )

        if response.status_code != 200:
            raise NovaAPIError(
                f"{resource} failed: "
                f"{response.status_code} - "
                f"{response.text[:500]}"
            )

        payload = response.json()

        data = payload.get("data", [])
        pagination = payload.get("pagination", {})

        records.extend(data)

        print(
            f"{resource}: fetched {len(data)} "
            f"records (offset={offset})"
        )

        if not pagination.get("has_more", False):
            break

        offset += page_size

    print(
        f"{resource}: total records fetched = "
        f"{len(records)}"
    )

    return records


def parse_datetime(value):
    if not value:
        return None

    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    ).replace(tzinfo=None)


# ============================================================
# INVOICES
# ============================================================

def save_invoices(
    db: Session,
    records: List[Dict[str, Any]],
):

    inserted = 0
    updated = 0

    for record in records:

        existing = db.get(
            NovaInvoice,
            record["id"]
        )

        values = {
            "invoice_number": record.get("invoice_number"),
            "client_id": record.get("client_id"),
            "client_name": record.get("client_name"),
            "client_gst_number": record.get("client_gst_number"),
            "amount": record.get("amount"),
            "gst_amount": record.get("gst_amount"),
            "cgst_amount": record.get("cgst_amount"),
            "sgst_amount": record.get("sgst_amount"),
            "igst_amount": record.get("igst_amount"),
            "total_amount": record.get("total_amount"),
            "paid_amount": record.get("paid_amount"),
            "balance_due": record.get("balance_due"),
            "status": record.get("status"),
            "invoice_date": parse_datetime(
                record.get("invoice_date")
            ),
            "due_date": parse_datetime(
                record.get("due_date")
            ),
            "currency": record.get("currency"),
            "business_unit_id": record.get("business_unit_id"),
            "sales_rep_id": record.get("sales_rep_id"),
            "discount_amount": record.get("discount_amount"),
            "created_at": parse_datetime(
                record.get("created_at")
            ),
        }

        if existing:
            for key, value in values.items():
                setattr(existing, key, value)

            updated += 1

        else:
            invoice = NovaInvoice(
                id=record["id"],
                **values
            )

            db.add(invoice)
            inserted += 1

    db.commit()

    print(
        f"Invoices -> inserted: {inserted}, "
        f"updated: {updated}"
    )


# ============================================================
# VENDOR BANK ACCOUNTS
# ============================================================

def save_vendor_bank_accounts(
    db: Session,
    records: List[Dict[str, Any]],
):

    inserted = 0
    updated = 0

    for record in records:

        existing = db.get(
            NovaVendorBankAccount,
            record["id"]
        )

        values = {
            "vendor_id": record.get("vendor_id"),
            "ifsc": record.get("ifsc"),
            "account_last4": record.get("account_last4"),
            "account_fingerprint": record.get(
                "account_fingerprint"
            ),
            "holder_name": record.get("holder_name"),
            "valid_from": parse_datetime(
                record.get("valid_from")
            ),
            "valid_to": parse_datetime(
                record.get("valid_to")
            ),
            "verified": (
                1 if record.get("verified") else 0
            ),
        }

        if existing:

            for key, value in values.items():
                setattr(existing, key, value)

            updated += 1

        else:

            bank_account = NovaVendorBankAccount(
                id=record["id"],
                **values
            )

            db.add(bank_account)
            inserted += 1

    db.commit()

    print(
        f"Vendor bank accounts -> "
        f"inserted: {inserted}, "
        f"updated: {updated}"
    )


# ============================================================
# VENDOR PAYMENTS
# ============================================================

def save_vendor_payments(
    db: Session,
    records: List[Dict[str, Any]],
):

    inserted = 0
    updated = 0

    for record in records:

        existing = db.get(
            NovaVendorPayment,
            record["id"]
        )

        bill_ids = record.get("bill_ids", [])

        if isinstance(bill_ids, list):
            bill_ids_text = ",".join(bill_ids)
        else:
            bill_ids_text = str(bill_ids)

        values = {
            "payment_number": record.get("payment_number"),
            "vendor_id": record.get("vendor_id"),
            "beneficiary_account_id": record.get(
                "beneficiary_account_id"
            ),
            "from_account_id": record.get(
                "from_account_id"
            ),
            "amount": record.get("amount"),
            "channel": record.get("channel"),
            "initiated_by": record.get("initiated_by"),
            "approved_by": record.get("approved_by"),
            "initiated_at": parse_datetime(
                record.get("initiated_at")
            ),
            "status": record.get("status"),
            "bank_transaction_id": record.get(
                "bank_transaction_id"
            ),
            "bill_ids": bill_ids_text,
        }

        if existing:

            for key, value in values.items():
                setattr(existing, key, value)

            updated += 1

        else:

            payment = NovaVendorPayment(
                id=record["id"],
                **values
            )

            db.add(payment)
            inserted += 1

    db.commit()

    print(
        f"Vendor payments -> "
        f"inserted: {inserted}, "
        f"updated: {updated}"
    )


# ============================================================
# MASTER DATA CHANGES
# ============================================================

def save_master_data_changes(
    db: Session,
    records: List[Dict[str, Any]],
):

    inserted = 0
    updated = 0

    for record in records:

        existing = db.get(
            NovaMasterDataChange,
            record["id"]
        )

        values = {
            "entity_type": record.get("entity_type"),
            "entity_id": record.get("entity_id"),
            "field": record.get("field"),
            "old_value": record.get("old_value"),
            "new_value": record.get("new_value"),
            "changed_by": record.get("changed_by"),
            "changed_at": parse_datetime(
                record.get("changed_at")
            ),
            "approved_by": record.get("approved_by"),
        }

        if existing:

            for key, value in values.items():
                setattr(existing, key, value)

            updated += 1

        else:

            change = NovaMasterDataChange(
                id=record["id"],
                **values
            )

            db.add(change)
            inserted += 1

    db.commit()

    print(
        f"Master data changes -> "
        f"inserted: {inserted}, "
        f"updated: {updated}"
    )


# ============================================================
# APPROVALS
# ============================================================

def save_nova_approvals(
    db: Session,
    records: List[Dict[str, Any]],
):

    inserted = 0
    updated = 0

    for record in records:

        existing = db.get(
            NovaApproval,
            record["id"]
        )

        values = {
            "doc_type": record.get("doc_type"),
            "doc_id": record.get("doc_id"),
            "level": record.get("level"),
            "action": record.get("action"),
            "actor_id": record.get("actor_id"),
            "acted_at": parse_datetime(
                record.get("acted_at")
            ),
            "threshold_applied": record.get(
                "threshold_applied"
            ),
        }

        if existing:

            for key, value in values.items():
                setattr(existing, key, value)

            updated += 1

        else:

            approval = NovaApproval(
                id=record["id"],
                **values
            )

            db.add(approval)
            inserted += 1

    db.commit()

    print(
        f"Nova approvals -> "
        f"inserted: {inserted}, "
        f"updated: {updated}"
    )


# ============================================================
# MAIN INGESTION PIPELINE
# ============================================================

def ingest_all():

    db = SessionLocal()

    try:

        print("=" * 60)
        print("VendorTrust - Nova API Ingestion")
        print("=" * 60)

        # 1. Invoices
        print("\n[1/5] Fetching invoices...")
        invoices = fetch_all("invoices")
        save_invoices(db, invoices)

        # 2. Vendor bank accounts
        print("\n[2/5] Fetching vendor bank accounts...")
        bank_accounts = fetch_all(
            "vendor-bank-accounts"
        )
        save_vendor_bank_accounts(
            db,
            bank_accounts
        )

        # 3. Vendor payments
        print("\n[3/5] Fetching vendor payments...")
        payments = fetch_all(
            "vendor-payments"
        )
        save_vendor_payments(
            db,
            payments
        )

        # 4. Master data changes
        print("\n[4/5] Fetching master data changes...")
        changes = fetch_all(
            "master-data-changes"
        )
        save_master_data_changes(
            db,
            changes
        )

        # 5. Approvals
        print("\n[5/5] Fetching approvals...")
        approvals = fetch_all(
            "approvals"
        )
        save_nova_approvals(
            db,
            approvals
        )

        print("\n" + "=" * 60)
        print("NOVA INGESTION COMPLETED SUCCESSFULLY")
        print("=" * 60)

        print(
            f"Invoices: {len(invoices)}"
        )

        print(
            f"Vendor bank accounts: "
            f"{len(bank_accounts)}"
        )

        print(
            f"Vendor payments: {len(payments)}"
        )

        print(
            f"Master data changes: "
            f"{len(changes)}"
        )

        print(
            f"Approvals: {len(approvals)}"
        )

        print("=" * 60)

    except Exception as exc:

        db.rollback()

        print("\nNOVA INGESTION FAILED")
        print(str(exc))

        raise

    finally:
        db.close()


if __name__ == "__main__":
    ingest_all()