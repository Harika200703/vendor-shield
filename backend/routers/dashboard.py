from typing import Dict, List, Any
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Vendor, VendorChange, Approval, Transaction, RiskEvent
from ..services.risk_engine import calculate_risk_score, get_risk_level


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("")
def get_dashboard_data(session: Session = Depends(get_db)):
    """
    Returns aggregated dashboard metrics including risk distribution,
    pending approvals, exposure, and a list of the top critical vendors.
    """

    # 1. Total vendors
    total_vendors = session.query(Vendor).count()

    # 2. Changes today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    changes_today = session.query(VendorChange).filter(
        VendorChange.changed_at != None,
        VendorChange.changed_at >= today_start
    ).count()

    # 3. Pending approvals
    pending_approvals = session.query(Approval).filter(
        Approval.status == "PENDING"
    ).count()

    # 4. Payment exposure (sum of PENDING transactions)
    exposure_result = session.query(
        func.sum(Transaction.amount)
    ).filter(
        Transaction.status == "PENDING"
    ).scalar()
    payment_exposure = float(exposure_result) if exposure_result else 0.0

    # 5. Fetch risk events and calculate dynamic risk distribution
    vendors = session.query(Vendor).all()
    risk_events = session.query(RiskEvent).all()
    
    events_by_vendor: Dict[str, List[RiskEvent]] = {}
    for event in risk_events:
        if event.vendor_id not in events_by_vendor:
            events_by_vendor[event.vendor_id] = []
        events_by_vendor[event.vendor_id].append(event)
    
    risk_counts = {
        "LOW": 0,
        "MEDIUM": 0,
        "HIGH": 0,
        "CRITICAL": 0
    }
    
    top_vendors_list = []
    
    for vendor in vendors:
        events = events_by_vendor.get(vendor.vendor_id, [])
        score = calculate_risk_score(events)
        level = get_risk_level(score)
        
        risk_counts[level] += 1
        
        if level in ["HIGH", "CRITICAL"]:
            # Get latest change date for this vendor
            last_change = session.query(VendorChange).filter(
                VendorChange.vendor_id == vendor.vendor_id
            ).order_by(
                VendorChange.changed_at.desc()
            ).first()
            
            last_change_str = "No changes"
            if last_change and last_change.changed_at:
                last_change_str = last_change.changed_at.strftime("%d %b %Y")
            
            # Vendor-specific payment exposure
            vendor_exposure = session.query(func.sum(Transaction.amount)).filter(
                Transaction.vendor_id == vendor.vendor_id,
                Transaction.status == "PENDING"
            ).scalar()
            
            # Primary risk signal
            top_event = sorted(events, key=lambda x: x.score_contribution, reverse=True)
            signal = top_event[0].evidence if top_event else "High risk signals detected"
            
            top_vendors_list.append({
                "id": vendor.vendor_id,
                "name": vendor.legal_name,
                "riskScore": score,
                "riskLevel": level,
                "lastChange": last_change_str,
                "paymentExposure": float(vendor_exposure) if vendor_exposure else 0.0,
                "signal": signal
            })
            
    # Sort top vendors by risk score descending
    top_vendors_list.sort(key=lambda x: x["riskScore"], reverse=True)
    
    # Return exactly the fields expected by the frontend
    return {
        "totalVendors": total_vendors,
        "highRiskVendors": risk_counts["HIGH"],
        "criticalVendors": risk_counts["CRITICAL"],
        "changesToday": changes_today,
        "pendingApprovals": pending_approvals,
        "paymentExposure": payment_exposure,
        "riskDistribution": [
            {"name": "Low", "value": risk_counts["LOW"]},
            {"name": "Medium", "value": risk_counts["MEDIUM"]},
            {"name": "High", "value": risk_counts["HIGH"]},
            {"name": "Critical", "value": risk_counts["CRITICAL"]}
        ],
        "criticalVendors": top_vendors_list[:4] # Take top 4 for the dashboard
    }
