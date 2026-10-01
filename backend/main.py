from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import upload, risk, graph, dashboard


app = FastAPI(
    title="VendorTrust API",
    description="Backend API for Vendor Shield VendorTrust application",
    version="1.0.0",
)


# Configure CORS for the Vite/React frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# INCLUDE ROUTERS
# ============================================================

# The upload router defines its own prefix as "/upload".
# The frontend api.js expects POST /api/upload.
# Therefore, we mount it with the "/api" prefix here.
app.include_router(upload.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")

# The risk and graph routers already define their own prefix as "/api/vendors".
# Therefore, we mount them at the root level without an additional prefix.
app.include_router(risk.router)
app.include_router(graph.router)
