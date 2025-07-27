from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import upload, files
from app.database import engine
from app.models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Secure Video Upload API",
    description="API for secure video upload with encryption",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(files.router, prefix="/api", tags=["files"])

@app.get("/")
async def root():
    return {"message": "Secure Video Upload API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 