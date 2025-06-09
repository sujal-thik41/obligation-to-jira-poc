from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI(title="Legal Obligation Extraction")

# Register the API router under /api/v1 prefix
app.include_router(api_router, prefix="/api/v1")
