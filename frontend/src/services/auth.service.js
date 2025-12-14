import { http } from "./http";

export async function login(email, password) {
  const res = await http.post("/auth/login", { email, password });
  return res.data; // { access_token }
}

export async function me() {
  const res = await http.get("/auth/me");
  return res.data; // { id, name, email, role }
}
