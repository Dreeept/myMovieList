import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); // Reset error

    try {
      const response = await fetch("http://localhost:6543/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        // Kalau status bukan 2xx, anggap login gagal
        const errData = await response.json();
        setError(errData.error || "Login gagal. Coba lagi.");
        return;
      }

      // Jika login berhasil, misal backend kirim token atau user data
      const data = await response.json();

      // Simpan userId ke localStorage:
      if (data.user && data.user.id) {
        localStorage.setItem("userId", data.user.id);
      }

      // Simpan token ke localStorage/sessionStorage kalau ada
      if (data.token) {
        localStorage.setItem("token", data.token);
      }

      // Redirect ke halaman dashboard atau homepage
      navigate("/dashboard");
    } catch (err) {
      setError("Terjadi kesalahan jaringan. Coba lagi nanti.");
      console.error("Login error:", err);
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
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition duration-200"
          >
            Sign In
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
