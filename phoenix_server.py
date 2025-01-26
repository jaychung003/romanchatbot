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

if __name__ == "__main__":
    port = 6007  # Define port explicitly
    try:
        logger.info(f"Starting Phoenix server on port {port}...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="debug"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}", exc_info=True)
        raise