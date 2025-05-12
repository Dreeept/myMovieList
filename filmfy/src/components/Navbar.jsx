import React from 'react';
import { Link } from 'react-router-dom';

export default function Navbar() {
  const profileImage = 'https://i.pravatar.cc/40?img=12'; // Gambar avatar dummy

  return (
    <nav className="bg-gray-800 text-white px-6 py-4 shadow-md">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        {/* Logo */}
        <div className="text-2xl font-bold tracking-wide">
          <Link to="/">🎬 MyMovieList</Link>
        </div>

        {/* Navigation Links */}
        <div className="space-x-6 text-sm md:text-base">
          <Link to="/" className="hover:text-yellow-400 transition">Home</Link>
          <Link to="/favorites" className="hover:text-yellow-400 transition">Favorites</Link>
          <Link to="/add" className="hover:text-yellow-400 transition">Add Movie</Link>
        </div>

        {/* User Avatar & Logout */}
        <div className="flex items-center space-x-4">
          <img
            src={profileImage}
            alt="User Avatar"
            className="w-10 h-10 rounded-full border-2 border-white"
          />
          <button
            onClick={() => alert('Logout dummy')}
            className="bg-red-500 hover:bg-red-600 px-3 py-1 rounded-md text-sm md:text-base transition"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
