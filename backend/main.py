from fastapi import FastAPI
from sqlalchemy import text

from app.core.database import engine

app = FastAPI(
    title="Recipe Generator API",
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "message": "Recipe Generator API is running 🚀"
    }


@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "success",
            "database": "connected"
        }

    except Exception as e:
        return {
            "status": "error",
            "database": str(e)
        }