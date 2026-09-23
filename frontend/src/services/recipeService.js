import api from "./api";

export const recommendRecipes = async (data) => {
  const response = await api.post(
    "/recipes/recommend",
    data
  );

  return response.data;
};

export const generateSelectedRecipe = async (
  data
) => {
  const response = await api.post(
    "/recipes/generate-selected",
    data
  );

  return response.data;
};

export const getHistory = async () => {
  const response = await api.get(
    "/history/"
  );

  return response.data;
};

export const getRecipeDetail = async (id) => {
  const response = await api.get(
    `/history/${id}`
  );

  return response.data;
};

export const deleteRecipeFromHistory = async (
  id
) => {
  await api.delete(`/history/${id}`);
};

export const getFavorites = async () => {
  const response = await api.get(
    "/favorites/"
  );

  return response.data;
};

export const addFavorite = async (
  recipeId
) => {
  const response = await api.post(
    `/favorites/${recipeId}`
  );

  return response.data;
};

export const removeFavorite = async (
  recipeId
) => {
  await api.delete(`/favorites/${recipeId}`);
};

export const getRecipeCandidates = async (ingredients, servings) => {
  const response = await api.post("/recipes/candidates", { ingredients, servings });
  return response.data; // { candidates, available_styles }
};