from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(50), unique=True, nullable=False, index=True)

    email = Column(String(100), unique=True, nullable=False, index=True)

    hashed_password = Column(String(255), nullable=False)

    full_name = Column(String(100), nullable=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # TODO: Uncomment after RecipeHistory and FavoriteRecipe models are implemented.
    
    # Relationships

    # recipes = relationship(
    #     "Recipe",
    #     back_populates="user",
    #     cascade="all, delete-orphan"
    # )

    # recipe_history = relationship(
    #     "RecipeHistory",
    #     back_populates="user",
    #     cascade="all, delete-orphan"
    # )

    # favorite_recipes = relationship(
    #     "FavoriteRecipe",
    #     back_populates="user",
    #     cascade="all, delete-orphan"
    # )