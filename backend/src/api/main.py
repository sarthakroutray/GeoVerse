from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from src.utils.config import settings

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="GeoVerse API",
    description="AI-powered geospatial question-answering system for MOSDAC data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS dynamically
_origins = list(settings.allowed_origins)
frontend_url_env = os.getenv("FRONTEND_URL")
if frontend_url_env and frontend_url_env not in _origins:
    _origins.append(frontend_url_env.rstrip('/'))

vercel_url = os.getenv("VERCEL_URL")  # When running on Vercel (preview)
if vercel_url:
    if not vercel_url.startswith("http"):
        vercel_url = f"https://{vercel_url}"
    if vercel_url not in _origins:
        _origins.append(vercel_url.rstrip('/'))

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to GeoVerse API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "geoverse-backend"
    }

# Import and include routers
from .routes import chat, search

app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
