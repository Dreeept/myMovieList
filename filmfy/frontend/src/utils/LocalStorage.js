// src/utils/LocalStorage.js

const STORAGE_KEY = "movies";

// Simpan data ke localStorage
export function saveMovies(movies) {
  try {
    const json = JSON.stringify(movies);
    localStorage.setItem(STORAGE_KEY, json);
  } catch (error) {
    console.error("Error saving movies to localStorage:", error);
  }
}

// Baca data dari localStorage
export function loadMovies() {
  try {
    const json = localStorage.getItem(STORAGE_KEY);
    if (!json) return [];
    return JSON.parse(json);
  } catch (error) {
    console.error("Error loading movies from localStorage:", error);
    return [];
  }
}

// Hapus data localStorage (opsional)
export function clearMovies() {
  localStorage.removeItem(STORAGE_KEY);
}
