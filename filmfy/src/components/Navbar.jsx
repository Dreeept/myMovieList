import React from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();
  const profileImage = "https://i.pravatar.cc/40?img=12"; // Gambar avatar dummy

  const handleLogout = () => {
    // Hapus data autentikasi di sini kalau ada (misalnya localStorage.removeItem)
    // localStorage.removeItem("token");

    // Redirect ke halaman login
    navigate("/login");
  };

  const handleAvatarClick = () => {
    navigate("/users"); // arahkan ke halaman /users
  };

  return (
    <nav className="bg-[#000B58] text-white px-6 py-4 shadow-md">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        {/* Logo */}
        <div className="text-2xl font-bold tracking-wide">
          <Link to="/dashboard">FILMFY</Link>
        </div>

        {/* User Avatar & Logout */}
        <div className="flex items-center space-x-4">
          <img
            src={profileImage}
            alt="User Avatar"
            onClick={handleAvatarClick}
            className="w-10 h-10 rounded-full border-2 border-white"
          />
          <button
            onClick={handleLogout}
            className="bg-red-500 hover:bg-red-600 px-3 py-1 rounded-md text-sm md:text-base transition"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
