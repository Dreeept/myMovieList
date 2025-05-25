import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

export default function Signup() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [bio, setBio] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [profilePhoto, setProfilePhoto] = useState(null); // Ini akan jadi File object
  const [profilePhotoPreview, setProfilePhotoPreview] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false); // Tambahkan state loading
  const navigate = useNavigate();

  const handlePhotoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setProfilePhoto(file); // Simpan File object
      setProfilePhotoPreview(URL.createObjectURL(file)); // Buat URL sementara untuk preview
    } else {
      setProfilePhoto(null);
      setProfilePhotoPreview(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); // Reset error setiap kali submit
    setLoading(true); // Mulai loading

    if (password !== confirmPassword) {
      setError("Password dan konfirmasi password tidak sama!");
      setLoading(false);
      return;
    }

    if (!username.trim() || !email.trim() || !password) {
      // Pastikan email & password juga tidak hanya spasi
      setError("Username, email, dan password tidak boleh kosong!");
      setLoading(false);
      return;
    }

    const formDataToSend = new FormData(); // Ubah nama variabel agar lebih jelas
    formDataToSend.append("username", username);
    formDataToSend.append("email", email);
    formDataToSend.append("bio", bio);
    formDataToSend.append("password", password);
    formDataToSend.append("confirm_password", confirmPassword); // Kirim juga confirm_password

    if (profilePhoto) {
      // Nama field 'foto_profil' harus sama dengan yang diharapkan backend
      formDataToSend.append("foto_profil", profilePhoto);
    }

    try {
      const response = await fetch("http://localhost:6543/api/signup", {
        method: "POST",
        body: formDataToSend, // Kirim formDataToSend
      });

      const responseData = await response.json(); // Selalu coba parse JSON respons

      if (response.ok) {
        // response.ok berarti status 200-299
        alert("Akun berhasil dibuat! Silakan login.");
        navigate("/login");
      } else {
        // Gunakan pesan error dari backend jika ada, jika tidak, pesan generik
        setError(
          responseData.error || "Terjadi kesalahan saat mendaftar, coba lagi."
        );
      }
    } catch (error) {
      console.error("Signup fetch error:", error);
      setError("Tidak dapat terhubung ke server. Coba lagi nanti.");
    } finally {
      setLoading(false); // Selesai loading
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-2xl shadow-md w-full max-w-md">
        <h2 className="text-3xl font-bold mb-6 text-center text-gray-800">
          Signup
        </h2>
        {error && (
          <div className="mb-4 text-red-600 text-sm text-center">{error}</div>
        )}
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Username */}
          <div>
            <label className="block text-gray-700">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2 mt-1 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Masukkan username"
              required
            />
          </div>
          {/* Email */}
          <div>
            <label className="block text-gray-700">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 mt-1 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="you@example.com"
              required
            />
          </div>
          {/* Bio Singkat */}
          <div>
            <label className="block text-gray-700">Bio Singkat</label>
            <textarea
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              className="w-full px-4 py-2 mt-1 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Tulis sedikit tentang dirimu..."
              rows={3}
            />
          </div>
          {/* Foto Profil */}
          <div>
            <label className="block text-gray-700 mb-1">Foto Profil</label>
            {profilePhotoPreview && (
              <img
                src={profilePhotoPreview}
                alt="Preview Foto Profil"
                className="w-24 h-24 rounded-full mb-2 object-cover"
              />
            )}
            <input
              type="file"
              accept="image/*" // Batasi tipe file
              onChange={handlePhotoChange}
              className="w-full"
            />
          </div>
          {/* Password */}
          <div>
            <label className="block text-gray-700">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 mt-1 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="••••••••"
              required
            />
          </div>
          {/* Confirm Password */}
          <div>
            <label className="block text-gray-700">Confirm Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full px-4 py-2 mt-1 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="••••••••"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading} // Disable tombol saat loading
            className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition duration-200 disabled:opacity-50"
          >
            {loading ? "Mendaftar..." : "Sign Up"}
          </button>

          <div className="text-center mt-4 text-sm text-gray-600">
            Sudah punya akun?{" "}
            <Link to="/login" className="text-blue-600 hover:underline">
              Login di sini
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
