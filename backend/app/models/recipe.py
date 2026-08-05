from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

from app.core.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)

    ingredients = Column(Text, nullable=False)

    instructions = Column(Text, nullable=False)

    cuisine = Column(String(100))

    recipe_type = Column(String(100))

    cooking_tips = Column(Text)

    cooking_time = Column(Integer)

    servings = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationship (comment for now until User model is ready)
    # user = relationship("User", back_populates="recipes")