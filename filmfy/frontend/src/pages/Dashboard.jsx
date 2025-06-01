// filmfy/frontend/src/pages/Dashboard.jsx
import React, { useContext, useState } from "react";
import MovieList from "../components/MovieList";
import MovieForm from "../components/MovieForm";
import Modal from "../components/Modal";
import { MoviesContext } from "../context/MovieContext";
import { useAuth } from "../context/AuthContext";
import { useNavigate, Link } from "react-router-dom"; // <-- Tambahkan Link

export default function Dashboard() {
  const {
    movies,
    loading,
    error,
    addMovie,
    updateMovie, // Kita mungkin tidak pakai updateMovie langsung di Dashboard lagi
    deleteMovie, // Kita mungkin tidak pakai deleteMovie langsung di Dashboard lagi
    favoriteIds,
    toggleFavorite,
  } = useContext(MoviesContext);

  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [isModalOpen, setIsModalOpen] = useState(false);
  // editingMovie tidak digunakan lagi di sini, modal add saja
  // const [editingMovie, setEditingMovie] = useState(null);

  const handleOpenAddModal = () => {
    // Ubah nama fungsi
    // setEditingMovie(null); // Tidak perlu lagi
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    // setEditingMovie(null); // Tidak perlu lagi
  };

  const checkAuthAndHandleError = (result) => {
    if (!isAuthenticated) {
      navigate("/login");
      return false;
    }
    if (!result.success) {
      alert(`Error: ${result.error || "Gagal memproses data."}`);
      return false;
    }
    return true;
  };

  const handleSaveNewMovie = async (formData) => {
    // Hanya untuk add movie baru
    const result = await addMovie(formData);
    if (checkAuthAndHandleError(result)) {
      handleCloseModal();
    }
  };

  // Filter dan slice film untuk preview
  const favoriteMoviesPreview = movies
    .filter((movie) => favoriteIds.has(movie.id))
    .slice(0, 4);
  const allMoviesPreview = movies.slice(0, 4);

  if (loading) return <p className="text-center py-10">Loading dashboard...</p>;
  if (error) return <p className="text-center text-red-500 py-10">{error}</p>;

  return (
    <>
      <div className="p-4 mt-8 container mx-auto">
        <div className="flex justify-end items-center mb-8">
          {" "}
          {/* Pindahkan tombol tambah */}
          <button
            onClick={handleOpenAddModal}
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg shadow-md text-lg"
          >
            + Tambah Film Baru
          </button>
        </div>

        {/* Bagian Favorit */}
        <section className="mb-12">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-3xl font-bold text-gray-800">
              Film Favorit Anda
            </h2>
            {favoriteMoviesPreview.length > 0 && (
              <Link
                to="/favorites"
                className="text-blue-600 hover:text-blue-800 font-semibold"
              >
                Lihat Selengkapnya &rarr;
              </Link>
            )}
          </div>
          {favoriteMoviesPreview.length > 0 ? (
            <MovieList
              movies={favoriteMoviesPreview}
              // onEdit dan onDelete tidak kita berikan di preview dashboard
              // toggleFavorite bisa tetap ada
              favoriteIds={favoriteIds}
              toggleFavorite={toggleFavorite}
              showFullActions={false} // Hanya tampilkan tombol favorit
            />
          ) : (
            <p className="text-center text-gray-600 py-4">
              Anda belum memiliki film favorit.
            </p>
          )}
        </section>

        {/* Bagian Semua Film / Terbaru */}
        <section>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-3xl font-bold text-gray-800">Koleksi Film</h2>
            {allMoviesPreview.length > 0 && (
              <Link
                to="/movies"
                className="text-blue-600 hover:text-blue-800 font-semibold"
              >
                Lihat Selengkapnya &rarr;
              </Link>
            )}
          </div>
          {allMoviesPreview.length > 0 ? (
            <MovieList
              movies={allMoviesPreview}
              // onEdit dan onDelete tidak kita berikan di preview dashboard
              favoriteIds={favoriteIds}
              toggleFavorite={toggleFavorite}
              showFullActions={false} // Hanya tampilkan tombol favorit
            />
          ) : (
            !loading && (
              <p className="text-center text-gray-600 py-4">
                Belum ada film di database.
              </p>
            )
          )}
        </section>
      </div>

      {isModalOpen && (
        <Modal onClose={handleCloseModal}>
          <MovieForm
            onSave={handleSaveNewMovie} // Gunakan handleSaveNewMovie
            onCancel={handleCloseModal}
            existingMovie={null} // Selalu null karena ini modal 'Add'
          />
        </Modal>
      )}
    </>
  );
}
