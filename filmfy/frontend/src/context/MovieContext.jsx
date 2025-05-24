import React, { createContext, useState, useEffect } from "react";
import { loadMovies, saveMovies } from "../utils/LocalStorage";

export const MoviesContext = createContext();

export function MoviesProvider({ children }) {
  const [movies, setMovies] = useState(() => loadMovies());

  useEffect(() => {
    saveMovies(movies);
  }, [movies]);

  return (
    <MoviesContext.Provider value={{ movies, setMovies }}>
      {children}
    </MoviesContext.Provider>
  );
}
