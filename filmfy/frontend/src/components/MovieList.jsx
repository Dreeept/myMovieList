import React from "react";
import MovieCard from "./MovieCard";

// Komponen ini SEKARANG HANYA menampilkan daftar.
// Ia menerima 'movies', 'onEdit', dan 'onDelete' dari Dashboard.
export default function MovieList({ movies, onEdit, onDelete }) {
  return (
    <div className="px-6 py-6">
      {/* Judul dan Tombol Add dipindahkan ke Dashboard */}

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mt-6">
        {/* Periksa jika movies adalah array sebelum map */}
        {Array.isArray(movies) && movies.length > 0 ? (
          movies.map((movie) => (
            <MovieCard
              key={movie.id}
              movie={movie}
              onDelete={onDelete} // Teruskan onDelete
              onEdit={onEdit} // Teruskan onEdit
              // onToggleFavorite dihapus untuk saat ini
            />
          ))
        ) : (
          <p className="text-center col-span-full text-gray-600">
            Belum ada film yang ditambahkan atau ditemukan.
          </p>
        )}
      </div>
    </div>
  );
}
