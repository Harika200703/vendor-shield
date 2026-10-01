import re


def normalize_text(value):
    """Lowercase text, remove punctuation, and clean extra spaces."""
    if not value:
        return ""

    value = str(value).lower()
    value = re.sub(r"[^\w\s]", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def normalize_vendor_name(name):
    """Normalize vendor name and remove legal suffixes for comparison."""
    if not name:
        return ""

    name = normalize_text(name)

    # Remove legal business suffixes only for comparison
    suffixes = [
        "private limited",
        "pvt ltd",
        "private",
        "limited",
        "ltd",
        "pvt",
        "llp",
        "company",
    ]

    for suffix in suffixes:
        name = re.sub(rf"\b{re.escape(suffix)}\b", "", name)

    name = re.sub(r"\s+", " ", name)

    return name.strip()


def normalize_tax_id(value):
    """Normalize GSTIN or PAN."""
    if not value:
        return ""

    value = str(value).upper()
    value = re.sub(r"[\s\-]", "", value)

    return value


def normalize_phone(phone):
    """Normalize phone number by removing country code, spaces and hyphens."""
    if not phone:
        return ""

    phone = str(phone)
    phone = re.sub(r"[\s\-\(\)]", "", phone)

    if phone.startswith("+91"):
        phone = phone[3:]
    elif phone.startswith("91") and len(phone) > 10:
        phone = phone[2:]

    return phone


def normalize_email(email):
    """Normalize email for comparison."""
    if not email:
        return ""

    return str(email).strip().lower()


def normalize_address(address):
    """Normalize address by lowercasing and removing punctuation."""
    return normalize_text(address)


def normalize_vendor(vendor):
    """
    Create normalized comparison fields without changing
    the original vendor information.
    """

    return {
        **vendor,
        "normalized_name": normalize_vendor_name(
            vendor.get("legal_name")
        ),
        "normalized_gstin": normalize_tax_id(
            vendor.get("gstin")
        ),
        "normalized_pan": normalize_tax_id(
            vendor.get("pan")
        ),
        "normalized_phone": normalize_phone(
            vendor.get("phone")
        ),
        "normalized_email": normalize_email(
            vendor.get("email")
        ),
        "normalized_address": normalize_address(
            vendor.get("address")
        ),
    }