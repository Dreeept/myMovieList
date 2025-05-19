import React, { useState, useEffect } from "react";
import Navbar from "../components/Navbar";
import { saveMovies, loadMovies } from "../utils/LocalStorage";
import MovieList from "../components/MovieList";

export default function Dashboard() {
  // Inisialisasi movies dari localStorage
  const [movies, setMovies] = useState(() => loadMovies());

  // Simpan movies ke localStorage setiap movies berubah
  useEffect(() => {
    saveMovies(movies);
  }, [movies]);

  // Filter film favorit
  const favoriteMovies = movies.filter((movie) => movie.isFavorite);

  return (
    <>
      <Navbar />

      <div className="p-4 mt-8">
        <h2 className="text-2xl font-bold mb-4">Film Favorit</h2>

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

        <a
          href="/favorites"
          className="text-blue-500 mt-4 inline-block hover:underline"
        >
          Lihat Semua Favorit
        </a>
      </div>

      {/* Kirim props movies dan setMovies ke MovieList */}
      <MovieList movies={movies} setMovies={setMovies} />
    </>
  );
}
