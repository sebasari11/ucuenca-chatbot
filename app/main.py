from fastapi import FastAPI
from app.api.routes import router
from app.api.sources import source_router
from app.database import Base, engine


app = FastAPI(title="Chatbot UCUENCA - G.I Software")
Base.metadata.create_all(bind=engine)
app.include_router(router)
app.include_router(source_router)


@app.get("/health")
def health():
    return {"status": "ok"}
