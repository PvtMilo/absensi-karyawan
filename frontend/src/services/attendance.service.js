import { http } from "./http";

export async function adminGetAttendance({ day, user_id, limit = 50, offset = 0 }) {
  const params = {};
  if (day) params.day = day;
  if (user_id) params.user_id = user_id;
  params.limit = limit;
  params.offset = offset;

  const res = await http.get("/admin/attendance", { params });
  return res.data;
}
