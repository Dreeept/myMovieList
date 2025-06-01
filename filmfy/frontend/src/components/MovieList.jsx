// filmfy/frontend/src/components/MovieList.jsx
import React, { useContext } from "react";
import MovieCard from "./MovieCard";
import { MoviesContext } from "../context/MovieContext";

// Tambahkan showFullActions ke props
export default function MovieList({
  movies,
  onEdit,
  onDelete,
  favoriteIds,
  toggleFavorite,
  showFullActions = true,
}) {
  // Jika favoriteIds dan toggleFavorite tidak di-pass, ambil dari context (fallback, meski idealnya di-pass)
  const context = useContext(MoviesContext);
  const favIds = favoriteIds !== undefined ? favoriteIds : context.favoriteIds;
  const togFav =
    toggleFavorite !== undefined ? toggleFavorite : context.toggleFavorite;

  return (
    <div className="px-6 py-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mt-6">
        {Array.isArray(movies) && movies.length > 0 ? (
          movies.map((movie) => (
            <MovieCard
              key={movie.id}
              movie={movie}
              onDelete={onDelete}
              onEdit={onEdit}
              onToggleFavorite={togFav}
              isFavorite={favIds.has(movie.id)}
              showFullActions={showFullActions} // <-- Teruskan prop ini
            />
          ))
        ) : (
          <p className="text-center col-span-full text-gray-600">
            Belum ada film yang ditampilkan.
          </p>
        )}
      </div>
    </div>
  );
}
