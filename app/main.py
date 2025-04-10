from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Chatbot UCUENCA - G.I Software")
app.include_router(router)