from fastapi import FastAPI
from app.api import health, sources, ingest
from app.database import Base, engine


app = FastAPI(title="Chatbot UCUENCA - G.I Software")
Base.metadata.create_all(bind=engine)
app.include_router(health.router)
app.include_router(sources.router)
app.include_router(ingest.router)
