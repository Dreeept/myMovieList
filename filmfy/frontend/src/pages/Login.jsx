import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false); // Tambahkan state loading
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    if (!email.trim() || !password) {
      // Validasi input dasar
      setError("Email dan password tidak boleh kosong!");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch("http://localhost:6543/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      // Selalu coba parse JSON dari respons, bahkan untuk error
      const responseData = await response.json();

      if (!response.ok) {
        // Jika status bukan 2xx, anggap login gagal
        setError(
          responseData.error || "Login gagal. Periksa email dan password Anda."
        );
        setLoading(false);
        return;
      }

      // Jika login berhasil
      // Backend kita mengirimkan data.user
      if (responseData.user && responseData.user.id) {
        localStorage.setItem("userId", responseData.user.id);
        // Anda mungkin ingin menyimpan seluruh objek user atau token jika ada
        // localStorage.setItem("userData", JSON.stringify(responseData.user));
        navigate("/dashboard"); // Redirect ke dashboard
      } else {
        // Kasus jika respons OK tapi tidak ada user.id (seharusnya tidak terjadi dengan backend kita)
        setError("Gagal mendapatkan data pengguna setelah login.");
      }
    } catch (err) {
      setError("Tidak dapat terhubung ke server. Coba lagi nanti.");
      console.error("Login error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-2xl shadow-md w-full max-w-md">
        <h2 className="text-3xl font-bold mb-6 text-center text-gray-800">
          Login
        </h2>
        {error && (
          <div className="mb-4 text-red-600 text-sm text-center">{error}</div>
        )}
        <form onSubmit={handleSubmit} className="space-y-5">
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
          <button
            type="submit"
            disabled={loading} // Disable tombol saat loading
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition duration-200 disabled:opacity-50"
          >
            {loading ? "Memproses..." : "Sign In"}
          </button>
          <div className="text-center mt-4 text-sm text-gray-600">
            Belum Punya Akun?{" "}
            <Link to="/signup" className="text-blue-600 hover:underline">
              Daftar Sekarang
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
