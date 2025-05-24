import React from "react";

export default function MovieCard({
  movie,
  onEdit, // Fungsi untuk membuka modal edit
  onDelete, // Fungsi untuk menghapus
  // onToggleFavorite, // Kita nonaktifkan dulu
  showActions = true,
}) {
  // Gunakan poster_url jika ada, jika tidak, gunakan placeholder
  const imageUrl =
    movie.poster_url || "https://via.placeholder.com/300x400?text=No+Image";

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition w-full max-w-xs mx-auto">
      {" "}
      {/* Tambah mx-auto */}
      <img
        src={imageUrl} // <-- UBAH KE imageUrl (dari poster_url)
        alt={movie.title}
        className="w-full h-60 object-cover"
      />
      <div className="p-4">
        <h3 className="text-xl font-semibold">{movie.title}</h3>
        <p className="text-sm text-gray-600">
          {/* UBAH KE release_year */}
          {movie.release_year} · {movie.genre}
        </p>
        <p className="mt-1 text-yellow-600 font-bold">⭐ {movie.rating}/10</p>

        {showActions && (
          <div className="flex justify-between items-center mt-4">
            <button
              onClick={() => onEdit(movie)} // Pastikan memanggil onEdit
              className="text-blue-600 hover:underline text-sm"
            >
              ✏️ Edit
            </button>
            <button
              onClick={() => onDelete(movie.id)} // Pastikan memanggil onDelete
              className="text-red-600 hover:underline text-sm"
            >
              🗑️ Delete
            </button>
            {/* <button
              onClick={() => onToggleFavorite(movie.id)}
              className={`text-sm ${
                movie.isFavorite ? "text-yellow-500" : "text-gray-400"
              } hover:text-yellow-500`}
              title="Toggle Favorite"
            >
              ⭐
            </button> 
            */}
          </div>
        )}
      </div>
    </div>
  );
}
