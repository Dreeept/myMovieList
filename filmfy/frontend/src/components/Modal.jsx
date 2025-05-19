import React, { useState } from "react";

export default function Modal({ onClose, onSubmit }) {
  const [movieTitle, setMovieTitle] = useState("");
  const [moviePoster, setMoviePoster] = useState("");
  const [releaseDate, setReleaseDate] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    // Create new movie object
    const newMovie = {
      title: movieTitle,
      posterUrl: moviePoster,
      release_date: releaseDate,
    };
    // Pass the new movie data to parent component
    onSubmit(newMovie);
  };

  return (
    <div className="fixed inset-0 bg-gray-700 bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-gray-800 p-6 rounded-lg w-1/3">
        <h3 className="text-2xl font-semibold text-white mb-4">Tambah Film</h3>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="movieTitle" className="block text-white">
              Judul Film
            </label>
            <input
              type="text"
              id="movieTitle"
              className="w-full p-2 mt-1 bg-gray-700 text-white rounded-md focus:outline-none"
              value={movieTitle}
              onChange={(e) => setMovieTitle(e.target.value)}
              required
            />
          </div>
          <div className="mb-4">
            <label htmlFor="moviePoster" className="block text-white">
              URL Poster
            </label>
            <input
              type="url"
              id="moviePoster"
              className="w-full p-2 mt-1 bg-gray-700 text-white rounded-md focus:outline-none"
              value={moviePoster}
              onChange={(e) => setMoviePoster(e.target.value)}
              required
            />
          </div>
          <div className="mb-4">
            <label htmlFor="releaseDate" className="block text-white">
              Tanggal Rilis
            </label>
            <input
              type="date"
              id="releaseDate"
              className="w-full p-2 mt-1 bg-gray-700 text-white rounded-md focus:outline-none"
              value={releaseDate}
              onChange={(e) => setReleaseDate(e.target.value)}
              required
            />
          </div>
          <div className="flex justify-between">
            <button
              type="submit"
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Tambah Film
            </button>
            <button
              type="button"
              onClick={onClose}
              className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
            >
              Tutup
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
