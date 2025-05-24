import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Profile() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deleting, setDeleting] = useState(false);

  const userId = localStorage.getItem("userId");

  useEffect(() => {
    if (!userId) {
      setError("User belum login");
      setLoading(false);
      return;
    }

    fetch(`http://localhost:6543/api/user/${userId}`)
      .then((res) => {
        if (!res.ok) throw new Error("Gagal mengambil data user");
        return res.json();
      })
      .then((data) => {
        setUser(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Terjadi kesalahan");
        setLoading(false);
      });
  }, [userId]);

  const handleDelete = () => {
    if (!window.confirm("Apakah kamu yakin ingin menghapus akun ini?")) {
      return;
    }

    setDeleting(true);

    fetch(`http://localhost:6543/api/user/${userId}`, {
      method: "DELETE",
    })
      .then((res) => {
        if (!res.ok) throw new Error("Gagal menghapus akun");
        return res.json();
      })
      .then(() => {
        alert("Akun berhasil dihapus");
        localStorage.removeItem("userId");
        navigate("/login");
      })
      .catch((err) => {
        alert(err.message || "Terjadi kesalahan saat menghapus akun");
        setDeleting(false);
      });
  };

  if (loading)
    return <div className="text-center mt-8">Loading profile...</div>;
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
        {user.profile_photo ? (
          <img
            src={`http://localhost:6543/static/${user.profile_photo}`}
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
