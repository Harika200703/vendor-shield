from services.entity_resolution import (
    generate_relationships,
    compare_vendors
)


# -------------------------
# VENDOR 1
# -------------------------

vendor_a = {
    "vendor_id": "V001",
    "legal_name": "ABC Industries Pvt Ltd",
    "gstin": "36ABCDE1234F1Z5",
    "pan": "ABCDE1234F",
    "bank_account": "1234567890",
    "bank_ifsc": "SBIN0001234",
    "phone": "+91-9876543210",
    "email": "abc@gmail.com",
    "address": "Plot No. 12, Hyderabad, Telangana"
}


# -------------------------
# VENDOR 2
# Exact duplicate
# -------------------------

vendor_b = {
    "vendor_id": "V002",
    "legal_name": "ABC Industries Private Limited",
    "gstin": "36ABCDE1234F1Z5",
    "pan": "ABCDE1234F",
    "bank_account": "1234567890",
    "bank_ifsc": "SBIN0001234",
    "phone": "+91-9876543210",
    "email": "abc@gmail.com",
    "address": "Plot No 12 Hyderabad Telangana"
}


# -------------------------
# VENDOR 3
# Completely different
# -------------------------

vendor_c = {
    "vendor_id": "V003",
    "legal_name": "XYZ Technologies Ltd",
    "gstin": "36XYZAB1234C1Z5",
    "pan": "XYZAB1234C",
    "bank_account": "9876543210",
    "bank_ifsc": "HDFC0001234",
    "phone": "+91-9123456789",
    "email": "xyz@gmail.com",
    "address": "Banjara Hills, Hyderabad, Telangana"
}


# -------------------------
# VENDOR 4
# Similar name/address
# -------------------------

vendor_d = {
    "vendor_id": "V004",
    "legal_name": "ABC Industrial",
    "gstin": "29ZZZZZ9999Z9Z9",
    "pan": "ZZZZZ9999Z",
    "bank_account": "5555555555",
    "bank_ifsc": "ICIC0005555",
    "phone": "+91-9000011111",
    "email": "abcindustrial@gmail.com",
    "address": "Plot 12 Hyderabad Telangana"
}


vendors = [
    vendor_a,
    vendor_b,
    vendor_c,
    vendor_d
]


# -------------------------
# TEST 1
# Generate relationships
# -------------------------

print("\n--- RELATIONSHIPS FOUND ---\n")

relationships = generate_relationships(vendors)

for relationship in relationships:
    print(relationship)


# -------------------------
# TEST 2
# V001 vs V004
# -------------------------

print("\n--- V001 vs V004 COMPARISON ---\n")

result = compare_vendors(
    vendor_a,
    vendor_d
)

print(result)


# -------------------------
# TEST 3
# V001 vs V003
# -------------------------

print("\n--- V001 vs V003 COMPARISON ---\n")

result = compare_vendors(
    vendor_a,
    vendor_c
)

print(result)