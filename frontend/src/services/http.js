import axios from "axios";

export const http = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

http.interceptors.request.use((config) => {
  const t = localStorage.getItem("token");
  if (t) config.headers.Authorization = `Bearer ${t}`;
  else delete config.headers.Authorization;
  return config;
});