from rapidfuzz.fuzz import token_set_ratio

from backend.services.normalizer import normalize_vendor


def similarity_score(value1, value2):
    """Return similarity between two text values from 0 to 1."""

    if not value1 or not value2:
        return 0.0

    return token_set_ratio(value1, value2) / 100


def compare_vendors(vendor_a, vendor_b):
    """
    Compare two vendors and identify possible relationships.
    """

    # Normalize both vendors
    a = normalize_vendor(vendor_a)
    b = normalize_vendor(vendor_b)

    # -------------------------
    # 1. TAX ID MATCH
    # -------------------------

    gstin_match = (
        bool(a["normalized_gstin"])
        and bool(b["normalized_gstin"])
        and a["normalized_gstin"] == b["normalized_gstin"]
    )

    pan_match = (
        bool(a["normalized_pan"])
        and bool(b["normalized_pan"])
        and a["normalized_pan"] == b["normalized_pan"]
    )

    tax_id_match = gstin_match or pan_match

    # -------------------------
    # 2. BANK MATCH
    # -------------------------

    bank_match = (
        bool(a.get("bank_account"))
        and bool(b.get("bank_account"))
        and bool(a.get("bank_ifsc"))
        and bool(b.get("bank_ifsc"))
        and a["bank_account"] == b["bank_account"]
        and a["bank_ifsc"] == b["bank_ifsc"]
    )

    # -------------------------
    # 3. PHONE MATCH
    # -------------------------

    phone_match = (
        bool(a["normalized_phone"])
        and bool(b["normalized_phone"])
        and a["normalized_phone"] == b["normalized_phone"]
    )

    # -------------------------
    # 4. EMAIL MATCH
    # -------------------------

    email_match = (
        bool(a["normalized_email"])
        and bool(b["normalized_email"])
        and a["normalized_email"] == b["normalized_email"]
    )

    # -------------------------
    # 5. ADDRESS MATCH
    # -------------------------

    address_match = (
        bool(a["normalized_address"])
        and bool(b["normalized_address"])
        and a["normalized_address"] == b["normalized_address"]
    )

    # -------------------------
    # 6. NAME SIMILARITY
    # -------------------------

    name_similarity = similarity_score(
        a["normalized_name"],
        b["normalized_name"]
    )

    # -------------------------
    # 7. ADDRESS SIMILARITY
    # -------------------------

    address_similarity = similarity_score(
        a["normalized_address"],
        b["normalized_address"]
    )

    # -------------------------
    # 8. CONFIDENCE SCORE
    # -------------------------

    confidence = (
        0.35 * name_similarity
        + 0.20 * address_similarity
        + 0.15 * float(phone_match)
        + 0.10 * float(email_match)
        + 0.10 * float(bank_match)
        + 0.10 * float(tax_id_match)
    )

    relationships = []

    # -------------------------
    # 9. TAX ID RELATIONSHIP
    # -------------------------

    if tax_id_match:

        relationships.append({
            "relationship_type": "shared_tax_id",
            "confidence": 1.0,
            "evidence": "Matching GSTIN or PAN"
        })

        relationships.append({
            "relationship_type": "duplicate_candidate",
            "confidence": 1.0,
            "evidence": "Matching GSTIN or PAN"
        })

    # -------------------------
    # 10. BANK RELATIONSHIP
    # -------------------------

    if bank_match:

        relationships.append({
            "relationship_type": "shared_bank",
            "confidence": round(confidence, 4),
            "evidence": "Matching bank account and IFSC"
        })

    # -------------------------
    # 11. PHONE RELATIONSHIP
    # -------------------------

    if phone_match:

        relationships.append({
            "relationship_type": "shared_phone",
            "confidence": round(confidence, 4),
            "evidence": "Matching phone number"
        })

    # -------------------------
    # 12. EMAIL RELATIONSHIP
    # -------------------------

    if email_match:

        relationships.append({
            "relationship_type": "shared_email",
            "confidence": round(confidence, 4),
            "evidence": "Matching email address"
        })

    # -------------------------
    # 13. ADDRESS RELATIONSHIP
    # -------------------------

    if address_match:

        relationships.append({
            "relationship_type": "shared_address",
            "confidence": round(confidence, 4),
            "evidence": "Matching address"
        })

    # -------------------------
    # 14. DUPLICATE / SIMILAR
    # -------------------------

    if confidence >= 0.85 and not tax_id_match:

        relationships.append({
            "relationship_type": "duplicate_candidate",
            "confidence": round(confidence, 4),
            "evidence": (
                f"Name similarity: {name_similarity:.0%}; "
                f"Address similarity: {address_similarity:.0%}"
            )
        })

    elif 0.70 <= confidence < 0.85:

        relationships.append({
            "relationship_type": "similar_identity",
            "confidence": round(confidence, 4),
            "evidence": (
                f"Name similarity: {name_similarity:.0%}; "
                f"Address similarity: {address_similarity:.0%}"
            )
        })

    # -------------------------
    # 15. RETURN RESULT
    # -------------------------

    return {
        "vendor_a_id": vendor_a["vendor_id"],
        "vendor_b_id": vendor_b["vendor_id"],
        "confidence": round(confidence, 4),
        "name_similarity": round(name_similarity, 4),
        "address_similarity": round(address_similarity, 4),
        "relationships": relationships
    }


def generate_blocking_keys(vendor):
    """
    Generate keys used to find vendors that may be related.
    """

    normalized = normalize_vendor(vendor)

    keys = set()

    # Name blocking key
    name = normalized["normalized_name"]

    if name:
        words = name.split()

        if words:
            keys.add(f"name:{words[0][:3]}")

    # GSTIN blocking key
    if normalized["normalized_gstin"]:
        keys.add(f"gstin:{normalized['normalized_gstin']}")

    # PAN blocking key
    if normalized["normalized_pan"]:
        keys.add(f"pan:{normalized['normalized_pan']}")

    # Bank blocking key
    if vendor.get("bank_account") and vendor.get("bank_ifsc"):
        keys.add(
            f"bank:{vendor['bank_account']}:{vendor['bank_ifsc']}"
        )

    # Phone blocking key
    if normalized["normalized_phone"]:
        keys.add(
            f"phone:{normalized['normalized_phone']}"
        )

    # Email blocking key
    if normalized["normalized_email"]:
        keys.add(
            f"email:{normalized['normalized_email']}"
        )

    return keys


def generate_relationships(vendors):
    """
    Compare only vendors that share at least one blocking key.
    """

    # -------------------------
    # 1. CREATE BLOCKS
    # -------------------------

    blocks = {}

    for vendor in vendors:

        keys = generate_blocking_keys(vendor)

        for key in keys:

            if key not in blocks:
                blocks[key] = []

            blocks[key].append(vendor)

    # -------------------------
    # 2. FIND CANDIDATE PAIRS
    # -------------------------

    candidate_pairs = set()

    for block_vendors in blocks.values():

        for i in range(len(block_vendors)):

            for j in range(i + 1, len(block_vendors)):

                vendor_a = block_vendors[i]
                vendor_b = block_vendors[j]

                pair = tuple(
                    sorted([
                        vendor_a["vendor_id"],
                        vendor_b["vendor_id"]
                    ])
                )

                candidate_pairs.add(pair)

    # -------------------------
    # 3. CREATE LOOKUP
    # -------------------------

    vendor_lookup = {
        vendor["vendor_id"]: vendor
        for vendor in vendors
    }

    # -------------------------
    # 4. COMPARE CANDIDATES
    # -------------------------

    relationships = []

    for vendor_a_id, vendor_b_id in candidate_pairs:

        vendor_a = vendor_lookup[vendor_a_id]
        vendor_b = vendor_lookup[vendor_b_id]

        result = compare_vendors(
            vendor_a,
            vendor_b
        )

        for relationship in result["relationships"]:

            relationships.append({
                "vendor_a_id": result["vendor_a_id"],
                "vendor_b_id": result["vendor_b_id"],
                "relationship_type": relationship["relationship_type"],
                "confidence": relationship["confidence"],
                "evidence": relationship["evidence"]
            })

    return relationships

def run_entity_resolution(session):
    from backend.models import Vendor, VendorRelationship

    # Get all vendors from database
    vendors = session.query(Vendor).all()

    vendor_data = []

    for vendor in vendors:
        vendor_data.append({
            "vendor_id": vendor.vendor_id,
            "legal_name": vendor.legal_name,
            "gstin": vendor.gstin,
            "pan": vendor.pan,
            "bank_account": vendor.bank_account,
            "bank_ifsc": vendor.bank_ifsc,
            "phone": vendor.phone,
            "email": vendor.email,
            "address": vendor.address
        })

    # Generate relationships using your existing logic
    relationships = generate_relationships(vendor_data)

    saved_count = 0

    for relationship in relationships:

        # Prevent duplicate relationships
        existing = session.query(VendorRelationship).filter_by(
            vendor_a_id=relationship["vendor_a_id"],
            vendor_b_id=relationship["vendor_b_id"],
            relationship_type=relationship["relationship_type"]
        ).first()

        if existing:
            continue

        new_relationship = VendorRelationship(
            vendor_a_id=relationship["vendor_a_id"],
            vendor_b_id=relationship["vendor_b_id"],
            relationship_type=relationship["relationship_type"],
            confidence=relationship["confidence"],
            evidence=relationship["evidence"]
        )

        session.add(new_relationship)
        saved_count += 1

    session.commit()

    return {
        "relationships_found": len(relationships),
        "relationships_saved": saved_count
}