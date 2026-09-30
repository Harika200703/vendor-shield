from hashlib import sha1
from typing import Optional

import networkx as nx
from sqlalchemy.orm import Session

from ..models import (
    Vendor,
    Transaction,
    VendorChange,
    VendorRelationship,
    RiskEvent,
)

from .risk_engine import (
    calculate_risk_score,
    get_risk_level,
)


# ============================================================
# GRAPH CONFIGURATION
# ============================================================

MAX_RELATED_VENDORS = 12
MAX_TRANSACTIONS = 20


RELATIONSHIP_EDGE_LABELS = {
    "shared_bank": "SHARES_BANK",
    "shared_tax_id": "SHARES_TAX_ID",
    "shared_phone": "SHARES_PHONE",
    "shared_address": "SHARES_ADDRESS",
    "similar_identity": "SIMILAR_IDENTITY",
    "duplicate_candidate": "SIMILAR_IDENTITY",
    "shared_email": "SHARES_EMAIL",
}


# ============================================================
# GENERAL HELPERS
# ============================================================

def _clean(value) -> str:
    if value is None:
        return ""

    return str(value).strip()


def _stable_id(prefix: str, value: str) -> str:
    """
    Create a deterministic graph node ID without exposing
    raw identifiers such as full bank-account numbers.
    """

    digest = sha1(
        value.encode("utf-8")
    ).hexdigest()[:12]

    return f"{prefix}-{digest}"


def _mask_bank(account: str) -> str:
    account = _clean(account)

    if not account:
        return "Unknown bank"

    if len(account) <= 4:
        return f"XXXX{account}"

    return f"XXXX{account[-4:]}"


def _mask_pan(pan: str) -> str:
    pan = _clean(pan)

    if not pan:
        return ""

    if len(pan) <= 4:
        return pan

    return (
        pan[:2]
        + "X" * max(0, len(pan) - 6)
        + pan[-4:]
    )


def _relationship_risk(
    relationship_type: str,
    confidence: Optional[float],
) -> str:
    """
    Assign visual severity to relationship edges.

    This does NOT modify vendor risk scores.
    It only helps the graph UI highlight important links.
    """

    if relationship_type in {
        "shared_tax_id",
        "shared_bank",
    }:
        return "HIGH"

    if relationship_type == "duplicate_candidate":
        if (
            confidence is not None
            and confidence >= 0.90
        ):
            return "HIGH"

        return "MEDIUM"

    if relationship_type in {
        "shared_phone",
        "shared_address",
        "similar_identity",
        "shared_email",
    }:
        return "MEDIUM"

    return "LOW"


# ============================================================
# RISK LOOKUP
# ============================================================

def _get_vendor_risk_level(
    session: Session,
    vendor_id: str,
) -> tuple[int, str]:

    events = session.query(
        RiskEvent
    ).filter(
        RiskEvent.vendor_id == vendor_id
    ).all()

    score = calculate_risk_score(
        events
    )

    return (
        score,
        get_risk_level(score),
    )


# ============================================================
# NETWORKX HELPERS
# ============================================================

def _add_node(
    graph: nx.MultiDiGraph,
    node_id: str,
    **attributes,
) -> None:

    if node_id not in graph:
        graph.add_node(
            node_id,
            **attributes,
        )


def _add_edge(
    graph: nx.MultiDiGraph,
    source: str,
    target: str,
    label: str,
    risk: str = "LOW",
    evidence: Optional[str] = None,
) -> None:

    graph.add_edge(
        source,
        target,
        label=label,
        risk=risk,
        evidence=evidence or "",
    )


# ============================================================
# VENDOR CORE NODES
# ============================================================

def _add_vendor_node(
    graph: nx.MultiDiGraph,
    session: Session,
    vendor: Vendor,
    selected: bool = False,
) -> None:

    score, risk_level = (
        _get_vendor_risk_level(
            session,
            vendor.vendor_id,
        )
    )

    _add_node(
        graph,
        vendor.vendor_id,
        label=vendor.legal_name,
        type="vendor",
        risk=risk_level,
        risk_score=score,
        selected=selected,
        vendor_id=vendor.vendor_id,
    )


def _add_vendor_identity_nodes(
    graph: nx.MultiDiGraph,
    vendor: Vendor,
) -> None:
    """
    Add useful identity nodes directly connected
    to a vendor.
    """

    vendor_id = vendor.vendor_id

    # --------------------------------------------------------
    # Bank account
    # --------------------------------------------------------

    bank_account = _clean(
        vendor.bank_account
    )

    if bank_account:

        bank_node_id = _stable_id(
            "BANK",
            bank_account,
        )

        _add_node(
            graph,
            bank_node_id,
            label=(
                vendor.bank_account_masked
                or _mask_bank(bank_account)
            ),
            type="bank",
            risk="LOW",
        )

        _add_edge(
            graph,
            vendor_id,
            bank_node_id,
            label="SHARES_BANK",
            risk="LOW",
            evidence="Vendor bank account",
        )

    # --------------------------------------------------------
    # GSTIN
    # --------------------------------------------------------

    gstin = _clean(vendor.gstin)

    if gstin:

        gst_node_id = _stable_id(
            "GSTIN",
            gstin,
        )

        _add_node(
            graph,
            gst_node_id,
            label=gstin,
            type="tax_id",
            tax_type="GSTIN",
            risk="LOW",
        )

        _add_edge(
            graph,
            vendor_id,
            gst_node_id,
            label="SHARES_TAX_ID",
            risk="LOW",
            evidence="Vendor GSTIN",
        )

    # --------------------------------------------------------
    # PAN
    # --------------------------------------------------------

    pan = _clean(vendor.pan)

    if pan:

        pan_node_id = _stable_id(
            "PAN",
            pan,
        )

        _add_node(
            graph,
            pan_node_id,
            label=_mask_pan(pan),
            type="tax_id",
            tax_type="PAN",
            risk="LOW",
        )

        _add_edge(
            graph,
            vendor_id,
            pan_node_id,
            label="SHARES_TAX_ID",
            risk="LOW",
            evidence="Vendor PAN",
        )

    # --------------------------------------------------------
    # Address
    # --------------------------------------------------------

    address = _clean(
        vendor.address
    )

    normalized_address = _clean(
        vendor.normalized_address
    )

    address_key = (
        normalized_address
        or address
    )

    if address_key:

        address_node_id = _stable_id(
            "ADDRESS",
            address_key.lower(),
        )

        _add_node(
            graph,
            address_node_id,
            label=address,
            type="address",
            risk="LOW",
        )

        _add_edge(
            graph,
            vendor_id,
            address_node_id,
            label="SHARES_ADDRESS",
            risk="LOW",
            evidence="Vendor registered address",
        )


# ============================================================
# RELATED VENDORS
# ============================================================

def _get_local_relationships(
    session: Session,
    vendor_id: str,
) -> list[VendorRelationship]:

    relationships = session.query(
        VendorRelationship
    ).filter(
        (
            VendorRelationship.vendor_a_id
            == vendor_id
        )
        |
        (
            VendorRelationship.vendor_b_id
            == vendor_id
        )
    ).all()

    # Strongest relationships first.
    relationships.sort(
        key=lambda item: (
            item.confidence
            if item.confidence is not None
            else 0
        ),
        reverse=True,
    )

    return relationships


def _add_related_vendors(
    graph: nx.MultiDiGraph,
    session: Session,
    selected_vendor: Vendor,
) -> list[Vendor]:

    relationships = (
        _get_local_relationships(
            session,
            selected_vendor.vendor_id,
        )
    )

    related_vendor_ids = []
    selected_relationships = []

    for relationship in relationships:

        if (
            relationship.vendor_a_id
            == selected_vendor.vendor_id
        ):
            related_id = (
                relationship.vendor_b_id
            )
        else:
            related_id = (
                relationship.vendor_a_id
            )

        if related_id not in related_vendor_ids:

            if (
                len(related_vendor_ids)
                >= MAX_RELATED_VENDORS
            ):
                continue

            related_vendor_ids.append(
                related_id
            )

        selected_relationships.append(
            relationship
        )

    if not related_vendor_ids:
        return []

    related_vendors = session.query(
        Vendor
    ).filter(
        Vendor.vendor_id.in_(
            related_vendor_ids
        )
    ).all()

    vendors_by_id = {
        vendor.vendor_id: vendor
        for vendor in related_vendors
    }

    # Add related vendor nodes.
    for vendor_id in related_vendor_ids:

        vendor = vendors_by_id.get(
            vendor_id
        )

        if vendor is None:
            continue

        _add_vendor_node(
            graph,
            session,
            vendor,
            selected=False,
        )

        _add_vendor_identity_nodes(
            graph,
            vendor,
        )

    # Add relationship edges.
    for relationship in selected_relationships:

        if (
            relationship.vendor_a_id
            not in graph
            or relationship.vendor_b_id
            not in graph
        ):
            continue

        edge_label = (
            RELATIONSHIP_EDGE_LABELS.get(
                relationship.relationship_type,
                relationship.relationship_type.upper(),
            )
        )

        edge_risk = _relationship_risk(
            relationship.relationship_type,
            relationship.confidence,
        )

        _add_edge(
            graph,
            relationship.vendor_a_id,
            relationship.vendor_b_id,
            label=edge_label,
            risk=edge_risk,
            evidence=relationship.evidence,
        )

    return related_vendors


# ============================================================
# TRANSACTION NODES
# ============================================================

def _add_transaction_nodes(
    graph: nx.MultiDiGraph,
    session: Session,
    vendor: Vendor,
) -> None:

    transactions = session.query(
        Transaction
    ).filter(
        Transaction.vendor_id
        == vendor.vendor_id
    ).order_by(
        Transaction.transaction_date.desc()
    ).limit(
        MAX_TRANSACTIONS
    ).all()

    for transaction in transactions:

        transaction_node_id = (
            f"TXN-{transaction.transaction_id}"
        )

        _add_node(
            graph,
            transaction_node_id,
            label=(
                f"₹{transaction.amount:,.0f}"
            ),
            type="transaction",
            risk="LOW",
            transaction_id=(
                transaction.transaction_id
            ),
            amount=transaction.amount,
            status=transaction.status,
            date=(
                transaction.transaction_date.isoformat()
                if transaction.transaction_date
                else None
            ),
        )

        _add_edge(
            graph,
            transaction_node_id,
            vendor.vendor_id,
            label="PAID_TO",
            risk="LOW",
            evidence=(
                f"Transaction "
                f"{transaction.transaction_id}"
                f" paid ₹{transaction.amount:,.0f}"
            ),
        )

        # ----------------------------------------------------
        # Approved by employee
        # ----------------------------------------------------

        if transaction.approved_by:

            employee = transaction.approver

            if employee:

                employee_node_id = (
                    f"EMP-{employee.employee_id}"
                )

                _add_node(
                    graph,
                    employee_node_id,
                    label=employee.name,
                    type="employee",
                    risk="LOW",
                    role=employee.role,
                )

                _add_edge(
                    graph,
                    employee_node_id,
                    transaction_node_id,
                    label="APPROVED_BY",
                    risk="LOW",
                    evidence=(
                        f"{employee.name} approved "
                        f"{transaction.transaction_id}"
                    ),
                )


# ============================================================
# CHANGE / EMPLOYEE NODES
# ============================================================

def _add_change_actor_nodes(
    graph: nx.MultiDiGraph,
    session: Session,
    vendor: Vendor,
) -> None:

    changes = session.query(
        VendorChange
    ).filter(
        VendorChange.vendor_id
        == vendor.vendor_id
    ).all()

    added_employee_vendor_edges = set()

    for change in changes:

        if not change.changed_by:
            continue

        employee = (
            change.changed_by_employee
        )

        if employee is None:
            continue

        employee_node_id = (
            f"EMP-{employee.employee_id}"
        )

        _add_node(
            graph,
            employee_node_id,
            label=employee.name,
            type="employee",
            risk="LOW",
            role=employee.role,
        )

        edge_key = (
            employee_node_id,
            vendor.vendor_id,
        )

        if edge_key in (
            added_employee_vendor_edges
        ):
            continue

        added_employee_vendor_edges.add(
            edge_key
        )

        _add_edge(
            graph,
            employee_node_id,
            vendor.vendor_id,
            label="CHANGED_BY",
            risk="MEDIUM",
            evidence=(
                f"{employee.name} changed "
                f"vendor master data"
            ),
        )


# ============================================================
# NETWORKX -> API JSON
# ============================================================

def graph_to_json(
    graph: nx.MultiDiGraph,
) -> dict:

    nodes = []

    for node_id, attributes in (
        graph.nodes(data=True)
    ):

        node_data = {
            "id": node_id,
        }

        node_data.update(
            attributes
        )

        nodes.append(
            node_data
        )

    edges = []

    edge_counter = 0

    for (
        source,
        target,
        key,
        attributes,
    ) in graph.edges(
        keys=True,
        data=True,
    ):

        edge_counter += 1

        edge_data = {
            "id": (
                f"E-{edge_counter}"
            ),
            "source": source,
            "target": target,
        }

        edge_data.update(
            attributes
        )

        edges.append(
            edge_data
        )

    return {
        "nodes": nodes,
        "edges": edges,
    }


# ============================================================
# PUBLIC GRAPH FUNCTION
# ============================================================

def build_vendor_graph(
    session: Session,
    vendor_id: str,
) -> Optional[dict]:
    """
    Build a useful LOCAL investigation graph.

    Important:
    This intentionally does NOT load all vendors into
    the returned graph.

    It includes only:
    - selected vendor
    - direct relationship neighbours
    - identity/bank/address nodes
    - selected vendor transactions
    - involved employees
    """

    selected_vendor = session.query(
        Vendor
    ).filter(
        Vendor.vendor_id == vendor_id
    ).first()

    if selected_vendor is None:
        return None

    graph = nx.MultiDiGraph()

    # --------------------------------------------------------
    # Selected vendor
    # --------------------------------------------------------

    _add_vendor_node(
        graph,
        session,
        selected_vendor,
        selected=True,
    )

    _add_vendor_identity_nodes(
        graph,
        selected_vendor,
    )

    # --------------------------------------------------------
    # Direct vendor relationships
    # --------------------------------------------------------

    _add_related_vendors(
        graph,
        session,
        selected_vendor,
    )

    # --------------------------------------------------------
    # Transactions
    # --------------------------------------------------------

    _add_transaction_nodes(
        graph,
        session,
        selected_vendor,
    )

    # --------------------------------------------------------
    # Employees who changed vendor details
    # --------------------------------------------------------

    _add_change_actor_nodes(
        graph,
        session,
        selected_vendor,
    )

    result = graph_to_json(
        graph
    )

    result["vendor_id"] = (
        selected_vendor.vendor_id
    )

    result["vendor_name"] = (
        selected_vendor.legal_name
    )

    result["node_count"] = len(
        result["nodes"]
    )

    result["edge_count"] = len(
        result["edges"]
    )

    return result