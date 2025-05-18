import React, { useState, useEffect } from "react";

export default function MovieForm({ onSave, onCancel, existingMovie }) {
  const [formData, setFormData] = useState({
    title: "",
    genre: "",
    year: "",
    rating: "",
    poster: "",
  });

  // State untuk gambar sementara
  const [imagePreview, setImagePreview] = useState("");

  useEffect(() => {
    if (existingMovie) {
      setFormData(existingMovie);
      setImagePreview(existingMovie.poster); // Menampilkan gambar poster yang sudah ada
    }
  }, [existingMovie]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result); // Set gambar yang di-upload sebagai preview
        setFormData((prev) => ({
          ...prev,
          poster: reader.result, // Simpan gambar dalam format base64
        }));
      };
      reader.readAsDataURL(file); // Mengubah gambar menjadi format base64
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (
      !formData.title ||
      !formData.genre ||
      !formData.year ||
      !formData.rating
    ) {
      alert("Semua field wajib diisi!");
      return;
    }

    onSave(formData);
    setFormData({
      title: "",
      genre: "",
      year: "",
      rating: "",
      poster: "",
    });
    setImagePreview("");
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-md max-w-md w-full mx-auto mt-8">
      <h2 className="text-2xl font-bold mb-4 text-center">
        {existingMovie ? "Edit Movie" : "Add New Movie"}
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          name="title"
          placeholder="Movie Title"
          value={formData.title}
          onChange={handleChange}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg"
        />
        <input
          type="text"
          name="genre"
          placeholder="Genre"
          value={formData.genre}
          onChange={handleChange}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg"
        />
        <input
          type="number"
          name="year"
          placeholder="Release Year"
          value={formData.year}
          onChange={handleChange}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg"
        />
        <input
          type="number"
          name="rating"
          placeholder="Rating (1-10)"
          value={formData.rating}
          onChange={handleChange}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg"
          min="1"
          max="10"
        />
        <div>
          <label htmlFor="poster" className="block text-gray-700">
            Poster (Image)
          </label>
          <input
            type="file"
            id="poster"
            name="poster"
            onChange={handleFileChange}
            className="w-full px-4 py-2 mt-1 border border-gray-300 rounded-lg"
          />
          {imagePreview && (
            <div className="mt-4">
              <img
                src={imagePreview}
                alt="Preview"
                className="w-full h-40 object-cover rounded-lg"
              />
            </div>
          )}
        </div>
        <div className="flex justify-between">
          <button
            type="button"
            onClick={onCancel}
            className="bg-gray-400 hover:bg-gray-500 text-white px-4 py-2 rounded"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
          >
            {existingMovie ? "Update" : "Add"}
          </button>
        </div>
      </form>
    </div>
  );
}
