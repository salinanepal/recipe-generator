import api from "./api";

export const generateRecipe = async (data) => {
  const response = await api.post("/recipes/generate", data);
  return response.data;
};

export const getHistory = async () => {
  const response = await api.get("/history/");
  return response.data;
};

export const getRecipeDetail = async (id) => {
  const response = await api.get(`/history/${id}`);
  return response.data;
};

export const deleteRecipeFromHistory = async (id) => {
  await api.delete(`/history/${id}`);
};