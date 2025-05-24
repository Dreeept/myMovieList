import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function ProfileEdit() {
  const navigate = useNavigate();
  const userId = localStorage.getItem("userId");

  const [user, setUser] = useState({
    username: "",
    email: "",
    bio: "",
    profile_photo: "", // Ini akan menampung URL dari backend atau Data URL untuk pratinjau
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState(""); // State baru untuk pesan sukses
  const [photoFile, setPhotoFile] = useState(null); // File yang akan diunggah
  const [previewPhoto, setPreviewPhoto] = useState(null); // URL pratinjau gambar lokal

  // Fungsi untuk mengambil data user
  const fetchUserData = async () => {
    if (!userId) {
      setError("User belum login");
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(""); // Hapus error sebelumnya saat mulai fetch
    try {
      const res = await fetch(`http://localhost:6543/api/user/${userId}`);
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(
          `Gagal mengambil data user: ${res.status} ${errorText}`
        );
      }
      const data = await res.json();
      setUser(data);
      // Saat data awal dimuat, set previewPhoto ke foto profil yang ada
      setPreviewPhoto(
        data.profile_photo
          ? `http://localhost:6543/static/${data.profile_photo}`
          : null
      );
    } catch (err) {
      setError(err.message || "Terjadi kesalahan");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUserData();
  }, [userId]); // Dependensi hanya pada userId

  const handleChange = (e) => {
    setUser((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
    // Hapus pesan sukses/error saat ada perubahan input
    setSuccessMessage("");
    setError("");
  };

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      const file = e.target.files[0];
      setPhotoFile(file); // Simpan file yang dipilih untuk diunggah

      // Buat URL pratinjau lokal dari file
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewPhoto(reader.result); // Atur pratinjau agar langsung terlihat
      };
      reader.readAsDataURL(file);
    } else {
      setPhotoFile(null);
      // Jika file dibatalkan, kembalikan pratinjau ke foto profil asli
      setPreviewPhoto(
        user.profile_photo
          ? `http://localhost:6543/static/${user.profile_photo}`
          : null
      );
    }
    // Hapus pesan sukses/error saat ada perubahan input file
    setSuccessMessage("");
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccessMessage("");
    setSaving(true);

    try {
      const formData = new FormData();
      formData.append("username", user.username);
      formData.append("email", user.email);
      formData.append("bio", user.bio);
      if (photoFile) {
        formData.append("profile_photo", photoFile);
      }

      // Kirim permintaan PUT untuk update profil
      const response = await fetch(`http://localhost:6543/api/user/${userId}`, {
        method: "PUT",
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error || "Gagal update profil.");
      }

      // Setelah PUT berhasil, ambil ulang data user terbaru untuk memperbarui state
      await fetchUserData();

      // --- BARIS KODE BARU TAMBAHAN DI SINI ---
      // Memicu event kustom yang didengarkan oleh komponen Navbar
      window.dispatchEvent(new Event("profileUpdated"));
      // ---------------------------------------

      setSuccessMessage("Profil berhasil diperbarui!");
      setPhotoFile(null); // Reset photoFile setelah berhasil diunggah

      // Navigasi setelah beberapa saat agar pesan sukses terlihat
      setTimeout(() => {
        navigate("/profile");
      }, 1500);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading)
    return <div className="text-center mt-8 text-gray-700">Memuat data...</div>;
  if (error && !successMessage)
    // Tampilkan error utama jika tidak ada pesan sukses
    return (
      <div className="text-center mt-8 text-red-600 font-semibold p-4 bg-red-50 rounded">
        Error: {error}
      </div>
    );

  return (
    <div className="max-w-md mx-auto mt-10 p-8 bg-white rounded-lg shadow-lg border border-gray-200">
      <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">
        Edit Profil
      </h1>
      <form
        onSubmit={handleSubmit}
        className="space-y-6"
        encType="multipart/form-data"
      >
        <div>
          <label
            htmlFor="username"
            className="block font-semibold mb-1 text-gray-700"
          >
            Username
          </label>
          <input
            type="text"
            id="username"
            name="username"
            value={user.username}
            onChange={handleChange}
            required
            className="w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-150"
          />
        </div>

        <div>
          <label
            htmlFor="email"
            className="block font-semibold mb-1 text-gray-700"
          >
            Email
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={user.email}
            onChange={handleChange}
            required
            className="w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-150"
          />
        </div>

        <div>
          <label
            htmlFor="bio"
            className="block font-semibold mb-1 text-gray-700"
          >
            Bio
          </label>
          <textarea
            id="bio"
            name="bio"
            value={user.bio}
            onChange={handleChange}
            rows={4}
            className="w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-150 resize-y"
          />
        </div>

        <div>
          <label className="block font-semibold mb-2 text-gray-700">
            Foto Profil
          </label>
          {previewPhoto ? (
            <img
              src={
                previewPhoto.startsWith("http")
                  ? `${previewPhoto}?t=${Date.now()}`
                  : previewPhoto
              } // Tambahkan cache busting
              alt="Foto Profil"
              className="w-28 h-28 rounded-full mb-3 object-cover border-2 border-blue-600 shadow-md mx-auto"
            />
          ) : (
            <div className="w-28 h-28 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 mb-3 text-sm mx-auto border border-gray-300">
              Tidak ada foto
            </div>
          )}
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer"
          />
        </div>

        {/* Tampilan pesan sukses atau error di bawah tombol */}
        {successMessage && (
          <p className="text-green-600 text-center font-medium bg-green-50 p-2 rounded">
            {successMessage}
          </p>
        )}
        {error && (
          <p className="text-red-600 text-center font-medium bg-red-50 p-2 rounded">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={saving}
          className={`w-full py-2 rounded font-semibold transition duration-200 ${
            saving
              ? "bg-blue-400 text-white cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700 text-white shadow-md"
          }`}
        >
          {saving ? "Menyimpan..." : "Simpan Perubahan"}
        </button>

        <button
          type="button"
          onClick={() => navigate("/profile")}
          className={`w-full mt-3 py-2 rounded font-semibold transition duration-200 ${
            saving
              ? "bg-gray-200 text-gray-600 cursor-not-allowed"
              : "bg-gray-300 hover:bg-gray-400 text-gray-800"
          }`}
          disabled={saving}
        >
          Batal
        </button>
      </form>
    </div>
  );
}
