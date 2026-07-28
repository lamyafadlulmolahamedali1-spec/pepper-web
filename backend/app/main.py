"""Pepper Clinical Infinity V6 — Main API. © 2026 Lamya F. H. Ali"""
import os, time, logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api import auth, billing, sessions, clinical

os.makedirs("logs", exist_ok=True)
logging.basicConfig(level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.FileHandler("logs/pepper.log"), logging.StreamHandler()])
log=logging.getLogger("pepper")

@asynccontextmanager
async def lifespan(app):
    log.info("Starting Pepper Clinical Infinity V6...")
    init_db(); log.info("Database ready."); yield
    log.info("Shutdown.")

app=FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION,
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None, openapi_url=None if settings.is_production else "/openapi.json",
    lifespan=lifespan)

class SecHeaders(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        r=await call_next(request)
        r.headers["X-Content-Type-Options"]="nosniff"
        r.headers["X-Frame-Options"]="DENY"
        r.headers["Referrer-Policy"]="strict-origin-when-cross-origin"
        if settings.is_production:
            r.headers["Strict-Transport-Security"]="max-age=31536000; includeSubDomains"
        return r

app.add_middleware(SecHeaders)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(CORSMiddleware, allow_origins=settings.origins_list,
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.exception_handler(Exception)
async def err(request: Request, exc: Exception):
    log.error(f"Error {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(status_code=500,
        content={"detail":"Internal error" if settings.is_production else str(exc)})

app.include_router(auth.router)
app.include_router(billing.router)
app.include_router(sessions.router)
app.include_router(clinical.router)

@app.get("/health")
def health(): return {"status":"healthy","version":settings.APP_VERSION}

@app.get("/api")
def api_info(): return {"app":settings.APP_NAME,"version":settings.APP_VERSION,"status":"running"}
