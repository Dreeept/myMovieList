import React, { createContext, useState, useEffect, useCallback } from "react";
// Hapus import LocalStorage
// import { loadMovies, saveMovies } from "../utils/LocalStorage";

export const MoviesContext = createContext();

// Definisikan Base URL API Anda
const API_URL = "http://127.0.0.1:6543/api/movies";

export function MoviesProvider({ children }) {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true); // Tambah state loading
  const [error, setError] = useState(null); // Tambah state error

  // Fungsi untuk mengambil data film dari backend
  const fetchMovies = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(API_URL);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      // Pastikan data adalah array
      setMovies(Array.isArray(data) ? data : []);
    } catch (e) {
      console.error("Failed to fetch movies:", e);
      setError("Gagal memuat data film.");
      setMovies([]); // Kosongkan jika error
    } finally {
      setLoading(false);
    }
  }, []);

  // Panggil fetchMovies saat komponen pertama kali dimuat
  useEffect(() => {
    fetchMovies();
  }, [fetchMovies]);

  // Hapus useEffect untuk saveMovies ke LocalStorage

  // Fungsi untuk menambah film baru
  const addMovie = async (formData) => {
    // Terima FormData
    try {
      const response = await fetch(API_URL, {
        method: "POST",
        body: formData, // Langsung kirim FormData (tanpa header Content-Type)
      });
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(
          errData.error || `HTTP error! status: ${response.status}`
        );
      }
      // Ambil data baru dan refresh daftar film
      await fetchMovies();
      return { success: true };
    } catch (e) {
      console.error("Failed to add movie:", e);
      return { success: false, error: e.message };
    }
  };

  // Fungsi untuk mengedit film
  const updateMovie = async (movieId, formData) => {
    // Terima ID dan FormData
    try {
      const response = await fetch(`${API_URL}/${movieId}`, {
        method: "POST", // Ingat kita pakai POST untuk update
        body: formData, // Langsung kirim FormData
      });
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(
          errData.error || `HTTP error! status: ${response.status}`
        );
      }
      await fetchMovies(); // Refresh
      return { success: true };
    } catch (e) {
      console.error("Failed to update movie:", e);
      return { success: false, error: e.message };
    }
  };

  // Fungsi untuk menghapus film
  const deleteMovie = async (movieId) => {
    try {
      const response = await fetch(`${API_URL}/${movieId}`, {
        method: "DELETE",
      });
      if (!response.ok && response.status !== 204) {
        // 204 juga OK
        const errData = await response.json();
        throw new Error(
          errData.error || `HTTP error! status: ${response.status}`
        );
      }
      // Hapus dari state atau refresh dari server
      // setMovies(prevMovies => prevMovies.filter(movie => movie.id !== movieId));
      await fetchMovies(); // Lebih mudah refresh
      return { success: true };
    } catch (e) {
      console.error("Failed to delete movie:", e);
      return { success: false, error: e.message };
    }
  };

  return (
    <MoviesContext.Provider
      value={{
        movies,
        loading,
        error,
        addMovie,
        updateMovie,
        deleteMovie,
      }}
    >
      {children}
    </MoviesContext.Provider>
  );
}
