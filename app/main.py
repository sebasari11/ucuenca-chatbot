from fastapi import FastAPI
from app.api.routes import (
    health_api,
    ingest_api,
    source_api,
    chat_api,
    chunck_api,
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

app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG)


@app.on_event("startup")
async def on_startup():
    await init_db()
    await test_connection()


# Base.metadata.create_all(bind=engine)
app.include_router(health_api.router)
app.include_router(source_api.router)
app.include_router(ingest_api.router)
app.include_router(chat_api.router)
app.include_router(chunck_api.router)
app.include_router(user_api.router)
