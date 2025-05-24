import React, { useState, useEffect } from "react";

export default function MovieForm({ onSave, onCancel, existingMovie }) {
  const [formData, setFormData] = useState({
    title: "",
    genre: "",
    year: "", // Biarkan sebagai string, backend akan handle konversi
    rating: "", // Biarkan sebagai string
    // Hapus 'poster' dari state utama
  });

  // State terpisah untuk File Object poster
  const [posterFile, setPosterFile] = useState(null);
  // State untuk preview gambar
  const [imagePreview, setImagePreview] = useState("");

  useEffect(() => {
    if (existingMovie) {
      setFormData({
        title: existingMovie.title || "",
        genre: existingMovie.genre || "",
        year: existingMovie.release_year
          ? String(existingMovie.release_year)
          : "", // Ambil dari release_year
        rating: existingMovie.rating ? String(existingMovie.rating) : "",
      });
      // Gunakan poster_url untuk preview jika ada, jika tidak, jangan tampilkan apa-apa
      setImagePreview(existingMovie.poster_url || "");
      setPosterFile(null); // Reset file saat edit
    } else {
      // Reset form jika tidak ada existingMovie (untuk kasus 'Add New')
      setFormData({ title: "", genre: "", year: "", rating: "" });
      setImagePreview("");
      setPosterFile(null);
    }
  }, [existingMovie]); // Jalankan saat existingMovie berubah

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
      setPosterFile(file); // <-- SIMPAN FILE OBJECT

      // Buat preview (tetap pakai FileReader tapi hanya untuk preview)
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    } else {
      setPosterFile(null);
      setImagePreview(existingMovie ? existingMovie.poster_url : ""); // Kembali ke preview lama jika ada
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

    // --- BUAT FormData DI SINI ---
    const dataToSend = new FormData();
    dataToSend.append("title", formData.title);
    dataToSend.append("genre", formData.genre);
    dataToSend.append("release_year", formData.year); // Kirim sebagai string
    dataToSend.append("rating", formData.rating); // Kirim sebagai string

    // Tambahkan file HANYA jika ada file baru yang dipilih
    if (posterFile) {
      dataToSend.append("poster", posterFile);
    }
    // ----------------------------

    // Kirim FormData ke parent (atau panggil context langsung)
    onSave(dataToSend, existingMovie ? existingMovie.id : null);

    // Reset form (mungkin lebih baik dilakukan di parent setelah save sukses)
    // setFormData({ title: "", genre: "", year: "", rating: "" });
    // setImagePreview("");
    // setPosterFile(null);
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-md max-w-md w-full mx-auto mt-8">
      <h2 className="text-2xl font-bold mb-4 text-center">
        {existingMovie ? "Edit Movie" : "Add New Movie"}
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* ... Input fields Anda (sudah cukup baik) ... */}
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
          type="text"
          name="year"
          placeholder="Release Year"
          value={formData.year}
          onChange={(e) => {
            const val = e.target.value;
            if (/^\d*$/.test(val) && val.length <= 4) {
              // Batasi 4 digit
              setFormData((prev) => ({ ...prev, year: val }));
            }
          }}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg"
        />
        <input
          type="text"
          name="rating"
          placeholder="Rating (1-10)"
          value={formData.rating}
          onChange={(e) => {
            const val = e.target.value;
            if (/^([1-9]|10)?$/.test(val)) {
              setFormData((prev) => ({ ...prev, rating: val }));
            }
          }}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg"
        />
        <div>
          <label htmlFor="poster" className="block text-gray-700">
            Poster (Image)
          </label>
          <input
            type="file"
            id="poster"
            name="poster"
            accept="image/png, image/jpeg, image/jpg" // Tambah accept
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
        {/* ... Tombol Anda (sudah cukup baik) ... */}
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
