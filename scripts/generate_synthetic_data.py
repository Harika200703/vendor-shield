import random
import string
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(exist_ok=True)

NUM_VENDORS = 1500
NUM_TRANSACTIONS = 20000
NUM_CHANGES = 500
NUM_EMPLOYEES = 25


# ============================================================
# DEMO STORY REGISTRY
# ============================================================

STORIES = {
    "hero_vendor": "V0001",
    "hero_duplicate_vendor": "V0002",
    "shared_bank_vendor_a": "V0010",
    "shared_bank_vendor_b": "V0011",
    "related_vendor_a": "V0020",
    "related_vendor_b": "V0021",
    "related_vendor_c": "V0022",
    "legitimate_subsidiary_a": "V0030",
    "legitimate_subsidiary_b": "V0031",
    "hero_transaction": "T00001",
}


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def normalize_name(name):
    return (
        str(name)
        .upper()
        .replace(".", "")
        .replace(",", "")
        .replace("-", "")
        .replace(" ", "")
    )


def normalize_address(address):
    return (
        str(address)
        .upper()
        .replace(",", "")
        .replace(".", "")
        .replace("-", "")
        .replace(" ", "")
    )


# ============================================================
# RANDOM DATA HELPERS
# ============================================================

def random_string(length=8):
    return "".join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=length
        )
    )


def random_phone():
    return "9" + "".join(
        random.choices(string.digits, k=9)
    )


def random_email(name, index):
    clean_name = (
        name.lower()
        .replace(" ", "")
        .replace(".", "")
    )

    return f"{clean_name}{index}@example.com"


def random_gstin():
    state_code = f"{random.randint(10, 99):02d}"

    pan = (
        "".join(
            random.choices(
                string.ascii_uppercase,
                k=5
            )
        )
        + "".join(
            random.choices(
                string.digits,
                k=4
            )
        )
        + random.choice(string.ascii_uppercase)
    )

    return f"{state_code}{pan}Z{random.randint(1, 9)}"


def random_pan():
    return (
        "".join(
            random.choices(
                string.ascii_uppercase,
                k=5
            )
        )
        + "".join(
            random.choices(
                string.digits,
                k=4
            )
        )
        + random.choice(string.ascii_uppercase)
    )


def random_bank_account():
    return "".join(
        random.choices(
            string.digits,
            k=12
        )
    )


def mask_bank_account(account):
    account = str(account)
    return "*" * max(0, len(account) - 4) + account[-4:]


def random_ifsc():
    bank_codes = [
        "HDFC",
        "ICIC",
        "SBIN",
        "AXIS",
        "KKBK"
    ]

    return (
        random.choice(bank_codes)
        + "0"
        + random_string(6)
    )


def random_date(
    start_year=2024,
    end_year=2026
):
    start = datetime(
        start_year,
        1,
        1
    )

    end = datetime(
        end_year,
        9,
        30
    )

    days = (end - start).days

    return start + timedelta(
        days=random.randint(0, days)
    )


# ============================================================
# EMPLOYEES
# ============================================================

def generate_employees():

    employees = []

    roles = [
        "Finance Manager",
        "AP Analyst",
        "Procurement Officer",
        "Finance Analyst",
        "Accounts Executive",
    ]

    for i in range(1, NUM_EMPLOYEES + 1):

        employees.append({
            "employee_id": f"E{i:04d}",
            "name": f"Employee {i}",
            "email": f"employee{i}@vendortrust.demo",
            "role": random.choice(roles),
        })

    return employees


# ============================================================
# VENDORS
# ============================================================

def generate_vendors():

    vendors = []

    company_prefixes = [
        "Global",
        "Prime",
        "National",
        "Metro",
        "United",
        "Apex",
        "Reliable",
        "Industrial",
        "Eastern",
        "Southern",
    ]

    company_types = [
        "Industries",
        "Suppliers",
        "Enterprises",
        "Traders",
        "Solutions",
        "Services",
        "Technologies",
    ]

    cities = [
        "Hyderabad",
        "Mumbai",
        "Delhi",
        "Pune",
        "Chennai",
        "Bengaluru",
    ]

    streets = [
        "MG Road",
        "Industrial Area",
        "Market Street",
        "Main Road",
    ]

    for i in range(1, NUM_VENDORS + 1):

        vendor_id = f"V{i:04d}"

        legal_name = (
            f"{random.choice(company_prefixes)} "
            f"{random.choice(company_types)} "
            f"{i}"
        )

        address = (
            f"{random.randint(1, 999)}, "
            f"{random.choice(streets)}, "
            f"{random.choice(cities)}"
        )

        bank_account = random_bank_account()

        vendors.append({
            "vendor_id": vendor_id,
            "legal_name": legal_name,
            "normalized_name": normalize_name(
                legal_name
            ),
            "gstin": random_gstin(),
            "pan": random_pan(),
            "bank_account": bank_account,
            "bank_account_masked": mask_bank_account(
                bank_account
            ),
            "bank_ifsc": random_ifsc(),
            "phone": random_phone(),
            "email": random_email(
                legal_name,
                i
            ),
            "address": address,
            "normalized_address": normalize_address(
                address
            ),
            "status": random.choice([
                "ACTIVE",
                "ACTIVE",
                "ACTIVE",
                "INACTIVE",
            ]),
            "created_at": (
                datetime(2024, 1, 1)
                + timedelta(
                    days=random.randint(0, 900)
                )
            ),
        })

    return vendors


# ============================================================
# CONTROLLED DEMO STORIES
# ============================================================

def inject_vendor_stories(vendors):

    vendor_map = {
        vendor["vendor_id"]: vendor
        for vendor in vendors
    }

    # --------------------------------------------------------
    # STORY 1
    # ABC Industrial Pvt Ltd
    #
    # Same GSTIN as another vendor.
    # Bank account will later be changed.
    # Large payment follows the change.
    # --------------------------------------------------------

    hero = vendor_map["V0001"]
    duplicate = vendor_map["V0002"]

    hero["legal_name"] = (
        "ABC Industrial Pvt Ltd"
    )

    hero["normalized_name"] = normalize_name(
        "ABC Industrial Pvt Ltd"
    )

    hero["gstin"] = "36ABCDE1234F1Z5"

    duplicate["legal_name"] = (
        "ABC Industrial Private Limited"
    )

    duplicate["normalized_name"] = normalize_name(
        "ABC Industrial Private Limited"
    )

    duplicate["gstin"] = hero["gstin"]

    # --------------------------------------------------------
    # STORY 2
    # Two vendors share the same bank account.
    # --------------------------------------------------------

    shared_bank = "987654321012"

    for vendor_id in [
        "V0010",
        "V0011"
    ]:
        vendor_map[vendor_id][
            "bank_account"
        ] = shared_bank

        vendor_map[vendor_id][
            "bank_account_masked"
        ] = mask_bank_account(
            shared_bank
        )

    # --------------------------------------------------------
    # STORY 3
    # Three vendors share address and phone.
    # Two also share bank account.
    # --------------------------------------------------------

    related_address = (
        "12 Industrial Estate Hyderabad"
    )

    related_phone = "9876543210"

    for vendor_id in [
        "V0020",
        "V0021",
        "V0022"
    ]:
        vendor_map[vendor_id][
            "address"
        ] = related_address

        vendor_map[vendor_id][
            "normalized_address"
        ] = normalize_address(
            related_address
        )

        vendor_map[vendor_id][
            "phone"
        ] = related_phone

    related_bank = "123456789012"

    for vendor_id in [
        "V0020",
        "V0021"
    ]:
        vendor_map[vendor_id][
            "bank_account"
        ] = related_bank

        vendor_map[vendor_id][
            "bank_account_masked"
        ] = mask_bank_account(
            related_bank
        )

    # --------------------------------------------------------
    # STORY 4
    # Legitimate subsidiaries.
    #
    # Same address but different identities.
    # This is useful for demonstrating false-positive control.
    # --------------------------------------------------------

    subsidiary_address = (
        "100 Corporate Park Hyderabad"
    )

    vendor_map["V0030"][
        "legal_name"
    ] = "ABC Technologies India Pvt Ltd"

    vendor_map["V0031"][
        "legal_name"
    ] = "ABC Technologies Services Pvt Ltd"

    for vendor_id in [
        "V0030",
        "V0031"
    ]:
        vendor_map[vendor_id][
            "address"
        ] = subsidiary_address

        vendor_map[vendor_id][
            "normalized_address"
        ] = normalize_address(
            subsidiary_address
        )

    return vendors


# ============================================================
# VENDOR CHANGES
# ============================================================

def generate_vendor_changes(
    vendors,
    employees
):

    changes = []

    employee_ids = [
        employee["employee_id"]
        for employee in employees
    ]

    # --------------------------------------------------------
    # HERO BANK CHANGE
    # --------------------------------------------------------

    old_bank = "111122223333"
    new_bank = "444455556666"

    hero = next(
        vendor
        for vendor in vendors
        if vendor["vendor_id"] == "V0001"
    )

    hero["bank_account"] = new_bank

    hero["bank_account_masked"] = (
        mask_bank_account(new_bank)
    )

    bank_change_date = datetime(
        2026,
        9,
        10,
        10,
        30
    )

    changes.append({
        "change_id": 1,
        "vendor_id": "V0001",
        "field_changed": "bank_account",
        "old_value": old_bank,
        "new_value": new_bank,
        "changed_at": bank_change_date,
        "changed_by": "E0002",
    })

    # --------------------------------------------------------
    # OTHER CHANGES
    # --------------------------------------------------------

    change_id = 2

    fields = [
        "phone",
        "email",
        "address",
        "bank_account",
        "gstin",
    ]

    for _ in range(
        NUM_CHANGES - 1
    ):

        vendor = random.choice(
            vendors
        )

        field = random.choice(
            fields
        )

        employee_id = random.choice(
            employee_ids
        )

        old_value = (
            f"OLD_{random_string(8)}"
        )

        new_value = (
            f"NEW_{random_string(8)}"
        )

        changes.append({
            "change_id": change_id,
            "vendor_id": vendor["vendor_id"],
            "field_changed": field,
            "old_value": old_value,
            "new_value": new_value,
            "changed_at": random_date(),
            "changed_by": employee_id,
        })

        change_id += 1

    return changes


# ============================================================
# TRANSACTIONS
# ============================================================

def generate_transactions(
    vendors,
    employees
):

    transactions = []

    employee_ids = [
        employee["employee_id"]
        for employee in employees
    ]

    vendor_ids = [
        vendor["vendor_id"]
        for vendor in vendors
    ]

    # --------------------------------------------------------
    # HERO TRANSACTION
    #
    # ₹8.7 lakh payment within two days of bank change.
    # --------------------------------------------------------

    transactions.append({
        "transaction_id": "T00001",
        "vendor_id": "V0001",
        "amount": 870000,
        "invoice_no": "INV-ABC-001",
        "transaction_date": datetime(
            2026,
            9,
            11,
            14,
            30
        ),
        "status": "PENDING",
        "approved_by": "",
        "initiated_by": "E0003",
    })

    # --------------------------------------------------------
    # NORMAL TRANSACTIONS
    # --------------------------------------------------------

    for i in range(
        2,
        NUM_TRANSACTIONS + 1
    ):

        vendor_id = random.choice(
            vendor_ids
        )

        amount = round(
            random.uniform(
                5000,
                500000
            ),
            2
        )

        transaction_date = random_date()

        status = random.choice([
            "PAID",
            "PAID",
            "PAID",
            "PENDING",
            "APPROVED",
        ])

        approved_by = ""

        if status in [
            "PAID",
            "APPROVED"
        ]:
            approved_by = random.choice(
                employee_ids
            )

        transactions.append({
            "transaction_id": f"T{i:05d}",
            "vendor_id": vendor_id,
            "amount": amount,
            "invoice_no": f"INV-{i:06d}",
            "transaction_date": transaction_date,
            "status": status,
            "approved_by": approved_by,
            "initiated_by": random.choice(
                employee_ids
            ),
        })

    return transactions


# ============================================================
# CSV WRITER
# ============================================================

def write_csv(
    filename,
    rows
):

    path = DATA_DIR / filename

    df = pd.DataFrame(rows)

    df.to_csv(
        path,
        index=False
    )

    print(
        f"Created {filename}: "
        f"{len(df)} records"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "Generating VendorTrust "
        "synthetic dataset..."
    )

    employees = generate_employees()

    vendors = generate_vendors()

    vendors = inject_vendor_stories(
        vendors
    )

    changes = generate_vendor_changes(
        vendors,
        employees
    )

    transactions = generate_transactions(
        vendors,
        employees
    )

    # --------------------------------------------------------
    # WRITE CSV FILES
    # --------------------------------------------------------

    write_csv(
        "employees.csv",
        employees
    )

    write_csv(
        "vendors.csv",
        vendors
    )

    write_csv(
        "vendor_changes.csv",
        changes
    )

    write_csv(
        "transactions.csv",
        transactions
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print(
        "\nDataset generation completed."
    )

    print(
        "\nDemo story IDs:"
    )

    for key, value in STORIES.items():
        print(
            f"{key}: {value}"
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()