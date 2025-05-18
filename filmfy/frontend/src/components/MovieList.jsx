// MovieList.jsx
import React, { useState } from "react";
import MovieCard from "./MovieCard";
import MovieForm from "./MovieForm";

export default function MovieList({ movies, setMovies }) {
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [editingMovie, setEditingMovie] = useState(null);

  const handleAddClick = () => {
    setEditingMovie(null);
    setIsFormVisible(true);
  };

  const handleEdit = (movie) => {
    setEditingMovie(movie);
    setIsFormVisible(true);
  };

  const handleSave = (movie) => {
    if (movie.id) {
      setMovies(movies.map((m) => (m.id === movie.id ? movie : m)));
    } else {
      const newMovie = {
        ...movie,
        id: Date.now(),
        isFavorite: false,
      };
      setMovies([...movies, newMovie]);
    }
    setIsFormVisible(false);
    setEditingMovie(null);
  };

  const handleCancel = () => {
    setIsFormVisible(false);
    setEditingMovie(null);
  };

  const handleDelete = (id) => {
    if (window.confirm("Yakin ingin menghapus film ini?")) {
      setMovies(movies.filter((movie) => movie.id !== id));
    }
  };

  const handleToggleFavorite = (id) => {
    setMovies(
      movies.map((movie) =>
        movie.id === id ? { ...movie, isFavorite: !movie.isFavorite } : movie
      )
    );
  };

  return (
    <div className="px-6 py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Movie List</h1>
        <button
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md shadow"
          onClick={handleAddClick}
        >
          ➕ Add Movie
        </button>
      </div>

      {isFormVisible && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-50 flex justify-center items-center z-50">
          <div className="bg-white p-6 rounded-xl shadow-md max-w-md w-full">
            <MovieForm
              onSave={handleSave}
              onCancel={handleCancel}
              existingMovie={editingMovie}
            />
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mt-6">
        {movies.length > 0 ? (
          movies.map((movie) => (
            <MovieCard
              key={movie.id}
              movie={movie}
              onDelete={handleDelete}
              onEdit={handleEdit}
              onToggleFavorite={handleToggleFavorite}
            />
          ))
        ) : (
          <p className="text-center col-span-full text-gray-600">
            Belum ada film yang ditambahkan.
          </p>
        )}
      </div>
    </div>
  );
}
