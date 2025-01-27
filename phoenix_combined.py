import os
import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import httpx
from phoenix.otel import register
from opentelemetry import trace

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get absolute path for templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(BASE_DIR, "templates")

# Create templates directory if it doesn't exist
os.makedirs(templates_dir, exist_ok=True)
logger.info(f"Creating templates directory at {templates_dir}")

# Set up Jinja2 templates with absolute path
logger.info("Initializing Jinja2 templates")
templates = Jinja2Templates(directory=templates_dir)

# Configure Phoenix server URL
PHOENIX_SERVER_URL = "http://0.0.0.0:6006"

def wait_for_phoenix_server(max_retries=5, retry_delay=2):
    """Wait for Phoenix server to be ready"""
    for attempt in range(max_retries):
        try:
            with httpx.Client() as client:
                response = client.get(f"{PHOENIX_SERVER_URL}/health")
                if response.status_code == 200:
                    logger.info("Phoenix server is ready")
                    return True
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{max_retries}: Phoenix server not ready: {e}")
        time.sleep(retry_delay)
    return False

def init_phoenix():
    """Initialize Phoenix and OpenTelemetry"""
    try:
        logger.info("Starting Phoenix session...")

        # Wait for Phoenix server
        if not wait_for_phoenix_server():
            logger.error("Phoenix server not available after max retries")
            return None

        # Configure the Phoenix tracer with the HTTP/OTLP endpoint
        tracer_provider = register(
            endpoint="http://0.0.0.0:4317",  # Use gRPC endpoint
            protocol="grpc"                  # Use gRPC protocol
        )

        # Get the global tracer
        tracer = trace.get_tracer(__name__, tracer_provider=tracer_provider)
        logger.info("Phoenix tracer initialized successfully")
        return tracer
    except Exception as e:
        logger.error(f"Failed to initialize Phoenix: {e}")
        return None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application"""
    # Initialize Phoenix and store tracer in app state
    app.state.tracer = init_phoenix()
    yield
    # Cleanup on shutdown if needed

# Create FastAPI app with lifespan
app = FastAPI(
    title="Phoenix UI",
    description="Web interface for Phoenix tracing and feedback",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint serving the UI dashboard"""
    tracer = request.app.state.tracer
    if not tracer:
        logger.error("Tracer not initialized")
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "server_status": "Error - Tracer not initialized",
                "server_url": PHOENIX_SERVER_URL
            }
        )

    with tracer.start_as_current_span("root_request") as span:
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
                span.set_attribute("server_status", server_status)
        except Exception as e:
            logger.error(f"Failed to connect to Phoenix server: {e}")
            server_status = "Error"
            span.set_attribute("error", str(e))

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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    tracer = app.state.tracer
    if not tracer:
        return {"status": "unhealthy", "reason": "tracer not initialized"}

    with tracer.start_as_current_span("health_check") as span:
        span.set_attribute("endpoint", "/health")
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
        logger.info("Starting monitoring server...")
        uvicorn.run(
            "phoenix_combined:app",
            host="0.0.0.0",
            port=6008,
            reload=True,
            log_level="debug"
        )
    except Exception as e:
        logger.error(f"Failed to start Phoenix UI server: {e}")
        raise

if __name__ == "__main__":
    main()