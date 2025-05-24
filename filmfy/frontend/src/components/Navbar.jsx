import React from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();

  // Gunakan gambar avatar statis untuk sementara
  const displayProfileImage = "https://i.pravatar.cc/40?img=12";

  const handleLogout = () => {
    // Hapus userId dari localStorage
    localStorage.removeItem("userId");
    // Redirect ke halaman login
    navigate("/login");
  };

  return (
    <nav className="bg-[#000B58] text-white px-6 py-4 shadow-md">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        {/* Logo */}
        <div className="text-2xl font-bold tracking-wide">
          <Link to="/dashboard">FILMFY</Link>
        </div>

        {/* Menu tengah (Favorites belum berfungsi penuh) */}
        <div className="flex space-x-8">
          <Link
            to="/favorites"
            className="hover:underline text-lg font-semibold"
          >
            Favorites
          </Link>
          {/* Link Watch Later bisa ditambahkan jika ada halamannya */}
        </div>

        {/* User Avatar & Logout Sederhana */}
        <div className="relative">
          {/* Tampilkan avatar statis */}
          <img
            src={displayProfileImage}
            alt="User Avatar"
            // Anda bisa menambahkan dropdown sederhana atau langsung link profil
            className="w-10 h-10 rounded-full border-2 border-white cursor-pointer object-cover"
          />
          {/* Dropdown bisa ditambahkan kembali nanti saat profil sudah ada */}
          {/* Contoh tombol logout sederhana (bisa diletakkan di dropdown) */}
          {/* <button onClick={handleLogout} className="ml-4">Logout</button> */}
        </div>
      </div>
    </nav>
  );
}
