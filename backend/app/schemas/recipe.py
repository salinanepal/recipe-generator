from pydantic import BaseModel, ConfigDict
from typing import Optional


# Request sent by the frontend
class RecipeGenerateRequest(BaseModel):
    ingredients: list[str]
    cuisine: Optional[str] = None
    meal_type: Optional[str] = None
    servings: Optional[int] = None


# Response returned by the backend
class RecipeResponse(BaseModel):
    id: int
    title: str
    ingredients: str
    instructions: str
    cooking_time: Optional[int]
    servings: Optional[int]
    user_id: int

    model_config = ConfigDict(from_attributes=True)