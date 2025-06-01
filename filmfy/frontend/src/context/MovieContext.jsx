// filmfy/frontend/src/context/MovieContext.jsx
import React, {
  createContext,
  useState,
  useEffect,
  useCallback,
  useContext,
} from "react";
import axios from "axios";
import { useAuth } from "./AuthContext";

export const MoviesContext = createContext();

const FAVORITES_KEY = "filmfy_favorites"; // <-- Kunci untuk localStorage

export function MoviesProvider({ children }) {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { logout } = useAuth();

  // --- START: Penambahan State & Logika Favorit ---
  const [favoriteIds, setFavoriteIds] = useState(() => {
    try {
      const storedFavorites = localStorage.getItem(FAVORITES_KEY);
      return storedFavorites ? new Set(JSON.parse(storedFavorites)) : new Set();
    } catch (e) {
      console.error("Failed to load favorites from localStorage", e);
      return new Set();
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(
        FAVORITES_KEY,
        JSON.stringify(Array.from(favoriteIds))
      );
    } catch (e) {
      console.error("Failed to save favorites to localStorage", e);
    }
  }, [favoriteIds]);

  const toggleFavorite = (movieId) => {
    setFavoriteIds((prevIds) => {
      const newIds = new Set(prevIds);
      if (newIds.has(movieId)) {
        newIds.delete(movieId);
      } else {
        newIds.add(movieId);
      }
      return newIds;
    });
  };
  // --- END: Penambahan State & Logika Favorit ---

  const handleAuthError = useCallback(
    async (err) => {
      if (
        err.response &&
        (err.response.status === 401 || err.response.status === 403)
      ) {
        console.error("Authentication Error - Logging out:", err);
        await logout();
        return true;
      }
      return false;
    },
    [logout]
  );

  const fetchMovies = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
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
  }, [handleAuthError]);

  useEffect(() => {
    fetchMovies();
  }, [fetchMovies]);

  const addMovie = async (formData) => {
    try {
      const response = await axios.post("/movies", formData, {
        // Hapus header Content-Type, biarkan axios menentukannya untuk FormData
      });
      if (response.status === 201) {
        await fetchMovies();
        return { success: true };
      }
      throw new Error("Failed to add movie (unexpected response).");
    } catch (e) {
      console.error("Failed to add movie:", e);
      await handleAuthError(e);
      return { success: false, error: e.response?.data?.error || e.message };
    }
  };

  const updateMovie = async (movieId, formData) => {
    try {
      const response = await axios.post(`/movies/${movieId}`, formData, {
        // Hapus header Content-Type
      });
      if (response.status === 200) {
        await fetchMovies();
        return { success: true };
      }
      throw new Error("Failed to update movie (unexpected response).");
    } catch (e) {
      console.error("Failed to update movie:", e);
      await handleAuthError(e);
      return { success: false, error: e.response?.data?.error || e.message };
    }
  };

  const deleteMovie = async (movieId) => {
    try {
      const response = await axios.delete(`/movies/${movieId}`);
      if (response.status === 204) {
        // --- Hapus juga dari favorit jika ada ---
        setFavoriteIds((prevIds) => {
          const newIds = new Set(prevIds);
          newIds.delete(movieId);
          return newIds;
        });
        // --------------------------------------
        await fetchMovies();
        return { success: true };
      }
      throw new Error("Failed to delete movie (unexpected response).");
    } catch (e) {
      console.error("Failed to delete movie:", e);
      await handleAuthError(e);
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
        fetchMovies,
        favoriteIds, // <-- Export favoriteIds
        toggleFavorite, // <-- Export toggleFavorite
      }}
    >
      {children}
    </MoviesContext.Provider>
  );
}
