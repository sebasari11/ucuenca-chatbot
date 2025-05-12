from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import (
    chunk_api,
    health_api,
    source_api,
    chat_api,
    user_api,
)
from app.core.database import init_db, test_connection
from app.core.config import settings
from app.core.logging import get_logger, setup_logging

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

app.include_router(health_api.router)
app.include_router(source_api.router)
app.include_router(chat_api.router)
app.include_router(chunk_api.router)
app.include_router(user_api.router)
