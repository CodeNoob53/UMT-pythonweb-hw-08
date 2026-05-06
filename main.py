from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers import contacts

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Contacts API",
    description="REST API for managing contacts",
    version="1.0.0",
)

app.include_router(contacts.router)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok"}
