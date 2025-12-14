import { ref, computed } from "vue";

const token = ref(localStorage.getItem("token") || "");
const user = ref(JSON.parse(localStorage.getItem("user") || "null"));

function setAuth(newToken, newUser) {
  token.value = newToken;
  user.value = newUser;
  localStorage.setItem("token", newToken);
  localStorage.setItem("user", JSON.stringify(newUser));
}

function logout() {
  token.value = "";
  user.value = null;
  localStorage.removeItem("token");
  localStorage.removeItem("user");
}

const isAuthed = computed(() => !!token.value);
const role = computed(() => user.value?.role || "GUEST");

export function useAuth() {
  return { token, user, role, isAuthed, setAuth, logout };
}
