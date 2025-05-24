import React, { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();
  const menuRef = useRef();

  const [showMenu, setShowMenu] = useState(false);
  const [userProfile, setUserProfile] = useState(null); // State untuk menyimpan data profil pengguna
  const [loading, setLoading] = useState(true); // State loading untuk fetching data
  const [error, setError] = useState(null); // State error jika gagal fetching

  // Ambil userId dari localStorage
  const userId = localStorage.getItem("userId");

  // Fungsi untuk mengambil data profil pengguna
  const fetchUserProfile = async () => {
    if (!userId) {
      // Jika userId tidak ada (user belum login), atur loading selesai dan error
      setLoading(false);
      setError("User tidak login.");
      return;
    }

    setLoading(true); // Set loading true saat mulai fetching
    setError(null); // Hapus error sebelumnya
    try {
      const response = await fetch(`http://localhost:6543/api/user/${userId}`);
      if (!response.ok) {
        // Jika respons tidak OK (misal 404, 500), lemparkan error
        throw new Error("Gagal mengambil data profil pengguna.");
      }
      const data = await response.json(); // Parse respons JSON
      setUserProfile(data); // Set data profil ke state
    } catch (err) {
      setError(err.message); // Atur error
      console.error("Error saat mengambil data profil untuk Navbar:", err);
    } finally {
      setLoading(false); // Selesai loading
    }
  };

  // useEffect untuk mengambil data profil saat komponen dimuat
  useEffect(() => {
    fetchUserProfile();

    // Menambahkan event listener untuk memperbarui profil secara dinamis
    // Ketika ada perubahan di halaman ProfileEdit, event ini akan dipicu
    const handleProfileUpdated = () => {
      fetchUserProfile(); // Panggil ulang fetchUserProfile untuk mendapatkan data terbaru
    };
    window.addEventListener("profileUpdated", handleProfileUpdated);

    // Cleanup function: hapus event listener saat komponen unmount
    return () => {
      window.removeEventListener("profileUpdated", handleProfileUpdated);
    };
  }, [userId]); // Dependensi pada userId: fetch ulang jika userId berubah (misal setelah login/logout)

  const handleLogout = () => {
    // Hapus userId dan token (jika ada) dari localStorage
    localStorage.removeItem("userId");
    // localStorage.removeItem("token"); // Contoh jika Anda menggunakan token

    // Redirect ke halaman login
    navigate("/login");
  };

  const toggleMenu = () => {
    setShowMenu((prev) => !prev);
  };

  // Tutup dropdown jika klik di luar menu
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowMenu(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Tentukan gambar profil mana yang akan ditampilkan
  let displayProfileImage = "https://i.pravatar.cc/40?img=12"; // Gambar avatar dummy default

  if (loading) {
    displayProfileImage =
      "https://via.placeholder.com/40/000B58/FFFFFF?text=..."; // Placeholder saat memuat
  } else if (error || !userProfile || !userProfile.profile_photo) {
    // Jika ada error, userProfile kosong, atau tidak ada profile_photo, gunakan placeholder generik
    displayProfileImage = "https://via.placeholder.com/40/000B58/FFFFFF?text=U"; // Placeholder user generik
  } else {
    // Jika ada profile_photo, gunakan URL-nya dengan cache busting
    displayProfileImage = `http://localhost:6543/static/${
      userProfile.profile_photo
    }?t=${Date.now()}`;
  }

  return (
    <nav className="bg-[#000B58] text-white px-6 py-4 shadow-md">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        {/* Logo */}
        <div className="text-2xl font-bold tracking-wide">
          <Link to="/dashboard">FILMFY</Link>
        </div>

        {/* Menu tengah */}
        <div className="flex space-x-8">
          <Link
            to="/favorites"
            className="hover:underline text-lg font-semibold"
          >
            Favorites
          </Link>
          <Link
            to="/watch-later"
            className="hover:underline text-lg font-semibold"
          >
            Watch Later
          </Link>
        </div>

        {/* User Avatar & Logout */}
        <div className="relative" ref={menuRef}>
          <img
            src={displayProfileImage} // Gunakan sumber gambar yang sudah ditentukan
            alt="User Avatar"
            onClick={toggleMenu}
            className="w-10 h-10 rounded-full border-2 border-white cursor-pointer object-cover"
          />

          {showMenu && (
            <div
              className="absolute right-0 w-44 bg-white text-black rounded shadow-lg z-50"
              style={{ top: "110%" }}
            >
              <button
                onClick={() => {
                  setShowMenu(false);
                  navigate("/profile");
                }}
                className="block w-full text-left px-4 py-2 hover:bg-gray-200"
              >
                Lihat Profil
              </button>
              {/* Tombol 'Switch Account' ini bisa menjadi duplikat Logout atau dihapus jika tidak ada fungsi khusus */}
              <button
                onClick={() => {
                  setShowMenu(false);
                  handleLogout();
                }}
                className="block w-full text-left px-4 py-2 hover:bg-gray-200"
              >
                Switch Account
              </button>
              <button
                onClick={() => {
                  setShowMenu(false);
                  handleLogout();
                }}
                className="block w-full text-left px-4 py-2 hover:bg-gray-200"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
