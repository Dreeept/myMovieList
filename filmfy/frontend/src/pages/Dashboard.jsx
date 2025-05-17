import React from 'react';
import Navbar from '../components/Navbar'; // import Navbar
import MovieList from '../components/MovieList';

export default function Dashboard() {
  return (
    <>
      <Navbar /> {/* <-- Ini yang belum kamu tampilkan */}
      <MovieList />
    </>
  );
}
