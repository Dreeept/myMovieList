// Favorites.jsx
import React from "react";
import Navbar from "../components/Navbar";

export default function Favorites({ movies }) {
  const favoriteMovies = movies.filter((movie) => movie.isFavorite);

  return (
    <>
      <Navbar />
      <div className="p-4 mt-8">
        <h2 className="text-2xl font-bold mb-4">Semua Film Favorit</h2>

        {favoriteMovies.length === 0 ? (
          <p className="text-gray-600">Belum ada film favorit.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {favoriteMovies.map((movie) => (
              <div
                key={movie.id}
                className="bg-gray-800 text-white p-4 rounded-lg shadow-md"
              >
                <h3 className="text-xl font-semibold">{movie.title}</h3>
                <p className="text-sm text-gray-400">
                  {movie.release_date || movie.year}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
