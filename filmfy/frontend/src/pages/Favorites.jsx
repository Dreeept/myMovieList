import React, { useContext } from "react";
import Navbar from "../components/Navbar";
import { MoviesContext } from "../context/MovieContext";

export default function Favorites() {
  const { movies } = useContext(MoviesContext);

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
                className="bg-white text-black p-4 rounded-lg shadow-md"
              >
                {/* Poster */}
                <img
                  src={
                    movie.poster ||
                    "https://via.placeholder.com/300x400?text=No+Image"
                  }
                  alt={movie.title}
                  className="w-full h-60 object-cover rounded-md mb-4"
                />

                {/* Judul */}
                <h3 className="text-xl font-semibold">{movie.title}</h3>

                {/* Tahun & Genre */}
                <p className="text-sm text-gray-400">
                  {movie.release_date || movie.year} &nbsp;|&nbsp; {movie.genre}
                </p>

                {/* Rating */}
                <p className="mt-1 text-yellow-600 font-bold">
                  ⭐ {movie.rating}/10
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
