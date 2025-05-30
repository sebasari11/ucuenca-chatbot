from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.routes import (
    #   chunk_api,
    health_api,
    #  chat_api,
)
from app.core.database import init_db, test_connection
from app.core.config import settings
from app.core.logging import get_logger, setup_logging

from app.src.users.routes import router as users_router
from app.src.resources.routes import router as resources_router
from app.src.chunks.routes import router as chunks_router
from app.src.chats.routes import router as chats_router

# Set up logging configuration
setup_logging()

# # Optional: Run migrations on startup
# run_migrations()

# Set up logger for this module
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await test_connection()
    yield


app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_api.router)
app.include_router(users_router)
app.include_router(resources_router)
app.include_router(chunks_router)
app.include_router(chats_router)
