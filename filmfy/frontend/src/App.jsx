// filmfy/frontend/src/App.jsx
import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Favorites from "./pages/Favorites";
import { MoviesProvider } from "./context/MovieContext";
import Profile from "./pages/Profile";
import ProfileEdit from "./pages/ProfileEdit";
import ProtectedRoute from "./components/ProtectedRoute"; // <-- Import ProtectedRoute
// Hapus import Navbar jika tidak digunakan di sini lagi

export default function App() {
  return (
    <MoviesProvider>
      {" "}
      {/* MoviesProvider bisa di dalam atau luar AuthProvider, tergantung kebutuhan */}
      <Router>
        <Routes>
          {/* Rute Publik: Login, Signup, dan root (yang mengarah ke login) */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          {/* Rute Dilindungi: Menggunakan ProtectedRoute */}
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/favorites" element={<Favorites />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/profile/edit" element={<ProfileEdit />} />
            {/* Jika ingin root mengarah ke dashboard saat login, tambahkan ini */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Route>

          {/* Jika ingin root mengarah ke login jika belum login */}
          <Route path="/" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    </MoviesProvider>
  );
}
