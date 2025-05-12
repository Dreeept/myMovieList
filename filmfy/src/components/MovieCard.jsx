import React from 'react';

export default function MovieCard({ movie, onEdit, onDelete, onToggleFavorite }) {
  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition w-full max-w-xs">
      <img
        src={movie.poster || 'https://via.placeholder.com/300x400?text=No+Image'}
        alt={movie.title}
        className="w-full h-60 object-cover"
      />
      <div className="p-4">
        <h3 className="text-xl font-semibold">{movie.title}</h3>
        <p className="text-sm text-gray-600">{movie.year} · {movie.genre}</p>
        <p className="mt-1 text-yellow-600 font-bold">⭐ {movie.rating}/10</p>

        <div className="flex justify-between items-center mt-4">
          <button
            onClick={() => onEdit(movie)}
            className="text-blue-600 hover:underline text-sm"
          >
            ✏️ Edit
          </button>
          <button
            onClick={() => onDelete(movie.id)}
            className="text-red-600 hover:underline text-sm"
          >
            🗑️ Delete
          </button>
          <button
            onClick={() => onToggleFavorite(movie.id)}
            className={`text-sm ${movie.isFavorite ? 'text-yellow-500' : 'text-gray-400'} hover:text-yellow-500`}
            title="Toggle Favorite"
          >
            ⭐
          </button>
        </div>
      </div>
    </div>
  );
}
