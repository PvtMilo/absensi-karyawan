import { http } from "./http";

export async function adminListUsers() {
  const res = await http.get("/admin/users");
  return res.data;
}

export async function adminCreateUser(payload) {
  const res = await http.post("/admin/users", payload);
  return res.data;
}

export async function adminUpdateUser(userId, payload) {
  const res = await http.put(`/admin/users/${userId}`, payload);
  return res.data;
}

export async function adminResetPassword(userId, new_password) {
  const res = await http.post(`/admin/users/${userId}/reset-password`, { new_password });
  return res.data;
}
