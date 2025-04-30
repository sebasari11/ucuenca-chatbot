from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError
import asyncio

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)
# DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, future=True)


async def test_connection():
    try:
        async with engine.connect() as connection:
            logger.info("✅ Conexión exitosa a la base de datos")
    except OperationalError as e:
        logger.critical("❌ No se pudo conectar a la base de datos:")
        logger.critical(str(e))
        raise Exception("Error al conectar con la base de datos") from e


# Create async session factory
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Create declarative base for models
Base = declarative_base()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session():
    """Dependency for getting async database session.

    Yields:
        AsyncSession: Async database session
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
