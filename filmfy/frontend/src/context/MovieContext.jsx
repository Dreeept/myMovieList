// filmfy/frontend/src/context/MovieContext.jsx
import React, {
  createContext,
  useState,
  useEffect,
  useCallback,
  useContext,
} from "react";
import axios from "axios"; // <-- Import axios
import { useAuth } from "./AuthContext"; // <-- Import useAuth untuk logout
import { useNavigate } from "react-router-dom"; // <-- Import useNavigate

export const MoviesContext = createContext();

// Hapus API_URL, karena kita sudah set baseURL di axios
// const API_URL = "http://127.0.0.1:6543/api/movies";

export function MoviesProvider({ children }) {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { logout } = useAuth(); // <-- Ambil fungsi logout
  // Tidak bisa pakai useNavigate di sini, kita akan handle di komponen pemanggil

  // Fungsi helper untuk menangani error 401/403
  const handleAuthError = useCallback(
    async (err) => {
      if (
        err.response &&
        (err.response.status === 401 || err.response.status === 403)
      ) {
        console.error("Authentication Error - Logging out:", err);
        await logout();
        // Navigasi akan dilakukan di komponen yang memanggil
        return true; // Mengindikasikan error auth terjadi
      }
      return false; // Bukan error auth
    },
    [logout]
  );

  const fetchMovies = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Gunakan axios, cukup pakai path relatif karena baseURL sudah di-set
      const response = await axios.get("/movies");
      setMovies(Array.isArray(response.data) ? response.data : []);
    } catch (e) {
      console.error("Failed to fetch movies:", e);
      if (!(await handleAuthError(e))) {
        setError("Gagal memuat data film.");
      }
      setMovies([]);
    } finally {
      setLoading(false);
    }
  }, [handleAuthError]); // <-- Tambah dependensi

  useEffect(() => {
    fetchMovies();
  }, [fetchMovies]);

  const addMovie = async (formData) => {
    try {
      // Gunakan axios.post
      const response = await axios.post("/movies", formData, {
        headers: { "Content-Type": "multipart/form-data" }, // axios biasanya handle ini, tapi eksplisit lebih baik
      });
      if (response.status === 201) {
        // <-- Cek status 201 Created
        await fetchMovies();
        return { success: true };
      }
      throw new Error("Failed to add movie (unexpected response).");
    } catch (e) {
      console.error("Failed to add movie:", e);
      await handleAuthError(e); // <-- Handle auth error
      return { success: false, error: e.response?.data?.error || e.message };
    }
  };

  const updateMovie = async (movieId, formData) => {
    try {
      // Gunakan axios.post (karena backend pakai POST)
      const response = await axios.post(`/movies/${movieId}`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      if (response.status === 200) {
        // <-- Cek status 200 OK
        await fetchMovies();
        return { success: true };
      }
      throw new Error("Failed to update movie (unexpected response).");
    } catch (e) {
      console.error("Failed to update movie:", e);
      await handleAuthError(e); // <-- Handle auth error
      return { success: false, error: e.response?.data?.error || e.message };
    }
  };

  const deleteMovie = async (movieId) => {
    try {
      // Gunakan axios.delete
      const response = await axios.delete(`/movies/${movieId}`);
      if (response.status === 204) {
        // <-- Cek status 204 No Content
        await fetchMovies();
        return { success: true };
      }
      throw new Error("Failed to delete movie (unexpected response).");
    } catch (e) {
      console.error("Failed to delete movie:", e);
      await handleAuthError(e); // <-- Handle auth error
      return { success: false, error: e.response?.data?.error || e.message };
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
        fetchMovies, // <-- Export juga fetchMovies jika perlu refresh manual
      }}
    >
      {children}
    </MoviesContext.Provider>
  );
}
