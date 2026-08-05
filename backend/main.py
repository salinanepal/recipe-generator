from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text


from app.core.database import Base, engine
from app.models.user import User
from app.models.recipe import Recipe
from app.models.favorite import Favorite

from app.routers.auth import router as auth_router 
from app.routers.recipes import router as recipe_router
from app.routers.history import router as history_router
from app.routers.favorites import router as favorite_router

from app.models import recipe, user

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Recipe Generator API",
    version="1.0.0",
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
        "http://localhost:5174",
    "http://127.0.0.1:5174",
        "http://localhost:5175",
    "http://127.0.0.1:5175",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(recipe_router)
app.include_router(history_router)
app.include_router(favorite_router)

@app.get("/")
def home():
    return {
        "message": "Recipe Generator API is running"
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