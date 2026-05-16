from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.core.database import init_db, close_db
from app.routers import chat, auth, appointments, businesses, calendar, staff, admin, demo_requests


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db(app)
    yield
    await close_db(app)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(appointments.router)
app.include_router(businesses.router)
app.include_router(calendar.router)
app.include_router(staff.router)
app.include_router(admin.router)
app.include_router(demo_requests.router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}
