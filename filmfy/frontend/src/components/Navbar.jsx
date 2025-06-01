// filmfy/frontend/src/components/Navbar.jsx
import React, { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const navigate = useNavigate();
  const menuRef = useRef();

  const [showMenu, setShowMenu] = useState(false);
  const { isAuthenticated, user, logout, loading } = useAuth();

  const handleLogout = async () => {
    setShowMenu(false);
    await logout();
    navigate("/login");
  };

  const toggleMenu = () => {
    setShowMenu((prev) => !prev);
  };

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

  let displayProfileImage = "https://i.pravatar.cc/40?img=70";
  if (loading) {
    displayProfileImage = "https://placehold.co/40/CCCCCC/FFFFFF/png?text=L"; // <-- Ganti placeholder
  } else if (isAuthenticated && user) {
    if (user.profile_url) {
      displayProfileImage = `${user.profile_url}?t=${Date.now()}`;
    } else {
      const initial = user.username
        ? user.username.charAt(0).toUpperCase()
        : "U";
      displayProfileImage = `https://placehold.co/40/000B58/FFFFFF/png?text=${initial}`; // <-- Ganti placeholder
    }
  }

  return (
    <nav className="bg-[#000B58] text-white px-6 py-4 shadow-md sticky top-0 z-50">
      {" "}
      {/* Tambah sticky */}
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <div className="text-2xl font-bold tracking-wide">
          <Link to={isAuthenticated ? "/dashboard" : "/login"}>FILMFY</Link>
        </div>

        {/* Tampilkan menu jika sudah login */}
        {isAuthenticated && (
          <div className="hidden md:flex space-x-8 items-center">
            {" "}
            {/* hidden md:flex untuk responsif */}
            <Link
              to="/dashboard"
              className="hover:underline text-lg font-semibold"
            >
              Dashboard
            </Link>
            <Link
              to="/movies" // <-- LINK BARU
              className="hover:underline text-lg font-semibold"
            >
              Movies
            </Link>
            <Link
              to="/favorites"
              className="hover:underline text-lg font-semibold"
            >
              Favorites
            </Link>
          </div>
        )}

        <div className="relative" ref={menuRef}>
          <img
            src={displayProfileImage}
            alt="User Avatar"
            onClick={isAuthenticated ? toggleMenu : () => navigate("/login")}
            className="w-10 h-10 rounded-full border-2 border-white cursor-pointer object-cover"
          />
          {showMenu && isAuthenticated && user && (
            <div className="absolute right-0 mt-2 w-56 bg-white text-black rounded-md shadow-lg z-50 py-1">
              <div className="px-4 py-3 border-b border-gray-200">
                <p className="text-sm text-gray-700">Masuk sebagai</p>
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user.username}
                </p>
              </div>
              {/* Menu untuk mobile/dropdown */}
              <div className="md:hidden">
                <Link
                  to="/dashboard"
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  onClick={() => setShowMenu(false)}
                >
                  Dashboard
                </Link>
                <Link
                  to="/movies"
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  onClick={() => setShowMenu(false)}
                >
                  Movies
                </Link>
                <Link
                  to="/favorites"
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  onClick={() => setShowMenu(false)}
                >
                  Favorites
                </Link>
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
          {!loading && !isAuthenticated && (
            <button
              onClick={() => navigate("/login")}
              className="bg-blue-600 text-white px-4 py-1 rounded-lg hover:bg-blue-700"
            >
              Login
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}
