// filmfy/frontend/src/pages/Dashboard.jsx
import React, { useContext, useState } from "react";
// Hapus import Navbar karena sudah ada di ProtectedRoute
import MovieList from "../components/MovieList";
import MovieForm from "../components/MovieForm";
import Modal from "../components/Modal";
import { MoviesContext } from "../context/MovieContext";
import { useAuth } from "../context/AuthContext"; // <-- Import useAuth
import { useNavigate } from "react-router-dom"; // <-- Import useNavigate

export default function Dashboard() {
  const { movies, loading, error, addMovie, updateMovie, deleteMovie } =
    useContext(MoviesContext);
  const { isAuthenticated } = useAuth(); // <-- Dapatkan status auth
  const navigate = useNavigate(); // <-- Dapatkan navigate

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

  // Fungsi helper untuk cek auth setelah aksi
  const checkAuthAndHandleError = (result) => {
    if (!isAuthenticated) {
      navigate("/login"); // Jika entah bagaimana jadi tidak auth, redirect
      return false;
    }
    if (!result.success) {
      alert(`Error: ${result.error || "Gagal menyimpan data."}`);
      // Jika error auth terdeteksi oleh context, ia akan logout,
      // dan ProtectedRoute akan redirect. Di sini kita hanya alert error.
      return false;
    }
    return true;
  };

  const handleSaveMovie = async (formData, movieId) => {
    console.log("Saving Movie:", movieId ? "Update" : "Add", formData);
    let result;
    if (movieId) {
      result = await updateMovie(movieId, formData);
    } else {
      result = await addMovie(formData);
    }

    if (checkAuthAndHandleError(result)) {
      handleCloseModal(); // Tutup modal jika sukses
    }
  };

  const handleDeleteMovie = async (movieId) => {
    if (window.confirm("Apakah Anda yakin ingin menghapus film ini?")) {
      const result = await deleteMovie(movieId);
      checkAuthAndHandleError(result); // Cukup cek dan tampilkan error
    }
  };

  return (
    <>
      {/* Navbar sudah ditampilkan oleh ProtectedRoute */}
      <div className="p-4 mt-8 container mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Semua Film</h2>
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
          <MovieList // <-- Periksa apakah MovieList.jsx Anda sudah benar
            movies={movies}
            onEdit={handleOpenModal}
            onDelete={handleDeleteMovie}
          />
        )}
        {!loading && !error && movies.length === 0 && (
          <p className="text-center text-gray-600">
            Belum ada film di database.
          </p>
        )}
      </div>

      {isModalOpen && (
        <Modal onClose={handleCloseModal}>
          <MovieForm
            onSave={handleSaveMovie}
            onCancel={handleCloseModal}
            existingMovie={editingMovie}
          />
        </Modal>
      )}
    </>
  );
}
