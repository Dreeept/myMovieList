// filmfy/frontend/src/pages/AllMoviesPage.jsx
import React, { useContext, useState } from "react";
import MovieList from "../components/MovieList";
import MovieForm from "../components/MovieForm";
import Modal from "../components/Modal";
import { MoviesContext } from "../context/MovieContext";
import { useAuth } from "../context/AuthContext"; // Untuk menangani jika session habis
import { useNavigate } from "react-router-dom";

export default function AllMoviesPage() {
  const {
    movies,
    loading,
    error,
    addMovie,
    updateMovie,
    deleteMovie,
    favoriteIds,
    toggleFavorite,
    fetchMovies, // Tambahkan jika ingin ada tombol refresh manual
  } = useContext(MoviesContext);

  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingMovie, setEditingMovie] = useState(null);

  const handleOpenModal = (movieToEdit = null) => {
    setEditingMovie(movieToEdit);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingMovie(null);
  };

  const checkAuthAndHandleError = (result) => {
    if (!isAuthenticated) {
      navigate("/login");
      return false;
    }
    if (!result.success) {
      alert(`Error: ${result.error || "Gagal memproses data film."}`);
      return false;
    }
    return true;
  };

  const handleSaveMovie = async (formData, movieId) => {
    let result;
    if (movieId) {
      result = await updateMovie(movieId, formData);
    } else {
      result = await addMovie(formData);
    }
    if (checkAuthAndHandleError(result)) {
      handleCloseModal();
    }
  };

  const handleDeleteMovie = async (movieId) => {
    if (window.confirm("Apakah Anda yakin ingin menghapus film ini?")) {
      const result = await deleteMovie(movieId);
      checkAuthAndHandleError(result);
    }
  };

  return (
    <div className="p-4 mt-8 container mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Semua Film</h1>
        <button
          onClick={() => handleOpenModal()}
          className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded"
        >
          + Tambah Film Baru
        </button>
      </div>

      {loading && <p className="text-center">Loading movies...</p>}
      {error && <p className="text-center text-red-500">{error}</p>}

      {!loading && !error && movies.length > 0 && (
        <MovieList
          movies={movies}
          onEdit={handleOpenModal}
          onDelete={handleDeleteMovie}
          favoriteIds={favoriteIds}
          toggleFavorite={toggleFavorite}
        />
      )}
      {!loading && !error && movies.length === 0 && (
        <p className="text-center text-gray-600">Belum ada film di database.</p>
      )}

      {isModalOpen && (
        <Modal onClose={handleCloseModal}>
          <MovieForm
            onSave={handleSaveMovie}
            onCancel={handleCloseModal}
            existingMovie={editingMovie}
          />
        </Modal>
      )}
    </div>
  );
}
