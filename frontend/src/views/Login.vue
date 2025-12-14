<template>
  <div style="min-height:100vh; display:flex; align-items:center; justify-content:center; padding:16px;">
    <div style="width:100%; max-width:420px; border:1px solid #ddd; border-radius:10px; padding:16px;">
      <h2 style="margin:0 0 12px;">Login</h2>

      <div style="margin-bottom:10px;">
        <label style="display:block; font-size:12px; opacity:.8;">Email</label>
        <input v-model="email" type="email" placeholder="user@example.com" style="width:100%; padding:10px;" />
      </div>

      <div style="margin-bottom:10px;">
        <label style="display:block; font-size:12px; opacity:.8;">Password</label>
        <input v-model="password" type="password" placeholder="••••••••" style="width:100%; padding:10px;" />
      </div>

      <p v-if="error" style="color:#c00; margin:8px 0;">{{ error }}</p>

      <button @click="doLogin" :disabled="loading" style="width:100%; padding:10px;">
        {{ loading ? "Logging in..." : "Login" }}
      </button>

      <div style="margin-top:12px; font-size:12px; opacity:.7;">
        Setelah login sukses, token disimpan di localStorage dan otomatis dipakai untuk request berikutnya.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuth } from "../stores/auth";
import { login, me } from "../services/auth.service";

const router = useRouter();

const email = ref("user@example.com");
const password = ref("");
const loading = ref(false);
const error = ref("");

const auth = useAuth();

async function doLogin() {
  const data = await login(email.value, password.value);
  // simpan token dulu supaya /auth/me bisa jalan
  auth.setAuth(data.access_token, null);

  const user = await me();
  auth.setAuth(data.access_token, user);

  // redirect sesuai role
  if (user.role === "ADMIN") router.push("/admin/attendance");
  else router.push("/attendance");
}
</script>
