import os
import logging
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from phoenix.otel import register
from opentelemetry import trace

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

# Configure Phoenix server URL and tracer
PHOENIX_SERVER_URL = "http://localhost:6006"
TRACER = None

def init_phoenix():
    """Initialize Phoenix and OpenTelemetry"""
    try:
        global TRACER
        logger.info("Configuring Phoenix tracer...")

        # Configure the Phoenix tracer with the correct endpoint
        # Using HTTP/OTLP since gRPC is failing
        tracer_provider = register(
            endpoint="http://localhost:6006/v1/traces",
            protocol="http/protobuf"  # Use HTTP instead of gRPC
        )

        # Get tracer for this service
        TRACER = trace.get_tracer(__name__)
        logger.info("Phoenix tracer configured successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to configure Phoenix tracer: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    """Initialize Phoenix on startup"""
    init_phoenix()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint serving the UI dashboard"""
    with TRACER.start_as_current_span("root_request") as span:
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
            # Check if template exists
            template_path = os.path.join(templates_dir, "dashboard.html")
            if not os.path.exists(template_path):
                logger.error(f"Template not found at {template_path}")
                raise HTTPException(status_code=500, detail=f"Template not found: {template_path}")

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
    with TRACER.start_as_current_span("health_check") as span:
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
        logger.info("Starting Phoenix UI server...")
        uvicorn.run(
            "phoenix_combined:app",  # Use string reference to avoid reload issues
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