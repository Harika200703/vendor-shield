from datetime import datetime, timedelta
from typing import Any, Iterable, Optional


BANK_CHANGE_WINDOW_DAYS = 7
PAYMENT_AFTER_CHANGE_DAYS = 3
REPEATED_CHANGE_WINDOW_DAYS = 30
HIGH_VALUE_PAYMENT_THRESHOLD = 500_000


def _get(obj: Any, field: str, default=None):
    """
    Read a field from either:
    - a SQLAlchemy model/object
    - a dictionary

    This keeps the risk engine easy to test and integrate.
    """
    if isinstance(obj, dict):
        return obj.get(field, default)

    return getattr(obj, field, default)


def _as_datetime(value: Any) -> Optional[datetime]:
    """
    Convert supported values to datetime.

    Accepts:
    - datetime
    - ISO datetime string
    - None
    """
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        try:
            return datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError:
            return None

    return None


def get_bank_changes(
    vendor_id: str,
    vendor_changes: Iterable[Any],
) -> list[Any]:
    """
    Return bank-account changes belonging to one vendor.
    """
    changes = []

    for change in vendor_changes:
        if (
            _get(change, "vendor_id") == vendor_id
            and str(_get(change, "field_changed", "")).lower()
            == "bank_account"
        ):
            changes.append(change)

    return changes


def bank_changed_within_days(
    vendor_id: str,
    vendor_changes: Iterable[Any],
    reference_time: Optional[datetime] = None,
    days: int = BANK_CHANGE_WINDOW_DAYS,
) -> Optional[Any]:
    """
    Return the most recent qualifying bank-account change
    if it occurred within the given number of days.
    """
    reference_time = reference_time or datetime.now()

    qualifying_changes = []

    for change in get_bank_changes(vendor_id, vendor_changes):
        changed_at = _as_datetime(
            _get(change, "changed_at")
        )

        if changed_at is None:
            continue

        delta = reference_time - changed_at

        if timedelta(0) <= delta <= timedelta(days=days):
            qualifying_changes.append(
                (changed_at, change)
            )

    if not qualifying_changes:
        return None

    qualifying_changes.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return qualifying_changes[0][1]


def find_payments_after_bank_change(
    vendor_id: str,
    vendor_changes: Iterable[Any],
    transactions: Iterable[Any],
    max_days: int = PAYMENT_AFTER_CHANGE_DAYS,
    minimum_amount: float = HIGH_VALUE_PAYMENT_THRESHOLD,
) -> list[dict]:
    """
    Detect payments above ₹5,00,000 occurring 0–3 days
    after a bank-account change.

    This implements the project's strict temporal rule.
    """
    results = []

    bank_changes = get_bank_changes(
        vendor_id,
        vendor_changes,
    )

    vendor_transactions = [
        transaction
        for transaction in transactions
        if _get(transaction, "vendor_id") == vendor_id
    ]

    for change in bank_changes:
        changed_at = _as_datetime(
            _get(change, "changed_at")
        )

        if changed_at is None:
            continue

        for transaction in vendor_transactions:
            transaction_date = _as_datetime(
                _get(transaction, "transaction_date")
            )

            if transaction_date is None:
                continue

            try:
                amount = float(
                    _get(transaction, "amount", 0) or 0
                )
            except (TypeError, ValueError):
                continue

            delta = transaction_date - changed_at

            if (
                timedelta(0)
                <= delta
                <= timedelta(days=max_days)
                and amount > minimum_amount
            ):
                results.append(
                    {
                        "change": change,
                        "transaction": transaction,
                        "days_after_change": delta.days,
                        "amount": amount,
                    }
                )

    return results


def has_repeated_bank_changes(
    vendor_id: str,
    vendor_changes: Iterable[Any],
    window_days: int = REPEATED_CHANGE_WINDOW_DAYS,
) -> list[Any]:
    """
    Detect two or more bank-account changes occurring
    inside any rolling 30-day window.

    Returns the changes participating in the first
    qualifying window. Otherwise returns [].
    """
    changes = []

    for change in get_bank_changes(
        vendor_id,
        vendor_changes,
    ):
        changed_at = _as_datetime(
            _get(change, "changed_at")
        )

        if changed_at is not None:
            changes.append(
                (changed_at, change)
            )

    changes.sort(key=lambda item: item[0])

    for i in range(len(changes)):
        start_time = changes[i][0]

        qualifying = [
            item[1]
            for item in changes[i:]
            if item[0] - start_time
            <= timedelta(days=window_days)
        ]

        if len(qualifying) >= 2:
            return qualifying

    return []