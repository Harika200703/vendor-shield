from rapidfuzz.fuzz import token_set_ratio

from services.normalizer import normalize_vendor


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


vendor_b = {
    "vendor_id": "V002",
    "legal_name": "ABC Industries Private Limited",
    "gstin": "36ABCDE1234F1Z5",
    "pan": "ABCDE1234F",
    "bank_account": "1234567890",
    "bank_ifsc": "SBIN0001234",
    "phone": "+91-9876543210",
    "email": "abc@gmail.com",
    "address": "Plot 12, Hyderabad, Telangana"
}


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


vendors = [
    vendor_a,
    vendor_b,
    vendor_c
]


relationships = generate_relationships(vendors)


print("\n--- RELATIONSHIPS FOUND ---\n")

for relationship in relationships:
    print(relationship)