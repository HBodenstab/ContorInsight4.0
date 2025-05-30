from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import organizations, uploads, reports

app = FastAPI(title="Market Intelligence Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(organizations.router, prefix="/api/v1")
app.include_router(uploads.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Market Intelligence Platform API", "version": "1.0.0"} 