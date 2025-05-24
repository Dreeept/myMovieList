import React, { useContext, useState } from "react";
import Navbar from "../components/Navbar";
import MovieList from "../components/MovieList";
import MovieForm from "../components/MovieForm"; // Import MovieForm
import Modal from "../components/Modal"; // Import Modal
import { MoviesContext } from "../context/MovieContext";

export default function Dashboard() {
  // Ambil data dan fungsi dari context API
  const { movies, loading, error, addMovie, updateMovie, deleteMovie } =
    useContext(MoviesContext);

  // State untuk mengontrol modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingMovie, setEditingMovie] = useState(null);

  // Fungsi untuk membuka modal (bisa untuk add baru atau edit)
  const handleOpenModal = (movieToEdit = null) => {
    setEditingMovie(movieToEdit);
    setIsModalOpen(true);
  };

  // Fungsi untuk menutup modal
  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingMovie(null);
  };

  // Fungsi yang akan dipanggil saat form disubmit (dari MovieForm)
  const handleSaveMovie = async (formData, movieId) => {
    console.log("Saving Movie:", movieId ? "Update" : "Add", formData);
    let result;
    if (movieId) {
      result = await updateMovie(movieId, formData);
    } else {
      result = await addMovie(formData);
    }

    if (result.success) {
      handleCloseModal(); // Tutup modal jika sukses
    } else {
      alert(`Error: ${result.error || "Gagal menyimpan data."}`); // Tampilkan error
    }
  };

  // Fungsi untuk menangani delete (diteruskan ke MovieList)
  const handleDeleteMovie = async (movieId) => {
    if (window.confirm("Apakah Anda yakin ingin menghapus film ini?")) {
      const result = await deleteMovie(movieId);
      if (!result.success) {
        alert(`Error: ${result.error || "Gagal menghapus data."}`);
      }
    }
  };

  return (
    <>
      <Navbar />

      <div className="p-4 mt-8 container mx-auto">
        {" "}
        {/* Bungkus dengan container */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Semua Film</h2>
          <button
            onClick={() => handleOpenModal()} // Tombol untuk membuka modal 'Add'
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded"
          >
            + Tambah Film Baru
          </button>
        </div>
        {/* Hapus bagian Favorit untuk sementara */}
        {/* Tampilkan status loading/error/data */}
        {loading && <p className="text-center">Loading movies...</p>}
        {error && <p className="text-center text-red-500">{error}</p>}
        {!loading && !error && movies.length > 0 && (
          <MovieList
            movies={movies}
            onEdit={handleOpenModal} // Teruskan handleOpenModal sebagai onEdit
            onDelete={handleDeleteMovie} // Teruskan handleDeleteMovie sebagai onDelete
          />
        )}
        {!loading && !error && movies.length === 0 && (
          <p className="text-center text-gray-600">
            Belum ada film di database.
          </p>
        )}
      </div>

      {/* Tampilkan Modal jika isModalOpen true */}
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
