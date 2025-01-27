import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Roman Empire Chatbot Monitor",
    description="Monitoring interface for the Roman Empire chatbot using Phoenix",
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
os.makedirs(templates_dir, exist_ok=True)
templates = Jinja2Templates(directory=templates_dir)

# Phoenix session holder
phoenix_url = None

def init_phoenix():
    """Initialize Phoenix session"""
    try:
        import phoenix as px
        global phoenix_url
        logger.info("Starting Phoenix session...")
        session = px.launch_app()
        phoenix_url = session.url
        logger.info(f"Phoenix initialized at {phoenix_url}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Phoenix: {str(e)}")
        return False

@app.on_event("startup")
async def startup_event():
    """Initialize Phoenix on FastAPI startup"""
    init_phoenix()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint serving the Phoenix monitoring dashboard"""
    try:
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "phoenix_url": phoenix_url if phoenix_url else "",
                "server_status": "Connected" if phoenix_url else "Error"
            }
        )
    except Exception as e:
        logger.error(f"Template error: {str(e)}")
        logger.error(f"Templates directory: {templates_dir}")
        logger.error(f"Current working directory: {os.getcwd()}")
        return HTMLResponse(
            content=f"""
            <html>
                <body>
                    <h1>Error Loading Dashboard</h1>
                    <p>Status: Error</p>
                    <p>Details: {str(e)}</p>
                </body>
            </html>
            """,
            status_code=500
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if phoenix_url else "unhealthy",
        "phoenix_url": phoenix_url
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global exception handler caught: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

def main():
    """Main entry point"""
    try:
        logger.info("Starting monitoring server...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=6008,
            log_level="debug"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise

if __name__ == "__main__":
    main()