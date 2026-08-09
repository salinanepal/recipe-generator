from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# Request from frontend to find recommended recipes
class RecipeGenerateRequest(BaseModel):
    ingredients: list[str]
    servings: Optional[int] = 2

# Request when user selects a recommended recipe
class RecipeSelectionRequest(BaseModel):
    recipe_name: str
    ingredients: list[str]
    servings: Optional[int] = 2

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
    cuisine: Optional[str] = None
    recipe_type: Optional[str] = None
    cooking_tips: Optional[str] = None

# --- Favorites module ---

class FavoriteResponse(BaseModel):
    id: int
    recipe_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FavoriteRecipe(BaseModel):
    id: int
    title: str
    cooking_time: Optional[int] = None
    servings: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)