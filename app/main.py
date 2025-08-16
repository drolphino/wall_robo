from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database.init_db import init_db
from app.routers import walls, trajectory
from app.middleware.logging import log_requests

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.middleware("http")(log_requests)

# Serve static frontend
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# Initialize database
init_db()

# Include routers
app.include_router(walls.router)
app.include_router(trajectory.router)







