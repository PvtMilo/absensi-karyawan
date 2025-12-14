<template>
  <div style="padding:16px; max-width:900px; margin:0 auto;">
    <h2>Staff — Absensi</h2>

    <p v-if="error" style="color:#c00;">{{ error }}</p>
    <p v-if="info" style="color:#060;">{{ info }}</p>

    <!-- GPS -->
    <div style="border:1px solid #ddd; border-radius:8px; padding:12px; margin:12px 0;">
      <h3 style="margin:0 0 8px;">GPS</h3>

      <button @click="getLocation" :disabled="loadingLoc">
        {{ loadingLoc ? "Mengambil lokasi..." : "Ambil Lokasi" }}
      </button>

      <div style="margin-top:8px; font-size:14px;">
        <div>lat: <b>{{ loc?.lat ?? "-" }}</b></div>
        <div>lng: <b>{{ loc?.lng ?? "-" }}</b></div>
        <div>accuracy: <b>{{ loc?.accuracy_m ?? "-" }}</b> m</div>
      </div>
    </div>

    <!-- Selfie -->
    <div style="border:1px solid #ddd; border-radius:8px; padding:12px; margin:12px 0;">
      <h3 style="margin:0 0 8px;">Selfie</h3>

      <div style="display:flex; gap:12px; flex-wrap:wrap;">
        <div>
          <video ref="videoEl" autoplay playsinline style="width:280px; border:1px solid #ccc; border-radius:8px;"></video>
          <div style="margin-top:8px; display:flex; gap:8px;">
            <button @click="startCamera" :disabled="camOn">Start Camera</button>
            <button @click="stopCamera" :disabled="!camOn">Stop</button>
          </div>
          <div style="margin-top:8px;">
            <button @click="captureSelfie" :disabled="!camOn">Capture</button>
            <button @click="resetSelfie" :disabled="!selfieFile">Reset</button>
          </div>
        </div>

        <div>
          <div style="font-size:12px; opacity:.8;">Preview</div>
          <img v-if="selfiePreview" :src="selfiePreview" style="width:280px; border:1px solid #ccc; border-radius:8px;" />
          <div v-else style="width:280px; height:210px; border:1px dashed #aaa; border-radius:8px; display:flex; align-items:center; justify-content:center; opacity:.6;">
            belum ada selfie
          </div>
          <div style="margin-top:8px; font-size:12px; opacity:.8;">
            file: {{ selfieFile ? selfieFile.name : "-" }}
          </div>
        </div>
      </div>

      <canvas ref="canvasEl" style="display:none;"></canvas>
    </div>

    <!-- Actions -->
    <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top:12px;">
      <button @click="doCheckIn" :disabled="loadingAction">CHECK-IN</button>
      <button @click="doCheckOut" :disabled="loadingAction">CHECK-OUT</button>
    </div>

    <!-- Result -->
    <div v-if="lastResult" style="margin-top:14px; border:1px solid #ddd; border-radius:8px; padding:12px;">
      <h3 style="margin:0 0 8px;">Last Response</h3>
      <pre style="white-space:pre-wrap;">{{ JSON.stringify(lastResult, null, 2) }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount } from "vue";
import { checkIn, checkOut } from "../services/attendance.service";

const videoEl = ref(null);
const canvasEl = ref(null);

const camOn = ref(false);
let stream = null;

const loadingLoc = ref(false);
const loadingAction = ref(false);

const loc = ref(null); // {lat, lng, accuracy_m}
const selfieFile = ref(null);
const selfiePreview = ref("");

const lastResult = ref(null);
const error = ref("");
const info = ref("");

function clearMsg() {
  error.value = "";
  info.value = "";
}

async function getLocation() {
  clearMsg();
  loadingLoc.value = true;

  try {
    const pos = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 0,
      });
    });

    loc.value = {
      lat: pos.coords.latitude,
      lng: pos.coords.longitude,
      accuracy_m: pos.coords.accuracy,
    };

    info.value = "Lokasi berhasil diambil.";
  } catch (e) {
    error.value = e.message || "Gagal ambil lokasi. Pastikan izin lokasi aktif.";
  } finally {
    loadingLoc.value = false;
  }
}

async function startCamera() {
  clearMsg();
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "user" },
      audio: false,
    });
    videoEl.value.srcObject = stream;
    camOn.value = true;
  } catch (e) {
    error.value = e.message || "Gagal akses kamera. Pastikan izin kamera aktif.";
  }
}

function stopCamera() {
  if (stream) {
    stream.getTracks().forEach(t => t.stop());
    stream = null;
  }
  if (videoEl.value) videoEl.value.srcObject = null;
  camOn.value = false;
}

async function captureSelfie() {
  clearMsg();
  if (!videoEl.value) return;

  const v = videoEl.value;
  const c = canvasEl.value;

  c.width = v.videoWidth || 640;
  c.height = v.videoHeight || 480;

  const ctx = c.getContext("2d");
  ctx.drawImage(v, 0, 0, c.width, c.height);

  const blob = await new Promise(resolve => c.toBlob(resolve, "image/jpeg", 0.92));
  if (!blob) {
    error.value = "Gagal capture selfie.";
    return;
  }

  const file = new File([blob], `selfie_${Date.now()}.jpg`, { type: "image/jpeg" });
  selfieFile.value = file;

  if (selfiePreview.value) URL.revokeObjectURL(selfiePreview.value);
  selfiePreview.value = URL.createObjectURL(file);

  info.value = "Selfie berhasil di-capture.";
}

function resetSelfie() {
  if (selfiePreview.value) URL.revokeObjectURL(selfiePreview.value);
  selfiePreview.value = "";
  selfieFile.value = null;
}

function validateBeforeSend() {
  if (!loc.value) return "GPS belum diambil.";
  if (!selfieFile.value) return "Selfie belum di-capture.";
  return null;
}

async function doCheckIn() {
  clearMsg();
  const err = validateBeforeSend();
  if (err) return (error.value = err);

  loadingAction.value = true;
  try {
    const res = await checkIn({
      lat: loc.value.lat,
      lng: loc.value.lng,
      accuracy_m: loc.value.accuracy_m,
      selfieFile: selfieFile.value,
    });
    lastResult.value = res;
    info.value = "Check-in sukses.";
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || "Check-in gagal";
  } finally {
    loadingAction.value = false;
  }
}

async function doCheckOut() {
  clearMsg();
  const err = validateBeforeSend();
  if (err) return (error.value = err);

  loadingAction.value = true;
  try {
    const res = await checkOut({
      lat: loc.value.lat,
      lng: loc.value.lng,
      accuracy_m: loc.value.accuracy_m,
      selfieFile: selfieFile.value,
    });
    lastResult.value = res;
    info.value = "Check-out sukses.";
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || "Check-out gagal";
  } finally {
    loadingAction.value = false;
  }
}

onBeforeUnmount(() => {
  stopCamera();
  if (selfiePreview.value) URL.revokeObjectURL(selfiePreview.value);
});
</script>
