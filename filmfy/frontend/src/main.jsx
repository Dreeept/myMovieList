// filmfy/frontend/src/main.jsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import axios from "axios"; // <-- Import axios
import { AuthProvider } from "./context/AuthContext"; // <-- Import AuthProvider

// <-- Setup Axios Global -->
axios.defaults.baseURL = "http://localhost:6543/api";
axios.defaults.withCredentials = true;
// <---------------------->

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <AuthProvider>
      {" "}
      {/* <-- Bungkus App dengan AuthProvider --> */}
      <App />
    </AuthProvider>
  </StrictMode>
);
