import React, { useState, useEffect } from "react";

export default function UserForm({ onSave, onCancel, existingUser }) {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
  });

  useEffect(() => {
    if (existingUser) {
      setFormData(existingUser);
    }
  }, [existingUser]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.name || !formData.email) {
      alert("Nama dan email wajib diisi!");
      return;
    }
    onSave(formData);
    setFormData({ name: "", email: "" });
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-md max-w-md w-full mx-auto mt-8">
      <h2 className="text-2xl font-bold mb-4 text-center">
        {existingUser ? "Edit User" : "Add New User"}
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          name="name"
          placeholder="Full Name"
          value={formData.name}
          onChange={handleChange}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg"
        />
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={formData.email}
          onChange={handleChange}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg"
        />
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
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded"
          >
            {existingUser ? "Update" : "Add"}
          </button>
        </div>
      </form>
    </div>
  );
}
