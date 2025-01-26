import os
import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import httpx
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Phoenix UI",
    description="Web interface for Phoenix tracing and feedback",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get absolute path for templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(BASE_DIR, "templates")

# Create templates directory if it doesn't exist
os.makedirs(templates_dir, exist_ok=True)

# Set up Jinja2 templates with absolute path
templates = Jinja2Templates(directory=templates_dir)

# Configure Phoenix server URL
PHOENIX_SERVER_URL = "http://0.0.0.0:6007"

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint serving the UI dashboard"""
    try:
        # Test connection to Phoenix server
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{PHOENIX_SERVER_URL}/health")
            if response.status_code == 200:
                logger.info("Successfully connected to Phoenix server")
                server_status = "Connected"
            else:
                logger.warning("Phoenix server health check failed")
                server_status = "Disconnected"
    except Exception as e:
        logger.error(f"Failed to connect to Phoenix server: {e}")
        server_status = "Error"

    try:
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "server_status": server_status,
                "server_url": PHOENIX_SERVER_URL
            }
        )
    except Exception as e:
        logger.error(f"Template error: {str(e)}")
        logger.error(f"Templates directory: {templates_dir}")
        logger.error(f"Current working directory: {os.getcwd()}")
        raise HTTPException(status_code=500, detail=f"Template error: {str(e)}")

@app.get("/traces")
async def get_traces():
    """Fetch traces from Phoenix server"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{PHOENIX_SERVER_URL}/traces")
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Phoenix server returned status {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch traces")
    except httpx.RequestError as e:
        logger.error(f"Failed to fetch traces: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")
    except Exception as e:
        logger.error(f"Unexpected error fetching traces: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/feedback")
async def get_feedback():
    """Fetch feedback from Phoenix server"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{PHOENIX_SERVER_URL}/feedback")
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Phoenix server returned status {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch feedback")
    except httpx.RequestError as e:
        logger.error(f"Failed to fetch feedback: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")
    except Exception as e:
        logger.error(f"Unexpected error fetching feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global exception handler caught: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

def main():
    try:
        logger.info("Starting Phoenix UI server...")
        uvicorn.run(
            "phoenix_ui:app",  # Use string reference to avoid reload issues
            host="0.0.0.0",
            port=6008,
            reload=True,  # Enable auto-reload for development
            log_level="debug"
        )
    except Exception as e:
        logger.error(f"Failed to start Phoenix UI server: {e}")
        raise

if __name__ == "__main__":
    main()