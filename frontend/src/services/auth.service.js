import { http, setAuthToken } from "./http";

export async function login(email, password) {
  const res = await http.post("/auth/login", { email, password });
  // asumsi backend balikin { access_token: "...", token_type: "bearer" }
  setAuthToken(res.data.access_token);
  return res.data;
}

export function logout() {
  setAuthToken(null);
}
