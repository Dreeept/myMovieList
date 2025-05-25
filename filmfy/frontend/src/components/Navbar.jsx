import React, { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();
  const menuRef = useRef(); // Untuk menutup dropdown saat klik di luar

  const [showMenu, setShowMenu] = useState(false);
  const [loggedInUserProfile, setLoggedInUserProfile] = useState(null);
  const [loadingProfile, setLoadingProfile] = useState(false);
  // const [profileError, setProfileError] = useState(null); // Bisa ditambahkan jika ingin menampilkan error

  // Ambil userId dari localStorage
  const userId = localStorage.getItem("userId");

  // Fungsi untuk mengambil data profil pengguna yang login
  const fetchLoggedInUserProfile = async () => {
    if (!userId) {
      setLoggedInUserProfile(null); // Tidak ada user yang login
      setLoadingProfile(false);
      return;
    }

    setLoadingProfile(true);
    // setProfileError(null);
    try {
      const response = await fetch(`http://localhost:6543/api/user/${userId}`);
      if (!response.ok) {
        // Jika user tidak ditemukan (misal setelah dihapus) atau error lain
        setLoggedInUserProfile(null); // Anggap tidak ada profil
        throw new Error("Gagal mengambil data profil pengguna.");
      }
      const data = await response.json();
      setLoggedInUserProfile(data); // Set data profil ke state
    } catch (err) {
      // setProfileError(err.message);
      console.error("Error saat mengambil data profil untuk Navbar:", err);
      setLoggedInUserProfile(null); // Kosongkan profil jika error
    } finally {
      setLoadingProfile(false);
    }
  };

  // useEffect untuk mengambil data profil saat komponen dimuat atau userId berubah
  useEffect(() => {
    fetchLoggedInUserProfile();

    // Ini adalah contoh jika Anda ingin Navbar otomatis update
    // jika ada event 'profileUpdated' dari halaman lain (misal ProfileEdit)
    const handleProfileUpdated = () => {
      fetchLoggedInUserProfile();
    };
    window.addEventListener("profileUpdated", handleProfileUpdated);

    return () => {
      window.removeEventListener("profileUpdated", handleProfileUpdated);
    };
  }, [userId]); // Dependensi pada userId

  const handleLogout = () => {
    localStorage.removeItem("userId");
    // localStorage.removeItem("userData"); // Hapus juga jika ada
    setLoggedInUserProfile(null); // Bersihkan state profil
    setShowMenu(false); // Tutup menu
    navigate("/login");
  };

  const toggleMenu = () => {
    setShowMenu((prev) => !prev);
  };

  // Efek untuk menutup dropdown jika klik di luar
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
  let displayProfileImage = "https://i.pravatar.cc/40?img=70"; // Avatar default jika tidak login / error
  if (loadingProfile) {
    displayProfileImage =
      "https://via.placeholder.com/40/000B58/FFFFFF?text=..."; // Saat loading
  } else if (loggedInUserProfile && loggedInUserProfile.profile_url) {
    // Gunakan profile_url dari API (sudah lengkap) dan tambahkan cache buster
    displayProfileImage = `${loggedInUserProfile.profile_url}?t=${Date.now()}`;
  } else if (loggedInUserProfile) {
    // Pengguna ada tapi tidak ada foto profil, gunakan inisial atau placeholder
    const initial = loggedInUserProfile.username
      ? loggedInUserProfile.username.charAt(0).toUpperCase()
      : "U";
    displayProfileImage = `https://via.placeholder.com/40/000B58/FFFFFF?text=${initial}`;
  }

  return (
    <nav className="bg-[#000B58] text-white px-6 py-4 shadow-md">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <div className="text-2xl font-bold tracking-wide">
          <Link to={userId ? "/dashboard" : "/login"}>FILMFY</Link>
        </div>

        <div className="flex space-x-8">
          {userId && ( // Hanya tampilkan jika sudah login
            <Link
              to="/favorites"
              className="hover:underline text-lg font-semibold"
            >
              Favorites
            </Link>
          )}
          {/* Anda bisa menambahkan link lain di sini */}
        </div>

        <div className="relative" ref={menuRef}>
          <img
            src={displayProfileImage}
            alt="User Avatar"
            onClick={userId ? toggleMenu : () => navigate("/login")} // Jika belum login, klik avatar arahkan ke login
            className="w-10 h-10 rounded-full border-2 border-white cursor-pointer object-cover"
          />
          {showMenu &&
            userId &&
            loggedInUserProfile && ( // Hanya tampilkan menu jika sudah login
              <div className="absolute right-0 mt-2 w-48 bg-white text-black rounded-md shadow-lg z-50 py-1">
                <div className="px-4 py-3 border-b border-gray-200">
                  <p className="text-sm text-gray-700">Masuk sebagai</p>
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {loggedInUserProfile.username}
                  </p>
                </div>
                <button
                  onClick={() => {
                    setShowMenu(false);
                    navigate("/profile");
                  }}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Lihat Profil
                </button>
                <button
                  onClick={handleLogout}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
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
