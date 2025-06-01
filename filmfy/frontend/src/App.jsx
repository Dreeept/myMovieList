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
import ProtectedRoute from "./components/ProtectedRoute";
import AllMoviesPage from "./pages/AllMoviesPage"; // <-- Import halaman baru

export default function App() {
  return (
    <MoviesProvider>
      <Router>
        {/* Navbar sekarang dirender di dalam ProtectedRoute */}
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/movies" element={<AllMoviesPage />} />{" "}
            {/* <-- Rute Baru */}
            <Route path="/favorites" element={<Favorites />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/profile/edit" element={<ProfileEdit />} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Route>

          {/* Fallback jika tidak ada yang cocok dan tidak login */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    </MoviesProvider>
  );
}
