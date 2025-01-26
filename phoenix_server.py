import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI()

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

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/v1/traces")
async def receive_traces(request: Request):
    try:
        trace_data = await request.json()
        logger.info(f"Received trace data: {trace_data}")
        stored_traces.append(trace_data)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing trace: {str(e)}", exc_info=True)
        raise

@app.post("/v1/span_annotations")
async def receive_annotations(request: Request):
    try:
        feedback_data = await request.json()
        logger.info(f"Received feedback annotation: {feedback_data}")
        stored_feedback.append(feedback_data)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}", exc_info=True)
        raise

@app.get("/feedback")
async def get_feedback():
    """Endpoint to view all stored feedback"""
    return {"feedback": stored_feedback}

@app.get("/traces")
async def get_traces():
    """Endpoint to view all stored traces"""
    return {"traces": stored_traces}

if __name__ == "__main__":
    try:
        logger.info("Starting Phoenix server...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=6006,
            log_level="debug"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}", exc_info=True)
        raise