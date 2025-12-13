import axios from "axios";

export const http = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// simpan token in-memory + localStorage
export function setAuthToken(token) {
  if (token) {
    http.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    localStorage.setItem("token", token);
  } else {
    delete http.defaults.headers.common["Authorization"];
    localStorage.removeItem("token");
  }
}

// auto load token saat app dibuka
const saved = localStorage.getItem("token");
if (saved) setAuthToken(saved);
