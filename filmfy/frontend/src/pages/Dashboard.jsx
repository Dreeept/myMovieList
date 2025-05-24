import React, { useContext } from "react";
import Navbar from "../components/Navbar";
import MovieList from "../components/MovieList";
import MovieCard from "../components/MovieCard"; // Import MovieCard
import { MoviesContext } from "../context/MovieContext";

export default function Dashboard() {
  const { movies, setMovies } = useContext(MoviesContext);

  const favoriteMovies = movies.filter((movie) => movie.isFavorite);

  // Batasi hanya 3 film yang ditampilkan
  const displayedFavorites = favoriteMovies.slice(0, 3);

  return (
    <>
      <Navbar />

      <div className="p-4 mt-8">
        <h2 className="text-2xl font-bold mb-4">Film Favorit</h2>

        {favoriteMovies.length === 0 ? (
          <p className="text-gray-600">Belum ada film favorit.</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {displayedFavorites.map((movie) => (
              <MovieCard key={movie.id} movie={movie} showActions={false} />
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

      <MovieList movies={movies} setMovies={setMovies} />
    </>
  );
}
