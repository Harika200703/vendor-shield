from backend.database import SessionLocal

from backend.models import (
    Vendor,
    Employee,
    Transaction,
    VendorChange,
    NovaInvoice,
    NovaVendorBankAccount,
    NovaVendorPayment,
    NovaMasterDataChange,
    NovaApproval,
)


def check_database():
    db = SessionLocal()

    try:
        print("=" * 55)
        print("VendorTrust Database Health Check")
        print("=" * 55)

        counts = {
            "Synthetic Vendors": db.query(Vendor).count(),
            "Synthetic Employees": db.query(Employee).count(),
            "Synthetic Transactions": db.query(Transaction).count(),
            "Synthetic Vendor Changes": db.query(VendorChange).count(),
            "Nova Invoices": db.query(NovaInvoice).count(),
            "Nova Bank Accounts": db.query(
                NovaVendorBankAccount
            ).count(),
            "Nova Vendor Payments": db.query(
                NovaVendorPayment
            ).count(),
            "Nova Master Data Changes": db.query(
                NovaMasterDataChange
            ).count(),
            "Nova Approvals": db.query(
                NovaApproval
            ).count(),
        }

        for name, count in counts.items():
            status = "OK" if count > 0 else "EMPTY"
            print(f"{name:<30} {count:<6} [{status}]")

        print("=" * 55)

        if all(count > 0 for count in counts.values()):
            print("DATABASE STATUS: HEALTHY")
        else:
            print("DATABASE STATUS: CHECK REQUIRED")

        print("=" * 55)

    finally:
        db.close()


if __name__ == "__main__":
    check_database()