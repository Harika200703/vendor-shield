from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


# ============================================================
# VENDORS
# ============================================================

class Vendor(Base):
    __tablename__ = "vendors"

    vendor_id = Column(
        String,
        primary_key=True,
        index=True
    )

    legal_name = Column(
        String,
        nullable=False
    )

    normalized_name = Column(
        String,
        nullable=False,
        index=True
    )

    gstin = Column(
        String,
        nullable=True,
        index=True
    )

    pan = Column(
        String,
        nullable=True,
        index=True
    )

    bank_account = Column(
        String,
        nullable=False,
        index=True
    )

    bank_account_masked = Column(
        String,
        nullable=True
    )

    bank_ifsc = Column(
        String,
        nullable=True
    )

    phone = Column(
        String,
        nullable=True
    )

    email = Column(
        String,
        nullable=True
    )

    address = Column(
        Text,
        nullable=True
    )

    normalized_address = Column(
        Text,
        nullable=True,
        index=True
    )

    status = Column(
        String,
        nullable=False,
        default="ACTIVE"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    transactions = relationship(
        "Transaction",
        back_populates="vendor"
    )

    changes = relationship(
        "VendorChange",
        back_populates="vendor"
    )

    risk_events = relationship(
        "RiskEvent",
        back_populates="vendor"
    )


# ============================================================
# EMPLOYEES
# ============================================================

class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(
        String,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        nullable=False
    )

    role = Column(
        String,
        nullable=False
    )

    approved_transactions = relationship(
        "Transaction",
        foreign_keys="Transaction.approved_by",
        back_populates="approver"
    )

    initiated_transactions = relationship(
        "Transaction",
        foreign_keys="Transaction.initiated_by",
        back_populates="initiator"
    )

    vendor_changes = relationship(
        "VendorChange",
        back_populates="changed_by_employee"
    )

    approvals = relationship(
        "Approval",
        back_populates="actor"
    )


# ============================================================
# TRANSACTIONS
# ============================================================

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(
        String,
        primary_key=True,
        index=True
    )

    vendor_id = Column(
        String,
        ForeignKey("vendors.vendor_id"),
        nullable=False,
        index=True
    )

    amount = Column(
        Float,
        nullable=False
    )

    invoice_no = Column(
        String,
        nullable=False
    )

    transaction_date = Column(
        DateTime,
        nullable=False
    )

    status = Column(
        String,
        nullable=False,
        default="PENDING"
    )

    approved_by = Column(
        String,
        ForeignKey("employees.employee_id"),
        nullable=True
    )

    initiated_by = Column(
        String,
        ForeignKey("employees.employee_id"),
        nullable=True
    )

    vendor = relationship(
        "Vendor",
        back_populates="transactions"
    )

    approver = relationship(
        "Employee",
        foreign_keys=[approved_by],
        back_populates="approved_transactions"
    )

    initiator = relationship(
        "Employee",
        foreign_keys=[initiated_by],
        back_populates="initiated_transactions"
    )

    approvals = relationship(
        "Approval",
        back_populates="transaction"
    )


# ============================================================
# VENDOR CHANGES
# ============================================================

class VendorChange(Base):
    __tablename__ = "vendor_changes"

    change_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    vendor_id = Column(
        String,
        ForeignKey("vendors.vendor_id"),
        nullable=False,
        index=True
    )

    field_changed = Column(
        String,
        nullable=False
    )

    old_value = Column(
        Text,
        nullable=True
    )

    new_value = Column(
        Text,
        nullable=True
    )

    changed_at = Column(
        DateTime,
        nullable=False
    )

    changed_by = Column(
        String,
        ForeignKey("employees.employee_id"),
        nullable=True
    )

    vendor = relationship(
        "Vendor",
        back_populates="changes"
    )

    changed_by_employee = relationship(
        "Employee",
        back_populates="vendor_changes"
    )


# ============================================================
# VENDOR RELATIONSHIPS
# ============================================================

class VendorRelationship(Base):
    __tablename__ = "relationships"

    relationship_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    vendor_a_id = Column(
        String,
        ForeignKey("vendors.vendor_id"),
        nullable=False,
        index=True
    )

    vendor_b_id = Column(
        String,
        ForeignKey("vendors.vendor_id"),
        nullable=False,
        index=True
    )

    relationship_type = Column(
        String,
        nullable=False
    )

    confidence = Column(
        Float,
        nullable=False
    )

    evidence = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ============================================================
# RISK EVENTS
# ============================================================

class RiskEvent(Base):
    __tablename__ = "risk_events"

    risk_event_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    vendor_id = Column(
        String,
        ForeignKey("vendors.vendor_id"),
        nullable=False,
        index=True
    )

    signal_type = Column(
        String,
        nullable=False
    )

    severity = Column(
        String,
        nullable=False
    )

    score_contribution = Column(
        Integer,
        nullable=False
    )

    evidence = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    vendor = relationship(
        "Vendor",
        back_populates="risk_events"
    )


# ============================================================
# APPROVALS
# ============================================================

class Approval(Base):
    __tablename__ = "approvals"

    approval_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    transaction_id = Column(
        String,
        ForeignKey("transactions.transaction_id"),
        nullable=False,
        index=True
    )

    action = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        nullable=False
    )

    actor_id = Column(
        String,
        ForeignKey("employees.employee_id"),
        nullable=False
    )

    reason = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    transaction = relationship(
        "Transaction",
        back_populates="approvals"
    )

    actor = relationship(
        "Employee",
        back_populates="approvals"
    )


# ============================================================
# AUDIT LOGS
# ============================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"

    audit_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    actor = Column(
        String,
        nullable=False
    )

    action = Column(
        String,
        nullable=False
    )

    entity_type = Column(
        String,
        nullable=False
    )

    entity_id = Column(
        String,
        nullable=False
    )

    details = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
# ============================================================
# NOVA INVOICES
# ============================================================

class NovaInvoice(Base):
    __tablename__ = "nova_invoices"

    id = Column(String, primary_key=True, index=True)
    invoice_number = Column(String, nullable=True, index=True)
    client_id = Column(String, nullable=True, index=True)
    client_name = Column(String, nullable=True)
    client_gst_number = Column(String, nullable=True, index=True)

    amount = Column(Float, nullable=True)
    gst_amount = Column(Float, nullable=True)
    cgst_amount = Column(Float, nullable=True)
    sgst_amount = Column(Float, nullable=True)
    igst_amount = Column(Float, nullable=True)
    total_amount = Column(Float, nullable=True)

    paid_amount = Column(Float, nullable=True)
    balance_due = Column(Float, nullable=True)

    status = Column(String, nullable=True, index=True)
    invoice_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)

    currency = Column(String, nullable=True)
    business_unit_id = Column(String, nullable=True)
    sales_rep_id = Column(String, nullable=True)
    discount_amount = Column(Float, nullable=True)

    created_at = Column(DateTime, nullable=True)


# ============================================================
# NOVA VENDOR BANK ACCOUNTS
# ============================================================

class NovaVendorBankAccount(Base):
    __tablename__ = "nova_vendor_bank_accounts"

    id = Column(String, primary_key=True, index=True)

    vendor_id = Column(
        String,
        nullable=False,
        index=True
    )

    ifsc = Column(String, nullable=True, index=True)
    account_last4 = Column(String, nullable=True)
    account_fingerprint = Column(
        String,
        nullable=True,
        index=True
    )

    holder_name = Column(String, nullable=True)

    valid_from = Column(DateTime, nullable=True)
    valid_to = Column(DateTime, nullable=True)

    verified = Column(Integer, nullable=True)


# ============================================================
# NOVA VENDOR PAYMENTS
# ============================================================

class NovaVendorPayment(Base):
    __tablename__ = "nova_vendor_payments"

    id = Column(String, primary_key=True, index=True)

    payment_number = Column(
        String,
        nullable=True,
        index=True
    )

    vendor_id = Column(
        String,
        nullable=False,
        index=True
    )

    beneficiary_account_id = Column(
        String,
        nullable=True,
        index=True
    )

    from_account_id = Column(
        String,
        nullable=True,
        index=True
    )

    amount = Column(Float, nullable=True)

    channel = Column(String, nullable=True)
    initiated_by = Column(String, nullable=True, index=True)
    approved_by = Column(String, nullable=True, index=True)

    initiated_at = Column(DateTime, nullable=True)

    status = Column(
        String,
        nullable=True,
        index=True
    )

    bank_transaction_id = Column(
        String,
        nullable=True,
        index=True
    )

    bill_ids = Column(Text, nullable=True)


# ============================================================
# NOVA MASTER DATA CHANGES
# ============================================================

class NovaMasterDataChange(Base):
    __tablename__ = "nova_master_data_changes"

    id = Column(String, primary_key=True, index=True)

    entity_type = Column(
        String,
        nullable=True,
        index=True
    )

    entity_id = Column(
        String,
        nullable=True,
        index=True
    )

    field = Column(String, nullable=True)

    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)

    changed_by = Column(
        String,
        nullable=True,
        index=True
    )

    changed_at = Column(DateTime, nullable=True)

    approved_by = Column(
        String,
        nullable=True,
        index=True
    )


# ============================================================
# NOVA APPROVALS
# ============================================================

class NovaApproval(Base):
    __tablename__ = "nova_approvals"

    id = Column(String, primary_key=True, index=True)

    doc_type = Column(
        String,
        nullable=True,
        index=True
    )

    doc_id = Column(
        String,
        nullable=True,
        index=True
    )

    level = Column(Integer, nullable=True)

    action = Column(String, nullable=True)

    actor_id = Column(
        String,
        nullable=True,
        index=True
    )

    acted_at = Column(DateTime, nullable=True)

    threshold_applied = Column(Float, nullable=True)    