<template>
  <div style="padding:16px; max-width:1100px; margin:0 auto;">
    <h2>Admin — Users</h2>

    <p v-if="error" style="color:#c00;">{{ error }}</p>
    <p v-if="info" style="color:#060;">{{ info }}</p>

    <!-- Actions -->
    <div style="display:flex; gap:8px; flex-wrap:wrap; margin:10px 0;">
      <button @click="load" :disabled="loading">
        {{ loading ? "Loading..." : "Refresh" }}
      </button>

      <input
        v-model="q"
        placeholder="Search name/email/role..."
        style="padding:8px; border:1px solid #ddd; border-radius:8px; min-width:240px;"
      />
    </div>

    <!-- Create User -->
    <div style="border:1px solid #ddd; border-radius:10px; padding:12px; margin:12px 0;">
      <h3 style="margin:0 0 10px;">Create User</h3>

      <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:flex-end;">
        <div>
          <div style="font-size:12px; opacity:.7;">Name</div>
          <input v-model="form.name" style="padding:8px; border:1px solid #ddd; border-radius:8px;" />
        </div>

        <div>
          <div style="font-size:12px; opacity:.7;">Email</div>
          <input v-model="form.email" style="padding:8px; border:1px solid #ddd; border-radius:8px;" />
        </div>

        <div>
          <div style="font-size:12px; opacity:.7;">Password</div>
          <input v-model="form.password" type="password" style="padding:8px; border:1px solid #ddd; border-radius:8px;" />
        </div>

        <div>
          <div style="font-size:12px; opacity:.7;">Role</div>
          <select v-model="form.role" style="padding:8px; border:1px solid #ddd; border-radius:8px;">
            <option value="STAFF">STAFF</option>
            <option value="ADMIN">ADMIN</option>
          </select>
        </div>

        <button @click="createUser" :disabled="creating">
          {{ creating ? "Creating..." : "Create" }}
        </button>
      </div>

      <div style="margin-top:8px; font-size:12px; opacity:.7;">
        Tips: buat akun STAFF dulu, nanti promote ke ADMIN kalau perlu.
      </div>
    </div>

    <!-- Users Table -->
    <div style="border:1px solid #ddd; border-radius:10px; overflow:hidden;">
      <div style="padding:12px; border-bottom:1px solid #eee; display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap;">
        <div><b>Total:</b> {{ filtered.length }}</div>
        <div style="font-size:12px; opacity:.7;">Klik role untuk toggle, atau edit name.</div>
      </div>

      <div style="overflow:auto;">
        <table style="width:100%; border-collapse:collapse;">
          <thead>
            <tr style="background:#f7f7f7;">
              <th style="text-align:left; padding:10px; border-bottom:1px solid #eee;">ID</th>
              <th style="text-align:left; padding:10px; border-bottom:1px solid #eee;">Name</th>
              <th style="text-align:left; padding:10px; border-bottom:1px solid #eee;">Email</th>
              <th style="text-align:left; padding:10px; border-bottom:1px solid #eee;">Role</th>
              <th style="text-align:left; padding:10px; border-bottom:1px solid #eee;">Created</th>
              <th style="text-align:left; padding:10px; border-bottom:1px solid #eee;">Actions</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="u in filtered" :key="u.id">
              <td style="padding:10px; border-bottom:1px solid #f0f0f0;">{{ u.id }}</td>

              <td style="padding:10px; border-bottom:1px solid #f0f0f0;">
                <div v-if="editId !== u.id" style="display:flex; gap:8px; align-items:center;">
                  <span>{{ u.name }}</span>
                  <button @click="startEdit(u)" style="font-size:12px;">Edit</button>
                </div>

                <div v-else style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
                  <input v-model="editName" style="padding:6px; border:1px solid #ddd; border-radius:8px;" />
                  <button @click="saveEdit(u)" :disabled="savingEdit">Save</button>
                  <button @click="cancelEdit" :disabled="savingEdit">Cancel</button>
                </div>
              </td>

              <td style="padding:10px; border-bottom:1px solid #f0f0f0;">{{ u.email }}</td>

              <td style="padding:10px; border-bottom:1px solid #f0f0f0;">
                <button @click="toggleRole(u)" :disabled="roleBusyId === u.id">
                  {{ u.role }}
                </button>
              </td>

              <td style="padding:10px; border-bottom:1px solid #f0f0f0;">
                {{ formatDateTime(u.created_at) }}
              </td>

              <td style="padding:10px; border-bottom:1px solid #f0f0f0;">
                <div style="display:flex; gap:8px; flex-wrap:wrap;">
                  <button @click="openReset(u)">Reset Password</button>
                </div>
              </td>
            </tr>

            <tr v-if="filtered.length === 0">
              <td colspan="6" style="padding:14px; opacity:.7;">No users.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Reset Password Modal (simple) -->
    <div v-if="resetOpen" style="position:fixed; inset:0; background:rgba(0,0,0,.35); display:flex; align-items:center; justify-content:center; padding:16px;">
      <div style="background:#fff; border-radius:12px; width:min(520px, 100%); padding:14px;">
        <h3 style="margin:0 0 10px;">Reset Password</h3>
        <div style="font-size:14px; margin-bottom:10px;">
          User: <b>{{ resetUser?.email }}</b>
        </div>

        <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:flex-end;">
          <div style="flex:1; min-width:240px;">
            <div style="font-size:12px; opacity:.7;">New Password</div>
            <input v-model="resetPass" type="password" style="width:100%; padding:8px; border:1px solid #ddd; border-radius:8px;" />
          </div>
          <button @click="doResetPassword" :disabled="resetting">
            {{ resetting ? "Saving..." : "Save" }}
          </button>
          <button @click="closeReset" :disabled="resetting">Cancel</button>
        </div>

        <div style="margin-top:10px; font-size:12px; opacity:.7;">
          Catatan: password baru minimal 6 dan maksimal 72 karakter (bcrypt limit).
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import {
  adminListUsers,
  adminCreateUser,
  adminUpdateUser,
  adminResetPassword,
} from "../services/adminUsers.service";

const users = ref([]);
const loading = ref(false);
const creating = ref(false);
const savingEdit = ref(false);
const roleBusyId = ref(null);

const error = ref("");
const info = ref("");
const q = ref("");

const form = ref({
  name: "",
  email: "",
  password: "",
  role: "STAFF",
});

const editId = ref(null);
const editName = ref("");

const resetOpen = ref(false);
const resetUser = ref(null);
const resetPass = ref("");
const resetting = ref(false);

function clearMsg() {
  error.value = "";
  info.value = "";
}

function formatDateTime(s) {
  if (!s) return "-";
  // iso -> "YYYY-MM-DD HH:mm:ss"
  return String(s).replace("T", " ").split(".")[0];
}

const filtered = computed(() => {
  const term = q.value.trim().toLowerCase();
  if (!term) return users.value;

  return users.value.filter((u) => {
    const hay = `${u.id} ${u.name} ${u.email} ${u.role}`.toLowerCase();
    return hay.includes(term);
  });
});

async function load() {
  clearMsg();
  loading.value = true;
  try {
    users.value = await adminListUsers();
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || "Gagal load users";
  } finally {
    loading.value = false;
  }
}

async function createUser() {
  clearMsg();

  if (!form.value.name.trim()) return (error.value = "Name wajib diisi.");
  if (!form.value.email.trim()) return (error.value = "Email wajib diisi.");
  if (!form.value.password.trim()) return (error.value = "Password wajib diisi.");

  creating.value = true;
  try {
    const created = await adminCreateUser({
      name: form.value.name.trim(),
      email: form.value.email.trim(),
      password: form.value.password,
      role: form.value.role,
    });

    // update UI
    users.value = [created, ...users.value];

    // reset form
    form.value.name = "";
    form.value.email = "";
    form.value.password = "";
    form.value.role = "STAFF";

    info.value = "User berhasil dibuat.";
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || "Gagal create user";
  } finally {
    creating.value = false;
  }
}

function startEdit(u) {
  clearMsg();
  editId.value = u.id;
  editName.value = u.name || "";
}

function cancelEdit() {
  editId.value = null;
  editName.value = "";
}

async function saveEdit(u) {
  clearMsg();
  if (!editName.value.trim()) return (error.value = "Name tidak boleh kosong.");

  savingEdit.value = true;
  try {
    const updated = await adminUpdateUser(u.id, { name: editName.value.trim() });

    // replace in list
    users.value = users.value.map((x) => (x.id === updated.id ? updated : x));

    cancelEdit();
    info.value = "Name berhasil diupdate.";
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || "Gagal update user";
  } finally {
    savingEdit.value = false;
  }
}

async function toggleRole(u) {
  clearMsg();
  roleBusyId.value = u.id;

  try {
    const nextRole = u.role === "ADMIN" ? "STAFF" : "ADMIN";
    const updated = await adminUpdateUser(u.id, { role: nextRole });
    users.value = users.value.map((x) => (x.id === updated.id ? updated : x));
    info.value = `Role user ${u.email} -> ${nextRole}`;
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || "Gagal update role";
  } finally {
    roleBusyId.value = null;
  }
}

function openReset(u) {
  clearMsg();
  resetUser.value = u;
  resetPass.value = "";
  resetOpen.value = true;
}

function closeReset() {
  resetOpen.value = false;
  resetUser.value = null;
  resetPass.value = "";
}

async function doResetPassword() {
  clearMsg();
  if (!resetUser.value) return;
  if (!resetPass.value.trim()) return (error.value = "Password baru wajib diisi.");

  resetting.value = true;
  try {
    await adminResetPassword(resetUser.value.id, resetPass.value);
    info.value = "Password berhasil direset.";
    closeReset();
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || "Gagal reset password";
  } finally {
    resetting.value = false;
  }
}

onMounted(load);
</script>
