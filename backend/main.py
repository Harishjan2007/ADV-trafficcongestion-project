"""
FastAPI Server Entry Point: Chennai Traffic Intelligence Platform
"""

import logging
from backend.fastapi_compat import FastAPI, CORSMiddleware
from backend.api.routes_traffic import router as traffic_router
from backend.api.routes_analytics import router as analytics_router
from backend.api.routes_insights import router as insights_router
from backend.api.routes_ml import router as ml_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("chennai_traffic_backend")

app = FastAPI(
    title="Chennai Traffic Intelligence & Multidimensional Visualization Platform API",
    description="High-performance analytics, geospatial data services, and ML prediction endpoints for Chennai Traffic Authorities.",
    version="1.0.0"
)

# Enable CORS for local React/Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Sub-Routers
app.include_router(traffic_router)
app.include_router(analytics_router)
app.include_router(insights_router)
app.include_router(ml_router)

# Preload Multi-City ML Engines
try:
    from backend.services.ml_engine import MultiCityMLEngine
    MultiCityMLEngine.get_instance()
except Exception as e:
    logger.warning(f"Could not initialize MultiCityMLEngine at startup: {e}")


import os
try:
    from fastapi.responses import FileResponse, HTMLResponse
except Exception:
    FileResponse, HTMLResponse = None, None


@app.get("/")
@app.get("/index.html")
def serve_index():
    index_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "index.html"))
    if os.path.exists(index_path):
        if FileResponse is not None:
            return FileResponse(index_path)
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        if HTMLResponse is not None:
            return HTMLResponse(content)
        return content
    return {
        "status": "healthy",
        "service": "Chennai Traffic Intelligence Platform",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Chennai Traffic Intelligence API",
        "version": "1.0.0",
        "environment": "development"
    }


if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
    except ImportError:
        print("Uvicorn not installed. Please run: pip install uvicorn fastapi")
