import React from "react";

export default function Modal({ children, onClose }) {
  // Fungsi ini mencegah modal tertutup saat area kontennya diklik
  const handleModalContentClick = (e) => {
    e.stopPropagation();
  };

  return (
    // Lapisan luar (overlay), klik di sini akan menutup modal
    <div
      className="fixed inset-0 bg-gray-600 bg-opacity-75 flex justify-center items-center z-50 p-4"
      onClick={onClose}
    >
      {/* Konten modal */}
      <div
        className="bg-white p-6 rounded-xl shadow-2xl max-w-md w-full"
        onClick={handleModalContentClick} // Cegah penutupan saat diklik
      >
        {/* Tombol tutup bisa ditambahkan di sini jika mau */}
        {/* Tampilkan konten yang diberikan (yaitu MovieForm) */}
        {children}
      </div>
    </div>
  );
}
