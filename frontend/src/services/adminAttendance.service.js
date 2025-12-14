import { http } from "./http";

export async function adminGetAttendance(params = {}) {
  // params bisa: { user_id, date_from, date_to }
  const res = await http.get("/admin/attendance", { params });
  return res.data;
}