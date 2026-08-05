from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime



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

# --- History module ---

class RecipeSummary(BaseModel):
    id: int
    title: str
    cooking_time: Optional[int] = None
    servings: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecipeDetail(RecipeSummary):
    ingredients: str
    instructions: str