from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from ..models import (
    Vendor,
    Transaction,
    VendorChange,
    VendorRelationship,
    RiskEvent,
)

from .change_intelligence import (
    bank_changed_within_days,
    find_payments_after_bank_change,
    has_repeated_bank_changes,
)


# ============================================================
# RISK CONFIGURATION
# ============================================================

HIGH_VALUE_PAYMENT_THRESHOLD = 500_000
DUPLICATE_CONFIDENCE_THRESHOLD = 0.90

RISK_CAP = 100


# Risk DNA categories
SIGNAL_CATEGORY = {
    "shared_tax_id": "identity",
    "duplicate_candidate": "identity",

    "shared_bank": "banking",
    "recent_bank_change": "banking",
    "repeated_bank_changes": "banking",

    "payment_after_bank_change": "behaviour",
    "new_vendor_high_value_payment": "behaviour",

    "shared_address_phone": "relationships",
}


# ============================================================
# GENERAL HELPERS
# ============================================================

def get_risk_level(score: int) -> str:
    """
    Convert numerical risk score into the project's
    agreed risk level.
    """

    if score <= 30:
        return "LOW"

    if score <= 60:
        return "MEDIUM"

    if score <= 80:
        return "HIGH"

    return "CRITICAL"


def _clean(value: Any) -> str:
    """
    Convert a value into a safe comparison string.

    Empty and None values become an empty string so that
    missing fields are never accidentally treated as matches.
    """

    if value is None:
        return ""

    return str(value).strip()


def _mask_account(account: str) -> str:
    """
    Safely mask a bank account for evidence messages.
    """

    account = _clean(account)

    if not account:
        return "UNKNOWN"

    if len(account) <= 4:
        return f"XXXX{account}"

    return f"XXXX{account[-4:]}"


def _add_signal(
    signals: list[dict],
    signal_type: str,
    points: int,
    severity: str,
    evidence: str,
) -> None:
    """
    Add one deterministic risk signal.

    Every signal contains:
    - type
    - score contribution
    - severity
    - evidence
    """

    signals.append(
        {
            "signal_type": signal_type,
            "score_contribution": points,
            "severity": severity,
            "evidence": evidence,
        }
    )


# ============================================================
# ANALYSIS REFERENCE TIME
# ============================================================

def get_analysis_reference_time(
    transactions: list[Transaction],
    changes: list[VendorChange],
) -> datetime:
    """
    Use the latest date inside the dataset as the reference time.

    This is intentional.

    Using datetime.now() would mean that the same demo dataset
    could receive a different score tomorrow.

    Using the dataset's latest activity keeps the analysis
    deterministic and repeatable.
    """

    dates = []

    for transaction in transactions:
        if transaction.transaction_date:
            dates.append(transaction.transaction_date)

    for change in changes:
        if change.changed_at:
            dates.append(change.changed_at)

    if dates:
        return max(dates)

    return datetime.utcnow()


# ============================================================
# DATA INDEXES
# ============================================================

def _build_indexes(
    vendors: list[Vendor],
    transactions: list[Transaction],
    changes: list[VendorChange],
    relationships: list[VendorRelationship],
) -> dict:
    """
    Build in-memory indexes.

    We only have around 1,500 vendors, so this avoids repeatedly
    querying SQLite while analysing every vendor.
    """

    gstin_index = defaultdict(list)
    pan_index = defaultdict(list)
    bank_index = defaultdict(list)
    address_phone_index = defaultdict(list)

    transactions_by_vendor = defaultdict(list)
    changes_by_vendor = defaultdict(list)
    relationships_by_vendor = defaultdict(list)

    # --------------------------------------------------------
    # Vendor indexes
    # --------------------------------------------------------

    for vendor in vendors:

        gstin = _clean(vendor.gstin).upper()

        if gstin:
            gstin_index[gstin].append(vendor)

        pan = _clean(vendor.pan).upper()

        if pan:
            pan_index[pan].append(vendor)

        bank_account = _clean(vendor.bank_account)

        if bank_account:
            bank_index[bank_account].append(vendor)

        address = _clean(
            vendor.normalized_address or vendor.address
        ).lower()

        phone = _clean(vendor.phone)

        if address and phone:
            address_phone_index[
                (address, phone)
            ].append(vendor)

    # --------------------------------------------------------
    # Transaction indexes
    # --------------------------------------------------------

    for transaction in transactions:
        transactions_by_vendor[
            transaction.vendor_id
        ].append(transaction)

    # --------------------------------------------------------
    # Change indexes
    # --------------------------------------------------------

    for change in changes:
        changes_by_vendor[
            change.vendor_id
        ].append(change)

    # --------------------------------------------------------
    # Relationship indexes
    # --------------------------------------------------------

    for relationship in relationships:

        relationships_by_vendor[
            relationship.vendor_a_id
        ].append(relationship)

        relationships_by_vendor[
            relationship.vendor_b_id
        ].append(relationship)

    return {
        "gstin": gstin_index,
        "pan": pan_index,
        "bank": bank_index,
        "address_phone": address_phone_index,
        "transactions": transactions_by_vendor,
        "changes": changes_by_vendor,
        "relationships": relationships_by_vendor,
    }


# ============================================================
# RULE 1 — SHARED GSTIN / PAN
# ============================================================

def _check_shared_tax_id(
    vendor: Vendor,
    indexes: dict,
    signals: list[dict],
) -> None:

    conflicting_vendor_ids = set()
    matched_fields = []

    gstin = _clean(vendor.gstin).upper()

    if gstin:
        matches = indexes["gstin"].get(
            gstin,
            [],
        )

        other_matches = [
            item.vendor_id
            for item in matches
            if item.vendor_id != vendor.vendor_id
        ]

        if other_matches:
            conflicting_vendor_ids.update(
                other_matches
            )

            matched_fields.append("GSTIN")

    pan = _clean(vendor.pan).upper()

    if pan:
        matches = indexes["pan"].get(
            pan,
            [],
        )

        other_matches = [
            item.vendor_id
            for item in matches
            if item.vendor_id != vendor.vendor_id
        ]

        if other_matches:
            conflicting_vendor_ids.update(
                other_matches
            )

            matched_fields.append("PAN")

    if conflicting_vendor_ids:

        evidence = (
            f"{' and '.join(matched_fields)} shared with vendor(s): "
            f"{', '.join(sorted(conflicting_vendor_ids))}"
        )

        _add_signal(
            signals=signals,
            signal_type="shared_tax_id",
            points=30,
            severity="HIGH",
            evidence=evidence,
        )


# ============================================================
# RULE 2 — SHARED BANK ACCOUNT
# ============================================================

def _check_shared_bank(
    vendor: Vendor,
    indexes: dict,
    signals: list[dict],
) -> None:

    bank_account = _clean(
        vendor.bank_account
    )

    if not bank_account:
        return

    matches = indexes["bank"].get(
        bank_account,
        [],
    )

    other_vendor_ids = sorted(
        {
            item.vendor_id
            for item in matches
            if item.vendor_id != vendor.vendor_id
        }
    )

    if not other_vendor_ids:
        return

    masked = (
        vendor.bank_account_masked
        or _mask_account(bank_account)
    )

    evidence = (
        f"Bank account {masked} is shared with vendor(s): "
        f"{', '.join(other_vendor_ids)}"
    )

    _add_signal(
        signals=signals,
        signal_type="shared_bank",
        points=25,
        severity="HIGH",
        evidence=evidence,
    )


# ============================================================
# RULE 3 — HIGH CONFIDENCE DUPLICATE
# ============================================================

def _check_duplicate_candidate(
    vendor: Vendor,
    indexes: dict,
    signals: list[dict],
) -> None:

    matching_relationships = []

    for relationship in indexes[
        "relationships"
    ].get(vendor.vendor_id, []):

        if (
            relationship.relationship_type
            == "duplicate_candidate"
            and relationship.confidence
            is not None
            and relationship.confidence
            >= DUPLICATE_CONFIDENCE_THRESHOLD
        ):
            matching_relationships.append(
                relationship
            )

    if not matching_relationships:
        return

    # Highest-confidence match is used in the evidence.
    strongest = max(
        matching_relationships,
        key=lambda item: item.confidence,
    )

    if strongest.vendor_a_id == vendor.vendor_id:
        other_vendor_id = strongest.vendor_b_id
    else:
        other_vendor_id = strongest.vendor_a_id

    evidence = (
        f"Duplicate candidate {other_vendor_id} detected "
        f"with {strongest.confidence:.0%} confidence"
    )

    if strongest.evidence:
        evidence += f". {strongest.evidence}"

    _add_signal(
        signals=signals,
        signal_type="duplicate_candidate",
        points=20,
        severity="HIGH",
        evidence=evidence,
    )


# ============================================================
# RULE 4 — RECENT BANK CHANGE
# ============================================================

def _check_recent_bank_change(
    vendor: Vendor,
    vendor_changes: list[VendorChange],
    analysis_reference_time: datetime,
    signals: list[dict],
) -> None:

    recent_change = bank_changed_within_days(
        vendor_id=vendor.vendor_id,
        vendor_changes=vendor_changes,
        reference_time=analysis_reference_time,
        days=7,
    )

    if recent_change is None:
        return

    evidence = (
        "Bank account changed within the last 7 days "
        f"from {_mask_account(recent_change.old_value)} "
        f"to {_mask_account(recent_change.new_value)} "
        f"on {recent_change.changed_at:%Y-%m-%d}"
    )

    _add_signal(
        signals=signals,
        signal_type="recent_bank_change",
        points=10,
        severity="MEDIUM",
        evidence=evidence,
    )


# ============================================================
# RULE 5 — HIGH PAYMENT AFTER BANK CHANGE
# ============================================================

def _check_payment_after_bank_change(
    vendor: Vendor,
    vendor_changes: list[VendorChange],
    vendor_transactions: list[Transaction],
    signals: list[dict],
) -> None:

    matches = find_payments_after_bank_change(
        vendor_id=vendor.vendor_id,
        vendor_changes=vendor_changes,
        transactions=vendor_transactions,
        max_days=3,
        minimum_amount=HIGH_VALUE_PAYMENT_THRESHOLD,
    )

    if not matches:
        return

    # Choose the highest-value matching transaction
    # for the strongest evidence.
    strongest = max(
        matches,
        key=lambda item: item["amount"],
    )

    transaction = strongest[
        "transaction"
    ]

    change = strongest[
        "change"
    ]

    days_after = strongest[
        "days_after_change"
    ]

    evidence = (
        f"₹{transaction.amount:,.0f} payment "
        f"{transaction.transaction_id} was initiated "
        f"{days_after} day(s) after bank account changed "
        f"from {_mask_account(change.old_value)} "
        f"to {_mask_account(change.new_value)}"
    )

    _add_signal(
        signals=signals,
        signal_type="payment_after_bank_change",
        points=20,
        severity="HIGH",
        evidence=evidence,
    )


# ============================================================
# RULE 6 — SAME ADDRESS + SAME PHONE
# ============================================================

def _check_shared_address_phone(
    vendor: Vendor,
    indexes: dict,
    signals: list[dict],
) -> None:

    address = _clean(
        vendor.normalized_address
        or vendor.address
    ).lower()

    phone = _clean(vendor.phone)

    if not address or not phone:
        return

    matches = indexes[
        "address_phone"
    ].get(
        (address, phone),
        [],
    )

    other_vendor_ids = sorted(
        {
            item.vendor_id
            for item in matches
            if item.vendor_id != vendor.vendor_id
        }
    )

    if not other_vendor_ids:
        return

    evidence = (
        "Vendor shares both address and phone with vendor(s): "
        f"{', '.join(other_vendor_ids)}"
    )

    _add_signal(
        signals=signals,
        signal_type="shared_address_phone",
        points=15,
        severity="MEDIUM",
        evidence=evidence,
    )


# ============================================================
# RULE 7 — NEW VENDOR + HIGH VALUE PAYMENT
# ============================================================

def _check_new_vendor_high_value_payment(
    vendor: Vendor,
    vendor_transactions: list[Transaction],
    signals: list[dict],
) -> None:

    if vendor.created_at is None:
        return

    qualifying_transactions = []

    for transaction in vendor_transactions:

        if transaction.transaction_date is None:
            continue

        if transaction.amount is None:
            continue

        age_at_payment = (
            transaction.transaction_date
            - vendor.created_at
        )

        if (
            timedelta(0)
            <= age_at_payment
            < timedelta(days=30)
            and transaction.amount
            > HIGH_VALUE_PAYMENT_THRESHOLD
        ):
            qualifying_transactions.append(
                (
                    transaction,
                    age_at_payment.days,
                )
            )

    if not qualifying_transactions:
        return

    strongest_transaction, age_days = max(
        qualifying_transactions,
        key=lambda item: item[0].amount,
    )

    evidence = (
        f"₹{strongest_transaction.amount:,.0f} payment "
        f"{strongest_transaction.transaction_id} occurred "
        f"{age_days} day(s) after the vendor was created"
    )

    _add_signal(
        signals=signals,
        signal_type="new_vendor_high_value_payment",
        points=15,
        severity="MEDIUM",
        evidence=evidence,
    )


# ============================================================
# RULE 8 — REPEATED BANK CHANGES
# ============================================================

def _check_repeated_bank_changes(
    vendor: Vendor,
    vendor_changes: list[VendorChange],
    signals: list[dict],
) -> None:

    repeated_changes = has_repeated_bank_changes(
        vendor_id=vendor.vendor_id,
        vendor_changes=vendor_changes,
        window_days=30,
    )

    if len(repeated_changes) < 2:
        return

    dates = sorted(
        change.changed_at.strftime(
            "%Y-%m-%d"
        )
        for change in repeated_changes
        if change.changed_at
    )

    evidence = (
        f"Bank account changed {len(repeated_changes)} times "
        f"within a 30-day window"
    )

    if dates:
        evidence += (
            f" ({', '.join(dates)})"
        )

    _add_signal(
        signals=signals,
        signal_type="repeated_bank_changes",
        points=10,
        severity="MEDIUM",
        evidence=evidence,
    )


# ============================================================
# EVALUATE ONE VENDOR
# ============================================================

def evaluate_vendor_risk(
    vendor: Vendor,
    indexes: dict,
    analysis_reference_time: datetime,
) -> list[dict]:
    """
    Apply every deterministic risk rule to one vendor.
    """

    signals = []

    vendor_changes = indexes[
        "changes"
    ].get(
        vendor.vendor_id,
        [],
    )

    vendor_transactions = indexes[
        "transactions"
    ].get(
        vendor.vendor_id,
        [],
    )

    _check_shared_tax_id(
        vendor,
        indexes,
        signals,
    )

    _check_shared_bank(
        vendor,
        indexes,
        signals,
    )

    _check_duplicate_candidate(
        vendor,
        indexes,
        signals,
    )

    _check_recent_bank_change(
        vendor,
        vendor_changes,
        analysis_reference_time,
        signals,
    )

    _check_payment_after_bank_change(
        vendor,
        vendor_changes,
        vendor_transactions,
        signals,
    )

    _check_shared_address_phone(
        vendor,
        indexes,
        signals,
    )

    _check_new_vendor_high_value_payment(
        vendor,
        vendor_transactions,
        signals,
    )

    _check_repeated_bank_changes(
        vendor,
        vendor_changes,
        signals,
    )

    return signals


# ============================================================
# RISK SCORE / DNA
# ============================================================

def calculate_risk_score(
    risk_events: list[RiskEvent],
) -> int:
    """
    Sum risk contributions and cap final score at 100.
    """

    total = sum(
        event.score_contribution
        for event in risk_events
    )

    return min(
        RISK_CAP,
        max(0, total),
    )


def calculate_risk_dna(
    risk_events: list[RiskEvent],
) -> dict:
    """
    Return the explainable contribution by risk category.
    """

    dna = {
        "identity": 0,
        "banking": 0,
        "behaviour": 0,
        "relationships": 0,
    }

    for event in risk_events:

        category = SIGNAL_CATEGORY.get(
            event.signal_type
        )

        if category:
            dna[category] += (
                event.score_contribution
            )

    return dna


# ============================================================
# RUN COMPLETE RISK ANALYSIS
# ============================================================

def run_risk_analysis(
    session: Session,
) -> dict:
    """
    Run deterministic VendorTrust risk analysis.

    This function is called after:
        upload
            ->
        entity resolution
            ->
        risk analysis

    Existing risk events are cleared before regeneration,
    making the process repeatable and preventing duplicates.
    """

    vendors = session.query(
        Vendor
    ).all()

    transactions = session.query(
        Transaction
    ).all()

    changes = session.query(
        VendorChange
    ).all()

    relationships = session.query(
        VendorRelationship
    ).all()

    analysis_reference_time = (
        get_analysis_reference_time(
            transactions,
            changes,
        )
    )

    indexes = _build_indexes(
        vendors=vendors,
        transactions=transactions,
        changes=changes,
        relationships=relationships,
    )

    # --------------------------------------------------------
    # Clear previous deterministic analysis
    # --------------------------------------------------------

    session.query(
        RiskEvent
    ).delete(
        synchronize_session=False
    )

    session.flush()

    created_events = 0

    # --------------------------------------------------------
    # Analyse vendors
    # --------------------------------------------------------

    for vendor in vendors:

        signals = evaluate_vendor_risk(
            vendor=vendor,
            indexes=indexes,
            analysis_reference_time=analysis_reference_time,
        )

        for signal in signals:

            event = RiskEvent(
                vendor_id=vendor.vendor_id,
                signal_type=signal[
                    "signal_type"
                ],
                severity=signal[
                    "severity"
                ],
                score_contribution=signal[
                    "score_contribution"
                ],
                evidence=signal[
                    "evidence"
                ],
            )

            session.add(event)

            created_events += 1

    session.commit()

    return {
        "vendors_analyzed": len(vendors),
        "risk_events_created": created_events,
        "analysis_reference_time": (
            analysis_reference_time.isoformat()
        ),
    }


# ============================================================
# GET ONE VENDOR'S RISK
# ============================================================

def get_vendor_risk(
    session: Session,
    vendor_id: str,
) -> dict | None:
    """
    Return complete risk details for one vendor.
    """

    vendor = session.query(
        Vendor
    ).filter(
        Vendor.vendor_id == vendor_id
    ).first()

    if vendor is None:
        return None

    events = session.query(
        RiskEvent
    ).filter(
        RiskEvent.vendor_id == vendor_id
    ).order_by(
        RiskEvent.score_contribution.desc()
    ).all()

    risk_score = calculate_risk_score(
        events
    )

    risk_level = get_risk_level(
        risk_score
    )

    risk_dna = calculate_risk_dna(
        events
    )

    signals = [
        {
            "type": event.signal_type.upper(),
            "points": event.score_contribution,
            "severity": event.severity,
            "evidence": event.evidence,
        }
        for event in events
    ]

    return {
        "vendor_id": vendor.vendor_id,
        "vendor_name": vendor.legal_name,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_dna": risk_dna,
        "signals": signals,
    }