// filmfy/frontend/src/pages/ProfileEdit.jsx
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext"; // <-- Import useAuth
import axios from "axios"; // <-- Import axios

export default function ProfileEdit() {
  const navigate = useNavigate();
  const {
    user: authUser,
    loading: authLoading,
    setUser: setAuthUser,
    logout,
  } = useAuth(); // <-- Gunakan context

  const [formData, setFormData] = useState({
    username: "",
    email: "",
    bio: "",
  });
  const [loading, setLoading] = useState(true); // Loading lokal untuk form
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [photoFile, setPhotoFile] = useState(null);
  const [previewPhoto, setPreviewPhoto] = useState(null);

  // Set form data saat data user dari context tersedia
  useEffect(() => {
    if (!authLoading && authUser) {
      setFormData({
        username: authUser.username || "",
        email: authUser.email || "",
        bio: authUser.bio || "",
      });
      setPreviewPhoto(authUser.profile_url || null);
      setLoading(false);
    } else if (!authLoading && !authUser) {
      // Jika tidak loading tapi tidak ada user, redirect
      navigate("/login");
    }
  }, [authUser, authLoading, navigate]);

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
    setSuccessMessage("");
    setError("");
  };

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      const file = e.target.files[0];
      setPhotoFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewPhoto(reader.result);
      };
      reader.readAsDataURL(file);
    } else {
      setPhotoFile(null);
      setPreviewPhoto(authUser.profile_url || null);
    }
    setSuccessMessage("");
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccessMessage("");
    setSaving(true);

    try {
      const dataToSubmit = new FormData();
      dataToSubmit.append("username", formData.username);
      dataToSubmit.append("email", formData.email);
      dataToSubmit.append("bio", formData.bio);

      if (photoFile) {
        dataToSubmit.append("foto_profil", photoFile);
      }

      // Gunakan axios dan authUser.id
      const response = await axios.post(`/user/${authUser.id}`, dataToSubmit);

      if (response.status === 200 && response.data.user) {
        setAuthUser(response.data.user); // <-- Update context global!
        setSuccessMessage("Profil berhasil diperbarui!");
        setPhotoFile(null);
        setTimeout(() => {
          navigate("/profile");
        }, 1500);
      } else {
        throw new Error("Gagal update profil.");
      }
    } catch (err) {
      console.error("Update profile error:", err);
      setError(err.response?.data?.error || "Terjadi kesalahan.");
      // Jika session habis, logout
      if (err.response?.status === 401 || err.response?.status === 403) {
        await logout();
        navigate("/login");
      }
    } finally {
      setSaving(false);
    }
  };

  if (loading)
    return <div className="text-center mt-8 text-gray-700">Memuat data...</div>;

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
            value={formData.username} // <-- Gunakan formData
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
            value={formData.email} // <-- Gunakan formData
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
            value={formData.bio} // <-- Gunakan formData
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
              src={previewPhoto} // <-- Gunakan previewPhoto
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
