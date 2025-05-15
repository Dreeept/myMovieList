import React, { useState, useEffect } from "react";
import UserForm from "./UserForm";

export default function UserList() {
  const [users, setUsers] = useState([]);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [editingUser, setEditingUser] = useState(null);

  useEffect(() => {
    const storedUsers = localStorage.getItem("users");
    if (storedUsers) setUsers(JSON.parse(storedUsers));
  }, []);

  useEffect(() => {
    localStorage.setItem("users", JSON.stringify(users));
  }, [users]);

  const handleAddClick = () => {
    setEditingUser(null);
    setIsFormVisible(true);
  };

  const handleEdit = (user) => {
    setEditingUser(user);
    setIsFormVisible(true);
  };

  const handleDelete = (id) => {
    if (window.confirm("Yakin ingin menghapus user ini?")) {
      setUsers(users.filter((user) => user.id !== id));
    }
  };

  const handleSave = (user) => {
    if (user.id) {
      setUsers(users.map((u) => (u.id === user.id ? user : u)));
    } else {
      const newUser = { ...user, id: Date.now() };
      setUsers([...users, newUser]);
    }
    setIsFormVisible(false);
    setEditingUser(null);
  };

  const handleCancel = () => {
    setIsFormVisible(false);
    setEditingUser(null);
  };

  return (
    <div className="px-6 py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">👥 User List</h1>
        <button
          className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md shadow"
          onClick={handleAddClick}
        >
          ➕ Add User
        </button>
      </div>

      {isFormVisible && (
        <UserForm
          onSave={handleSave}
          onCancel={handleCancel}
          existingUser={editingUser}
        />
      )}

      <div className="space-y-4">
        {users.length > 0 ? (
          users.map((user) => (
            <div
              key={user.id}
              className="bg-white p-4 rounded-lg shadow flex justify-between items-center"
            >
              <div>
                <h3 className="text-lg font-semibold">{user.name}</h3>
                <p className="text-gray-600">{user.email}</p>
              </div>
              <div className="space-x-4">
                <button
                  onClick={() => handleEdit(user)}
                  className="text-blue-600 hover:underline"
                >
                  ✏ Edit
                </button>
                <button
                  onClick={() => handleDelete(user.id)}
                  className="text-red-600 hover:underline"
                >
                  🗑 Delete
                </button>
              </div>
            </div>
          ))
        ) : (
          <p className="text-gray-600 text-center">
            Belum ada user yang ditambahkan.
          </p>
        )}
      </div>
    </div>
  );
}
