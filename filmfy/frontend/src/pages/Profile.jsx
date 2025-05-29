// filmfy/frontend/src/pages/Profile.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext"; // <-- Import useAuth
import axios from "axios"; // <-- Import axios

export default function Profile() {
  const navigate = useNavigate();
  const { user, loading, isAuthenticated, logout } = useAuth(); // <-- Gunakan context
  const [error, setError] = useState("");
  const [deleting, setDeleting] = useState(false);

  // Jika belum loading dan tidak authenticated, redirect (seharusnya sudah ditangani ProtectedRoute, tapi ini pengaman tambahan)
  React.useEffect(() => {
    if (!loading && !isAuthenticated) {
      navigate("/login");
    }
  }, [loading, isAuthenticated, navigate]);

  const handleDelete = async () => {
    // <-- Ubah ke async
    if (
      !window.confirm(
        "Apakah kamu yakin ingin menghapus akun ini? Ini tidak dapat dibatalkan."
      )
    ) {
      return;
    }
    setDeleting(true);
    setError("");

    try {
      // Gunakan axios dan user.id dari context
      const response = await axios.delete(`/user/${user.id}`);

      // Cek status 204 No Content
      if (response.status === 204) {
        alert("Akun berhasil dihapus");
        await logout(); // Panggil fungsi logout dari context
        navigate("/login"); // Navigate dilakukan oleh logout atau di sini
      } else {
        throw new Error("Gagal menghapus akun (respons tidak terduga).");
      }
    } catch (err) {
      console.error("Delete error:", err);
      setError(
        err.response?.data?.error || "Terjadi kesalahan saat menghapus akun."
      );
      // Jika session habis, logout juga
      if (err.response?.status === 401 || err.response?.status === 403) {
        await logout();
        navigate("/login");
      }
    } finally {
      setDeleting(false);
    }
  };

  // Tampilkan loading jika context masih loading atau user belum ada
  if (loading || !user)
    return <div className="text-center mt-8">Loading profile...</div>;

  // Tampilkan error jika ada
  if (error)
    return (
      <div className="text-center mt-8 text-red-600 font-semibold">
        Error: {error}
      </div>
    );

  return (
    <div className="max-w-md mx-auto mt-10 p-8 bg-white rounded-lg shadow-lg">
      <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">
        Profil Saya
      </h1>
      <div className="flex flex-col items-center">
        {user.profile_url ? ( // <-- Gunakan user.profile_url
          <img
            src={user.profile_url} // <-- Langsung gunakan URL dari context
            alt="Foto Profil"
            className="w-32 h-32 rounded-full object-cover mb-6 border-4 border-blue-600"
          />
        ) : (
          <div className="w-32 h-32 rounded-full bg-gray-300 flex items-center justify-center mb-6 text-gray-600 text-lg">
            Tidak ada foto
          </div>
        )}
        <p className="text-lg mb-2">
          <strong>Username:</strong> {user.username}
        </p>
        <p className="text-lg mb-2">
          <strong>Email:</strong> {user.email}
        </p>
        <p className="text-lg mb-6 text-center px-4">
          <strong>Bio:</strong> {user.bio || "-"}
        </p>
      </div>

      <div className="flex justify-center space-x-4">
        <button
          onClick={() => navigate("/profile/edit")}
          className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition"
          disabled={deleting}
        >
          Edit Profil
        </button>
        <button
          onClick={handleDelete}
          className="px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded transition"
          disabled={deleting}
        >
          {deleting ? "Menghapus..." : "Hapus Akun"}
        </button>
      </div>

      <button
        onClick={() => navigate("/dashboard")}
        className="mt-8 w-full bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold py-2 rounded transition"
      >
        Kembali ke Dashboard
      </button>
    </div>
  );
}
