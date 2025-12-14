import { http } from "./http";

// ===== ADMIN =====
export async function adminGetAttendance({ day, user_id, limit = 50, offset = 0 }) {
  const params = {};
  if (day) params.day = day;
  if (user_id) params.user_id = user_id;
  params.limit = limit;
  params.offset = offset;

  const res = await http.get("/admin/attendance", { params });
  return res.data;
}

// ===== STAFF =====
export async function checkIn({ lat, lng, accuracy_m, selfieFile }) {
  const fd = new FormData();
  fd.append("lat", String(lat));
  fd.append("lng", String(lng));
  fd.append("accuracy_m", String(accuracy_m));
  fd.append("selfie", selfieFile); // nama field harus sama dengan backend

  const res = await http.post("/attendance/check-in", fd);
  return res.data;
}

export async function checkOut({ lat, lng, accuracy_m, selfieFile }) {
  const fd = new FormData();
  fd.append("lat", String(lat));
  fd.append("lng", String(lng));
  fd.append("accuracy_m", String(accuracy_m));
  fd.append("selfie", selfieFile);

  const res = await http.post("/attendance/check-out", fd);
  return res.data;
}

export async function getMyAttendance() {
  const res = await http.get("/attendance/me");
  return res.data;
}
