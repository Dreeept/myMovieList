// filmfy/frontend/src/components/MovieCard.jsx
import React from "react";

export default function MovieCard({
  movie,
  onEdit,
  onDelete,
  onToggleFavorite,
  isFavorite,
  showFullActions = true, // <-- Prop baru, defaultnya true
}) {
  const imageUrl =
    movie.poster_url || "https://placehold.co/300x400?text=No+Image";

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition w-full max-w-xs mx-auto text-black">
      <img
        src={imageUrl}
        alt={movie.title}
        className="w-full h-60 object-cover"
      />
      <div className="p-4">
        <h3 className="text-xl font-semibold text-gray-900">{movie.title}</h3>
        <p className="text-sm text-gray-600">
          {movie.release_year} · {movie.genre}
        </p>
        <p className="mt-1 text-yellow-600 font-bold">⭐ {movie.rating}/10</p>

        {/* Selalu tampilkan tombol favorit jika onToggleFavorite ada */}
        {onToggleFavorite && (
          <div
            className={`flex ${
              showFullActions ? "justify-between" : "justify-end"
            } items-center mt-4`}
          >
            {showFullActions &&
              (onEdit || onDelete) && ( // Hanya tampilkan grup edit/delete jika showFullActions true
                <div>
                  {onEdit && (
                    <button
                      onClick={() => onEdit(movie)}
                      className="text-blue-600 hover:underline text-sm mr-3"
                    >
                      ✏️ Edit
                    </button>
                  )}
                  {onDelete && (
                    <button
                      onClick={() => onDelete(movie.id)}
                      className="text-red-600 hover:underline text-sm"
                    >
                      🗑️ Delete
                    </button>
                  )}
                </div>
              )}
            <button
              onClick={() => onToggleFavorite(movie.id)}
              className={`text-2xl transition-transform duration-150 ease-in-out ${
                isFavorite ? "transform scale-125" : ""
              }`}
              title={isFavorite ? "Hapus dari Favorit" : "Tambah ke Favorit"}
            >
              {isFavorite ? "❤️" : "🤍"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
