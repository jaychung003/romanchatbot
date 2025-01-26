import os
from phoenix.server import serve

if __name__ == "__main__":
    # Start the Phoenix server
    serve(
        host="0.0.0.0",
        port=6006,
        allow_origin="*",
        log_level="info"
    )