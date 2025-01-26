import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List, Dict, Any
import json

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Phoenix Server",
    description="Feedback and tracing server for Roman Empire Chat",
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

# Store feedback and traces in memory
stored_feedback = []
stored_traces = []

# Update port configuration
PORT = int(os.environ.get("PHOENIX_PORT", 6007))
logger.info(f"Phoenix server will start on port {PORT}")

# Define routes in correct order (specific routes first, catch-all last)
@app.get("/")
async def root():
    """Root endpoint that shows server status"""
    logger.info("Accessed root endpoint")
    return {
        "status": "running",
        "server": "Phoenix",
        "version": "1.0.0",
        "endpoints": {
            "root": "/",
            "traces": "/v1/traces",
            "feedback": "/v1/span_annotations",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/v1/traces")
async def receive_traces(request: Request):
    """Endpoint to receive and store traces"""
    try:
        # Get raw bytes first
        body = await request.body()
        try:
            # Try JSON decode first
            trace_data = json.loads(body)
        except UnicodeDecodeError:
            # If Unicode decode fails, store raw bytes
            trace_data = {"raw_data": str(body.hex())}
        except json.JSONDecodeError:
            # If JSON decode fails, store as string
            trace_data = {"raw_data": body.decode('latin1')}

        logger.info(f"Received trace data type: {type(trace_data)}")
        stored_traces.append(trace_data)
        return {"status": "success", "message": "Trace data stored"}
    except Exception as e:
        logger.error(f"Error processing trace: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/span_annotations")
async def receive_annotations(request: Request):
    """Endpoint to receive and store feedback annotations"""
    try:
        feedback_data = await request.json()
        logger.info(f"Received feedback annotation: {feedback_data}")
        stored_feedback.append(feedback_data)
        return {"status": "success", "message": "Feedback stored"}
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/feedback")
async def get_feedback():
    """Endpoint to view all stored feedback"""
    return {"feedback": stored_feedback}

@app.get("/traces")
async def get_traces():
    """Endpoint to view all stored traces"""
    return {"traces": stored_traces}

# Move catch-all route to the end
@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(request: Request, path_name: str):
    """Catch-all route handler for unsupported endpoints"""
    logger.warning(f"Attempted to access unsupported endpoint: {path_name}")
    if path_name == "":  # Empty path should redirect to root
        return await root()
    raise HTTPException(
        status_code=404,
        detail=f"Endpoint '/{path_name}' not found. Available endpoints: /, /health, /v1/traces, /v1/span_annotations"
    )

if __name__ == "__main__":
    try:
        logger.info(f"Starting Phoenix server on port {PORT}...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=PORT,
            log_level="debug"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}", exc_info=True)
        raise