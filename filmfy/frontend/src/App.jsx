// App.jsx
import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import Login from "./pages/Login"; // Sesuaikan path jika perlu
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Favorites from "./pages/Favorites";

export default function App() {
  const [movies, setMovies] = useState([]);

  // Load movies dari localStorage saat awal load aplikasi
  useEffect(() => {
    const storedMovies = localStorage.getItem("movies");
    if (storedMovies) {
      setMovies(JSON.parse(storedMovies));
    }
  }, []);

  // Simpan movies ke localStorage saat movies berubah
  useEffect(() => {
    localStorage.setItem("movies", JSON.stringify(movies));
  }, [movies]);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route
          path="/dashboard"
          element={<Dashboard movies={movies} setMovies={setMovies} />}
        />
        <Route
          path="/favorites"
          element={<Favorites movies={movies} setMovies={setMovies} />}
        />
      </Routes>
    </Router>
  );
}
