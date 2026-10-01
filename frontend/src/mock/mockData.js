export const mockDashboard = {
  totalVendors: 248,

  highRiskVendors: 17,

  criticalVendors: 4,

  changesToday: 12,

  pendingApprovals: 9,

  paymentExposure: 18470000,

  riskDistribution: [
    {
      name: "Low",
      value: 171,
    },
    {
      name: "Medium",
      value: 56,
    },
    {
      name: "High",
      value: 17,
    },
    {
      name: "Critical",
      value: 4,
    },
  ],

  criticalVendors: [
    {
      id: "V-1001",
      name: "ABC Industrial Pvt Ltd",
      riskScore: 88,
      riskLevel: "CRITICAL",
      lastChange: "18 Sep 2026",
      paymentExposure: 870000,
      signal:
        "Recent bank change + shared identity",
    },

    {
      id: "V-1023",
      name: "Metro Components Ltd",
      riskScore: 84,
      riskLevel: "HIGH",
      lastChange: "19 Sep 2026",
      paymentExposure: 640000,
      signal:
        "Shared bank relationship",
    },

    {
      id: "V-0981",
      name: "Apex Trading Co",
      riskScore: 81,
      riskLevel: "HIGH",
      lastChange: "14 Sep 2026",
      paymentExposure: 420000,
      signal:
        "GSTIN match with another vendor",
    },

    {
      id: "V-1108",
      name: "Northstar Supplies",
      riskScore: 79,
      riskLevel: "HIGH",
      lastChange: "17 Sep 2026",
      paymentExposure: 315000,
      signal:
        "Unusual payment velocity",
    },
  ],
};

export const mockVendors = [
  {
    id: "V-1001",
    name: "ABC Industrial Pvt Ltd",
    gstin: "29AABCA1001A1Z5",
    bankAccount: "••••9012",
    riskScore: 88,
    riskLevel: "CRITICAL",
    lastChange: "18 Sep 2026",
  },

  {
    id: "V-1002",
    name: "Brightline Components",
    gstin: "29AABCB1002A1Z6",
    bankAccount: "••••0123",
    riskScore: 22,
    riskLevel: "LOW",
    lastChange: "12 Aug 2026",
  },

  {
    id: "V-1003",
    name: "Metro Components Ltd",
    gstin: "27AABCM1003A1Z7",
    bankAccount: "••••1234",
    riskScore: 84,
    riskLevel: "HIGH",
    lastChange: "19 Sep 2026",
  },

  {
    id: "V-1004",
    name: "Apex Trading Co",
    gstin: "36AABCA1004A1Z8",
    bankAccount: "••••2345",
    riskScore: 81,
    riskLevel: "HIGH",
    lastChange: "14 Sep 2026",
  },

  {
    id: "V-1005",
    name: "Northstar Supplies",
    gstin: "36AABCN1005A1Z9",
    bankAccount: "••••3456",
    riskScore: 79,
    riskLevel: "HIGH",
    lastChange: "17 Sep 2026",
  },

  {
    id: "V-1006",
    name: "Greenfield Logistics",
    gstin: "33AABCG1006A1Z0",
    bankAccount: "••••4567",
    riskScore: 54,
    riskLevel: "MEDIUM",
    lastChange: "10 Sep 2026",
  },

  {
    id: "V-1007",
    name: "Sunrise Office Systems",
    gstin: "36AABCS1007B1Z1",
    bankAccount: "••••5678",
    riskScore: 18,
    riskLevel: "LOW",
    lastChange: "22 Jul 2026",
  },

  {
    id: "V-1008",
    name: "Vertex Engineering Works",
    gstin: "27AABCV1008B1Z2",
    bankAccount: "••••6789",
    riskScore: 47,
    riskLevel: "MEDIUM",
    lastChange: "05 Sep 2026",
  },

  {
    id: "V-1009",
    name: "Prime Industrial Services",
    gstin: "29AABCP1009B1Z3",
    bankAccount: "••••7890",
    riskScore: 26,
    riskLevel: "LOW",
    lastChange: "29 Aug 2026",
  },

  {
    id: "V-1010",
    name: "Silverline Distributors",
    gstin: "36AABCS1010B1Z4",
    bankAccount: "••••5566",
    riskScore: 61,
    riskLevel: "MEDIUM",
    lastChange: "16 Sep 2026",
  },
];

export const mockApprovals = [
  {
    transactionId: "T-5001",
    vendorId: "V-1001",
    vendorName: "ABC Industrial Pvt Ltd",
    amount: 870000,
    riskLevel: "CRITICAL",
    riskScore: 88,
    reason:
      "Recent bank change + shared banking relationship",
    status: "PENDING",
  },

  {
    transactionId: "T-5003",
    vendorId: "V-1003",
    vendorName: "Metro Components Ltd",
    amount: 640000,
    riskLevel: "HIGH",
    riskScore: 84,
    reason:
      "Shared bank relationship",
    status: "PENDING",
  },

  {
    transactionId: "T-5004",
    vendorId: "V-1004",
    vendorName: "Apex Trading Co",
    amount: 420000,
    riskLevel: "HIGH",
    riskScore: 81,
    reason:
      "Shared GSTIN relationship",
    status: "PENDING",
  },

  {
    transactionId: "T-5005",
    vendorId: "V-1005",
    vendorName: "Northstar Supplies",
    amount: 315000,
    riskLevel: "HIGH",
    riskScore: 79,
    reason:
      "Unusual payment velocity",
    status: "PENDING",
  },
];

export const mockAuditLogs = [
  {
    id: "AUD-001",
    time: "20 Sep 2026 10:42",
    actor: "Finance Admin",
    action: "Risk detected",
    entity: "V-1001",
    details:
      "Critical risk score generated for ABC Industrial Pvt Ltd.",
  },

  {
    id: "AUD-002",
    time: "20 Sep 2026 10:38",
    actor: "Risk Engine",
    action: "Signal detected",
    entity: "V-1001",
    details:
      "Recent bank account change detected.",
  },

  {
    id: "AUD-003",
    time: "19 Sep 2026 16:20",
    actor: "Risk Engine",
    action: "Relationship detected",
    entity: "V-1003",
    details:
      "Shared bank relationship detected.",
  },

  {
    id: "AUD-004",
    time: "18 Sep 2026 12:15",
    actor: "Finance Admin",
    action: "Vendor updated",
    entity: "V-1001",
    details:
      "Bank account information changed.",
  },
];