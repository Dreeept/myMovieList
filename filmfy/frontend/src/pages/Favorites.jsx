// filmfy/frontend/src/pages/Favorites.jsx
import React, { useContext } from "react";
import { MoviesContext } from "../context/MovieContext";
import MovieList from "../components/MovieList"; // <-- Gunakan MovieList

export default function Favorites() {
  const { movies, favoriteIds, loading, error, toggleFavorite } =
    useContext(MoviesContext);

  const favoriteMovies = movies.filter((movie) => favoriteIds.has(movie.id));

  // Di halaman favorit, tombol delete akan jadi Unfavorite
  const handleUnfavorite = (movieId) => {
    toggleFavorite(movieId);
  };

  return (
    <>
      <div className="p-4 mt-8 container mx-auto">
        <h2 className="text-3xl font-bold text-gray-800">Film Favorit Saya</h2>

        {loading && <p className="text-center">Loading...</p>}
        {error && <p className="text-center text-red-500">{error}</p>}

        {!loading && !error && favoriteMovies.length === 0 ? (
          <p className="text-gray-600 text-center">
            Belum ada film favorit. Klik ❤️ di Dashboard!
          </p>
        ) : (
          !loading &&
          !error && (
            <MovieList
              movies={favoriteMovies}
              onEdit={() => {
                /* Nonaktifkan Edit di sini */
              }}
              onDelete={handleUnfavorite} // <-- onDelete akan jadi Unfavorite
              favoriteIds={favoriteIds} // <-- Teruskan favoriteIds
              toggleFavorite={toggleFavorite} // <-- Teruskan toggleFavorite
            />
          )
        )}
      </div>
    </>
  );
}
