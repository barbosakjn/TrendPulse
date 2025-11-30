from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

def setup_cors(app: FastAPI):
    allowed_origins = [
        "http://localhost:5000",
        "http://0.0.0.0:5000",
        "http://127.0.0.1:5000",
    ]
    
    replit_domain = os.getenv("REPLIT_DEV_DOMAIN")
    if replit_domain:
        allowed_origins.append(f"https://{replit_domain}")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600,
    )
