import { http } from "./http";

export async function adminGetUsers() {
  const res = await http.get("/admin/users");
  return res.data;
}

export async function adminCreateUser(payload) {
  // payload: { name, email, password, role }
  const res = await http.post("/admin/users", payload);
  return res.data;
}

export async function adminUpdateUserRole(userId, role) {
  const res = await http.patch(`/admin/users/${userId}/role`, { role });
  return res.data;
}
