import axios from "axios";

import {
  mockDashboard,
  mockVendors,
  mockApprovals,
  mockAuditLogs,
} from "../mock/mockData";

/*
|--------------------------------------------------------------------------
| Vendor Shield API configuration
|--------------------------------------------------------------------------
|
| true  = frontend demo / mock data
| false = FastAPI backend
|
| This is the ONE switch needed when the backend is ready.
|
*/

const USE_MOCK_API = true;

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 15000,
});

/*
|--------------------------------------------------------------------------
| Dashboard
|--------------------------------------------------------------------------
*/

export async function getDashboard() {
  if (USE_MOCK_API) {
    await mockDelay();

    return mockDashboard;
  }

  const response =
    await api.get("/api/dashboard");

  return response.data;
}

/*
|--------------------------------------------------------------------------
| Vendors
|--------------------------------------------------------------------------
*/

export async function getVendors(params = {}) {
  if (USE_MOCK_API) {
    await mockDelay();

    let result = [...mockVendors];

    if (params.search) {
      const search =
        params.search.toLowerCase();

      result = result.filter(
        (vendor) =>
          vendor.name
            .toLowerCase()
            .includes(search) ||
          vendor.gstin
            ?.toLowerCase()
            .includes(search) ||
          vendor.id
            ?.toLowerCase()
            .includes(search)
      );
    }

    if (
      params.riskLevel &&
      params.riskLevel !== "ALL"
    ) {
      result = result.filter(
        (vendor) =>
          vendor.riskLevel ===
          params.riskLevel
      );
    }

    return result;
  }

  const response = await api.get(
    "/api/vendors",
    {
      params,
    }
  );

  return response.data;
}

/*
|--------------------------------------------------------------------------
| Vendor details
|--------------------------------------------------------------------------
*/

export async function getVendor(
  vendorId
) {
  if (USE_MOCK_API) {
    await mockDelay();

    return mockVendors.find(
      (vendor) => vendor.id === vendorId
    );
  }

  const response = await api.get(
    `/api/vendors/${vendorId}`
  );

  return response.data;
}

/*
|--------------------------------------------------------------------------
| Vendor DNA
|--------------------------------------------------------------------------
*/

export async function getVendorDNA(
  vendorId
) {
  if (USE_MOCK_API) {
    await mockDelay();

    return getMockVendorDNA(vendorId);
  }

  const response = await api.get(
    `/api/vendors/${vendorId}/dna`
  );

  return response.data;
}

/*
|--------------------------------------------------------------------------
| Vendor relationships
|--------------------------------------------------------------------------
*/

export async function getVendorRelationships(
  vendorId
) {
  if (USE_MOCK_API) {
    await mockDelay();

    return getMockRelationships(vendorId);
  }

  const response = await api.get(
    `/api/vendors/${vendorId}/relationships`
  );

  return response.data;
}

/*
|--------------------------------------------------------------------------
| Investigation
|--------------------------------------------------------------------------
*/

export async function getInvestigation(
  vendorId
) {
  if (USE_MOCK_API) {
    await mockDelay();

    return getMockInvestigation(vendorId);
  }

  const response = await api.get(
    `/api/vendors/${vendorId}/investigation`
  );

  return response.data;
}

/*
|--------------------------------------------------------------------------
| Approvals
|--------------------------------------------------------------------------
*/

export async function getApprovals() {
  if (USE_MOCK_API) {
    await mockDelay();

    return mockApprovals;
  }

  const response =
    await api.get("/api/approvals");

  return response.data;
}

/*
|--------------------------------------------------------------------------
| Approval action
|--------------------------------------------------------------------------
*/

export async function takeApprovalAction(
  transactionId,
  action,
  note = ""
) {
  if (USE_MOCK_API) {
    await mockDelay();

    return {
      success: true,
      transactionId,
      action,
      note,
      message: `Transaction ${action.toLowerCase()} successfully.`,
    };
  }

  const response = await api.post(
    `/api/approvals/${transactionId}/action`,
    {
      action,
      note,
    }
  );

  return response.data;
}

/*
|--------------------------------------------------------------------------
| Audit logs
|--------------------------------------------------------------------------
*/

export async function getAuditLogs() {
  if (USE_MOCK_API) {
    await mockDelay();

    return mockAuditLogs;
  }

  const response =
    await api.get("/api/audit-logs");

  return response.data;
}

/*
|--------------------------------------------------------------------------
| CSV upload
|--------------------------------------------------------------------------
|
| Backend upload endpoint is proposed as:
|
| POST /api/upload
|
| Confirm this endpoint name with the backend team before
| connecting the live API because it was not in the original
| API contract.
|
*/

export async function uploadDatasets(
  files,
  onUploadProgress
) {
  if (USE_MOCK_API) {
    await mockDelay(800);

    return {
      success: true,
      message: "Datasets uploaded successfully.",
      files: files.map((file) => ({
        name: file.name,
        size: file.size,
      })),
    };
  }

  const formData = new FormData();

  files.forEach((file) => {
    formData.append("files", file);
  });

  const response = await api.post(
    "/api/upload",
    formData,
    {
      headers: {
        "Content-Type":
          "multipart/form-data",
      },
      onUploadProgress,
    }
  );

  return response.data;
}

/*
|--------------------------------------------------------------------------
| Helpers
|--------------------------------------------------------------------------
*/

function mockDelay(
  milliseconds = 350
) {
  return new Promise((resolve) =>
    setTimeout(
      resolve,
      milliseconds
    )
  );
}

function getMockVendorDNA(
  vendorId
) {
  const vendor =
    mockVendors.find(
      (item) => item.id === vendorId
    );

  return {
    vendor,
    identity: {
      score: 91,
      signals: [
        "GSTIN verified",
        "Name similarity detected",
      ],
    },
    banking: {
      score: 72,
      signals: [
        "Recent bank account change",
        "Shared bank relationship",
      ],
    },
    behaviour: {
      score: 68,
      signals: [
        "High-value transaction",
        "Unusual payment timing",
      ],
    },
    relationships: {
      score: 84,
      signals: [
        "Shared GSTIN",
        "Shared bank account",
      ],
    },
  };
}

function getMockRelationships(
  vendorId
) {
  return {
    nodes: [
      {
        id: vendorId,
        type: "vendor",
        data: {
          label:
            "ABC Industrial Pvt Ltd",
        },
        position: {
          x: 300,
          y: 180,
        },
      },
      {
        id: "bank-1",
        type: "bank",
        data: {
          label:
            "HDFC ••••9012",
        },
        position: {
          x: 100,
          y: 80,
        },
      },
      {
        id: "gstin-1",
        type: "gstin",
        data: {
          label:
            "GSTIN V-0981",
        },
        position: {
          x: 100,
          y: 280,
        },
      },
      {
        id: "vendor-1023",
        type: "vendor",
        data: {
          label:
            "Metro Components Ltd",
        },
        position: {
          x: 560,
          y: 80,
        },
      },
      {
        id: "transaction-1",
        type: "transaction",
        data: {
          label:
            "₹8.7L payment",
        },
        position: {
          x: 560,
          y: 280,
        },
      },
    ],

    edges: [
      {
        id: "e1",
        source: vendorId,
        target: "bank-1",
        label: "BANK",
      },
      {
        id: "e2",
        source: vendorId,
        target: "gstin-1",
        label: "GSTIN",
      },
      {
        id: "e3",
        source: "bank-1",
        target: "vendor-1023",
        label: "SHARED",
      },
      {
        id: "e4",
        source: vendorId,
        target: "transaction-1",
        label: "PAYMENT",
      },
    ],
  };
}

function getMockInvestigation(
  vendorId
) {
  return {
    vendorId,
    riskScore: 88,
    riskLevel: "CRITICAL",

    signals: [
      {
        title:
          "Recent bank account change",
        severity: "HIGH",
        description:
          "Bank details changed shortly before a high-value payment.",
      },
      {
        title:
          "Shared bank relationship",
        severity: "HIGH",
        description:
          "The current bank account is also connected to another vendor.",
      },
      {
        title:
          "Shared GSTIN relationship",
        severity: "MEDIUM",
        description:
          "A matching GSTIN relationship was detected.",
      },
    ],

    exposure: 870000,

    aiSummary:
      "The vendor shows multiple connected risk signals. The strongest evidence is the recent banking change combined with a high-value pending payment and shared banking identity.",

    recommendedAction:
      "HOLD",

    timeline: [
      {
        date: "20 Sep 2026",
        title:
          "₹8.7L payment initiated",
        type: "transaction",
      },
      {
        date: "18 Sep 2026",
        title:
          "Bank account changed",
        type: "change",
      },
      {
        date: "15 Sep 2026",
        title:
          "Vendor relationship detected",
        type: "relationship",
      },
    ],
  };
}

export default api;