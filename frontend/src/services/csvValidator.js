const DATASET_SCHEMAS = {
  vendors: {
    label: "Vendor Dataset",
    required: [
      "vendor_id",
      "vendor_name",
      "gstin",
      "bank_account",
      "bank_name",
      "ifsc",
    ],
  },

  transactions: {
    label: "Transaction Dataset",
    required: [
      "transaction_id",
      "vendor_id",
      "amount",
      "transaction_date",
      "status",
    ],
  },

  vendor_changes: {
    label: "Vendor Change History",
    required: [
      "change_id",
      "vendor_id",
      "field_changed",
      "old_value",
      "new_value",
      "changed_at",
    ],
  },

  employees: {
    label: "Employee Dataset",
    required: [
      "employee_id",
      "employee_name",
      "role",
      "associated_vendor_id",
    ],
  },
};

function normalizeHeader(header) {
  return header
    .trim()
    .replace(/^"|"$/g, "")
    .toLowerCase()
    .replace(/\s+/g, "_");
}

export function detectDatasetType(fileName) {
  const name = fileName.toLowerCase();

  if (name.includes("vendor_changes")) {
    return "vendor_changes";
  }

  if (name.includes("transactions")) {
    return "transactions";
  }

  if (name.includes("employees")) {
    return "employees";
  }

  if (name.includes("vendors")) {
    return "vendors";
  }

  return null;
}

export function validateCSV(
  fileName,
  headers,
  recordCount
) {
  const datasetType =
    detectDatasetType(fileName);

  if (!datasetType) {
    return {
      valid: false,
      datasetType: "unknown",
      label: "Unknown Dataset",
      headers,
      recordCount,
      required: [],
      missing: [],
      matched: [],
      message:
        "Unable to identify this CSV dataset.",
    };
  }

  const schema =
    DATASET_SCHEMAS[datasetType];

  const normalizedHeaders = headers.map(
    normalizeHeader
  );

  const matched = schema.required.filter(
    (field) =>
      normalizedHeaders.includes(field)
  );

  const missing = schema.required.filter(
    (field) =>
      !normalizedHeaders.includes(field)
  );

  return {
    valid: missing.length === 0,
    datasetType,
    label: schema.label,
    headers: normalizedHeaders,
    recordCount,
    required: schema.required,
    missing,
    matched,
    message:
      missing.length === 0
        ? "All required fields detected."
        : `${missing.length} required field${
            missing.length === 1 ? "" : "s"
          } missing.`,
  };
}

export function getDatasetSchema(
  datasetType
) {
  return DATASET_SCHEMAS[datasetType] || null;
}