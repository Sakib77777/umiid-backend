from fastapi import FastAPI

from app.firebase import db
from app.routes.auth import router as auth_router
from app.routes.sessions import router as sessions_router
from app.routes.users import router as users_router


# Create FastAPI application


app = FastAPI(
    title="Umiid API",
    description="Umiid Backend API using Python, FastAPI and Firebase",
    version="1.0.0"
)


# Root API

@app.get("/")
def root():

    return {
        "success": True,
        "message": "Umiid Python API is running"
    }


# Authentication Routes

app.include_router(auth_router)

# User Profile Routes

app.include_router(users_router)

# Counseling Session Routes

app.include_router(sessions_router)