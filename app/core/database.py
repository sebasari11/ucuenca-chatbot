from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from app.core.config import settings

DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

print("DATABASE_URL =>   ", DATABASE_URL)

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        print("✅ Conexión exitosa a la base de datos")

except OperationalError as e:
    print("❌ No se pudo conectar a la base de datos:")
    print(str(e))
    # Puedes lanzar una excepción personalizada si quieres que falle la app
    raise Exception("Error al conectar con la base de datos") from e

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
