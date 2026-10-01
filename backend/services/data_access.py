from typing import Optional

from sqlalchemy.orm import Session

from backend.models import (
    NovaVendorBankAccount,
    NovaVendorPayment,
    NovaMasterDataChange,
    NovaApproval,
    NovaInvoice,
)


class DataAccessService:
    """
    Centralized database access layer for VendorTrust.

    Other services such as Risk Engine, Graph Engine,
    and Investigation Agent can use this class instead
    of writing SQLAlchemy queries directly.
    """

    def __init__(self, db: Session):
        self.db = db

    # --------------------------------------------------------
    # VENDOR BANK ACCOUNTS
    # --------------------------------------------------------

    def get_vendor_bank_accounts(
        self,
        vendor_id: Optional[str] = None,
    ):
        query = self.db.query(NovaVendorBankAccount)

        if vendor_id:
            query = query.filter(
                NovaVendorBankAccount.vendor_id == vendor_id
            )

        return query.all()

    # --------------------------------------------------------
    # VENDOR PAYMENTS
    # --------------------------------------------------------

    def get_vendor_payments(
        self,
        vendor_id: Optional[str] = None,
    ):
        query = self.db.query(NovaVendorPayment)

        if vendor_id:
            query = query.filter(
                NovaVendorPayment.vendor_id == vendor_id
            )

        return query.order_by(
            NovaVendorPayment.initiated_at.desc()
        ).all()

    # --------------------------------------------------------
    # MASTER DATA CHANGES
    # --------------------------------------------------------

    def get_vendor_changes(
        self,
        vendor_id: Optional[str] = None,
    ):
        query = self.db.query(NovaMasterDataChange)

        if vendor_id:
            query = query.filter(
                NovaMasterDataChange.entity_id == vendor_id
            )

        return query.order_by(
            NovaMasterDataChange.changed_at.desc()
        ).all()

    # --------------------------------------------------------
    # APPROVALS
    # --------------------------------------------------------

    def get_approvals(
        self,
        doc_id: Optional[str] = None,
    ):
        query = self.db.query(NovaApproval)

        if doc_id:
            query = query.filter(
                NovaApproval.doc_id == doc_id
            )

        return query.order_by(
            NovaApproval.acted_at.desc()
        ).all()

    # --------------------------------------------------------
    # INVOICES
    # --------------------------------------------------------

    def get_invoices(
        self,
        client_id: Optional[str] = None,
    ):
        query = self.db.query(NovaInvoice)

        if client_id:
            query = query.filter(
                NovaInvoice.client_id == client_id
            )

        return query.order_by(
            NovaInvoice.invoice_date.desc()
        ).all()

    # --------------------------------------------------------
    # PAYMENT HISTORY
    # --------------------------------------------------------

    def get_vendor_payment_history(
        self,
        vendor_id: str,
    ):
        return (
            self.db.query(NovaVendorPayment)
            .filter(
                NovaVendorPayment.vendor_id == vendor_id
            )
            .order_by(
                NovaVendorPayment.initiated_at.desc()
            )
            .all()
        )

    # --------------------------------------------------------
    # BANK ACCOUNT HISTORY
    # --------------------------------------------------------

    def get_vendor_bank_history(
        self,
        vendor_id: str,
    ):
        return (
            self.db.query(NovaVendorBankAccount)
            .filter(
                NovaVendorBankAccount.vendor_id == vendor_id
            )
            .order_by(
                NovaVendorBankAccount.valid_from.desc()
            )
            .all()
        )

    # --------------------------------------------------------
    # VENDOR INVESTIGATION DATA
    # --------------------------------------------------------

    def get_vendor_investigation_data(
        self,
        vendor_id: str,
    ):
        """
        Returns the main Nova data required to investigate
        a vendor.
        """

        return {
            "bank_accounts": self.get_vendor_bank_accounts(
                vendor_id
            ),
            "payments": self.get_vendor_payments(
                vendor_id
            ),
            "master_data_changes": self.get_vendor_changes(
                vendor_id
            ),
        }