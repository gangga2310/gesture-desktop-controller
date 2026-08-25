# ROADMAP PROJECT — GestureDesktopController

> **Tujuan utama:** mengontrol volume Windows menggunakan gesture pinch melalui webcam.
>
> Roadmap ini disusun seolah-olah project dikerjakan dari nol, dengan tanda **status progres saat ini**.
> Setiap fase dilengkapi **catatan** (pengalaman, keputusan, dan masalah yang ditemukan).

---

## 📍 Status Ringkas

```text
Milestone 1 (Simulasi volume pinch) : ✅ SELESAI — sinyal cm + kalibrasi + filter stabil
Milestone 2 (Windows Audio / pycaw)  : ✅ KORE DONE — volume Windows naik/turun halus via pinch!
Posisi sekarang                      : FINALISASI — main.py + config kalibrasi (menunggu uji)
```

**Legenda:** `[✓]` selesai · `[~]` sebagian / masih bermasalah · `[ ]` belum dikerjakan

---

# Phase 0 — Setup & Environment

- [✓] Struktur project (`src/`, `tests/`, `models/`, `docs/`, `assets/`)
- [✓] Virtual environment (`venv`, Python 3.12.4)
- [✓] Git init + GitHub repo (`gangga2310/gesture-dekstop-controller`)
- [✓] `.gitignore` (venv, `__pycache__`, `.pytest_cache`, dll.)
- [✓] `requirements.txt` (mediapipe 0.10.35, opencv, numpy, PySide6, pycaw, comtypes, pytest)
- [✓] Model MediaPipe (`models/hand_landmarker.task`)

> 📝 **Catatan fase:** Environment sudah tuntas. Prompt terminal `(venv) (base) PS ...` berarti venv aktif —
> jalankan module langsung dengan `python -m src.debug.debug_pinch`, jangan mengetik ulang `(venv)`.
> `pycaw` + `comtypes` sudah terpasang sejak awal (dipakai fase 5 nanti).

---

# Phase 1 — Computer Vision Foundation

- [✓] Test kamera (`tests/camera_test.py`)
- [✓] Hand detection (`src/hand_detect.py` — script lama, referensi awal)
- [✓] Landmark reader (`src/landmark_reader.py` — script lama, import belum konsisten)
- [✓] **HandTracker** (`src/services/hand_tracker.py`) — wrapper MediaPipe Tasks API, `num_hands=2`, dipakai pipeline baru
- [✓] **Geometry utils** (`src/utils/geometry.py`) — `distance`, `distance_squared`, `midpoint`, `vector`, `vector_length`, `normalize_vector`, `clamp`, `map_range` (sudah ada guard `input_min == input_max`)
- [✓] **Drawing utils** (`src/utils/drawing.py`) — `draw_point`, `draw_label`, `draw_line`
- [ ] Math utils (`src/utils/math_utils.py` — masih kosong, diisi saat dibutuhkan)

> 📝 **Catatan fase:** `hand_detect.py` & `landmark_reader.py` adalah script eksperimen lama — pipeline baru
> memakai `HandTracker`. `landmark_reader.py` masih meng-import `from utils.drawing import ...` tanpa
> prefix `src.` → akan error jika dijalankan `python -m src.landmark_reader`. `tests/test_geometry.py`
> juga rusak (import `normalize` yang tidak ada) — perlu diperbaiki/dihapus nanti.

---

# Phase 2 — Gesture Recognition (Pinch)

- [✓] **Constants dirapikan** (`src/utils/constants.py`):
      `PINCH_THRESHOLD = 0.35`, `EMA_ALPHA = 0.25`, `DEAD_ZONE_THRESHOLD = 0.015`,
      `MIN_PINCH_RATIO = 0.20`, `MAX_PINCH_RATIO = 1.20`
- [✓] **Gesture utils** (`src/utils/gesture_utils.py`): `get_landmark`, `get_landmark_pixel`, `hand_scale` (Index MCP ↔ Pinky MCP), `relative_distance`, `pinch_ratio`, `pinch_distance`, `is_pinch`
- [✓] **GestureState** (`src/gesture/gesture_state.py`) — dataclass: `raw_value`, `filtered_value`, `stable_value`, `detected`
- [✓] **EMAFilter** (`src/filters/ema_filter.py`) — + unit test ✅ 10/10 passed
- [✓] **DeadZoneFilter** (`src/filters/dead_zone.py`) — + unit test ✅ 8/8 passed
- [✓] **PinchGesture** (`src/gesture/pinch.py`) — pipeline: raw ratio → EMA → Dead Zone → GestureState

> 📝 **Catatan fase:** Constants pernah tidak konsisten (`PINCH_THRESHOLD = 40` dari project lama vs ratio
> normalized ~0.35) — sudah diperbaiki. Pelajaran penting: file filter berada di `src/filters/`,
> **bukan** `src/utils/` (kesalahan import ini pernah terjadi di test EMA dan sudah dikoreksi).
> Setiap filter baru (Hysteresis, RateLimiter) wajib disertai unit test.

---

# Phase 3 — Milestone 1: Simulasi Volume Pinch

- [✓] **VolumeMapper** (`src/utils/volume_mapper.py`) — ratio 0.35–0.85 → volume 0–100%
- [✓] **Arah volume dibalik** sesuai preferensi: pinch penuh → 0%, tangan terbuka → 100%
- [✓] **debug_pinch.py** (`src/debug/debug_pinch.py`) — menampilkan: webcam, landmark thumb/index,
      garis pinch, pixel distance, FPS, status hand detected, gesture OPEN/PINCH,
      Raw/EMA/Stable ratio, volume simulasi, progress bar.
      Kontrol: `R` = reset filter, `ESC` = keluar.
- [✓] Pipeline berjalan tanpa error (warning MediaPipe seperti `Feedback manager...` dan
      `NORM_RECT...` adalah wajar, tidak mengganggu)
- [~] **Raw ratio masih terpengaruh jarak kamera** — saat pinch penuh volume hanya ~25–40%,
      padahal targetnya 0% (ditangani di fase 4)

> 📝 **Catatan fase:** Arah mapping sempat terbalik (pinch → volume naik); sudah dibalik sesuai preferensi.
> `VolumeMapper` memakai nilai hardcoded 0.35/0.85 — belum terhubung ke `MIN_PINCH_RATIO` /
> `MAX_PINCH_RATIO` di constants. Masalah utama yang ditemukan: nilai ratio berubah terhadap jarak
> kamera walau sudah dinormalisasi → keputusan: **jangan tambal dengan filter dulu**, cari dulu
> reference scale yang stabil secara geometris.

---

# Phase 4 — Stabilisasi ← **POSISI SEKARANG**

### 4.0 Stabilisasi Pembacaan & Penggambaran (anti-bergetar) ✅ SELESAI

- [✓] Buat `OneEuroFilter` (`src/filters/one_euro_filter.py`) — filter adaptif:
      mulus saat tangan diam, tetap responsif saat gerak cepat
- [✓] Buat `LandmarkSmoother` (`src/filters/landmark_smoother.py`) — smoothing
      21 landmark (x, y, z) memakai One Euro Filter
- [✓] Unit test One Euro Filter & LandmarkSmoother — 11/11 passed
- [✓] Integrasi ke `debug_pinch.py` — garis pinch, titik landmark, dan nilai
      pembacaan tidak bergetar lagi; tetap responsif saat gerak cepat
- [✓] Tuning — parameter default (`min_cutoff=1.0`, `beta=1.0`) sudah nyaman;
      angka pembacaan stabil (perubahan hanya 0.00x, jarang 0.01x)

### 4.1 Hand Scale Analyzer ← **SEDANG DIKERJAKAN**

- [~] Buat `src/debug/debug_hand_scale.py` (alat riset, bukan aplikasi final) — file sudah dibuat, menunggu dijalankan:
  - [ ] Pakai `HandTracker` + `LandmarkSmoother`, baca satu tangan
  - [ ] Hitung beberapa kandidat scale secara real-time (hasil riset — `docs/riset_hand_scale.md`):
    - Scale A — Index MCP ↔ Pinky MCP (yang dipakai `hand_scale()` sekarang, baseline)
    - Scale B — Wrist ↔ Middle MCP
    - Scale C — Wrist ↔ Middle Tip (diduga lemah: tip ikut menekuk saat pinch)
    - Scale D — rata-rata beberapa segment palm
    - Scale E — **ratio 3D** memakai `hand_world_landmarks` (koreksi perspektif)
    - Scale F — **sudut bukaan** ibu jari–telunjuk (invariant skala/rotasi)
  - [ ] Tampilkan nilai + metrik stabilitas real-time: gerakkan tangan dekat–sedang–jauh, pinch & terbuka
- [✓] **Pilih reference scale** — hasil pengukuran: pakai **jarak di bidang telapak (xy)
      dari `hand_world_landmarks` dalam cm** (bukan ratio, bukan 3D penuh — z menyesatkan;
      detail `docs/riset_hand_scale.md` §6–7)
- [✓] **Validasi jarak dengan penggaris** (`debug_distance.py`): 2 cm→2.2, 5 cm→4.7,
      8 cm→7.7 (akurat ±0.3 cm); terbuka penuh 13 cm asli → 9.6 cm (under ~26%)
      → keputusan: kalibrasi per-user untuk mapping volume
- [✓] Implementasi sinyal pinch cm: `gesture_utils` (`pinch_distance_cm`),
      `constants` (PINCH_CM_*), `VolumeMapper` (parametrik), `PinchGesture` (threshold cm),
      `debug_pinch.py` — **teruji stabil**, kalibrasi M/X berfungsi

### 4.2 Filter Lanjutan ✅ SELESAI

- [✓] **Hysteresis filter** (`src/filters/hysteresis.py`) — anti-flicker status PINCH/OPEN
      (aktif < threshold-band, mati > threshold+band) — 9/9 test passed
- [✓] **RateLimiter** (`src/filters/rate_limiter.py`) — volume naik/turun bertahap
      (50→52→54, bukan 50→80) — 8/8 test passed; + `hold()` agar tidak loncat
      saat tangan keluar-masuk frame
- [✓] Integrasi: `PinchGesture` (hysteresis_band), `debug_pinch.py` (rate limiter +
      volume dipertahankan saat tangan hilang) — **teruji stabil, disukai user**

### 4.3 Kalibrasi

- [✓] Kalibrasi manual via tombol di `debug_pinch.py`: M = set MIN (pinch penuh),
      X = set MAX (terbuka penuh), C = reset — **berfungsi baik, disukai user,
      akan dipertahankan di aplikasi final** (disimpan ke file config saat fase GUI)
- [ ] Kalibrasi per-user tersimpan ke file config (untuk fase GUI nanti)
- [ ] (Opsional) Kalibrasi dinamis otomatis (running min/max + hysteresis)

> 📝 **Catatan fase:** Stabilitas yang dimaksud ada **dua lapis**:
> 1) **Stabilitas pembacaan & penggambaran** — garis/titik/nilai di layar masih sangat bergetar
>    karena noise landmark MediaPipe antar-frame. Dikerjakan **dulu** lewat smoothing landmark
>    (One Euro Filter, `4.0`).
> 2) **Stabilitas gestur** — rasio berubah terhadap jarak kamera (analisis: `docs/riset_hand_scale.md`).
>    Dikerjakan **setelah** lapis 1 stabil, lewat Hand Scale Analyzer (`4.1`).
> Kandidat scale untuk nanti: A (baseline), B, C, D, E (world 3D), F (sudut);
> kalibrasi dinamis (G) sebagai lapisan akhir. Keputusan menunggu data pengukuran.
>
> **Hasil 4.0:** garis & titik tidak bergetar lagi, tetap responsif; angka pembacaan stabil
> (perubahan 0.00x, jarang 0.01x). Masalah akurasi terhadap jarak belum terpecahkan
> → dikerjakan di 4.1 (Hand Scale Analyzer).
>
> **Hasil pengukuran 4.1 (25 Agu 2026):** kandidat 2D terbaik = A (drift ~7%); E & F gagal
> (pembagian 3D & sudut menambah noise). **Pemenang: jarak 3D mutlak dalam cm dari
> `hand_world_landmarks`** — stabil di 3 jarak kamera (8.1–9.4 cm), separasi besar
> (pinch 2.9 cm vs terbuka 9.2 cm). Keputusan: ganti sinyal pinch ratio → cm
> (detail: `docs/riset_hand_scale.md` §6).
>
> **Validasi jarak (25 Agu 2026):** 3D penuh menyesatkan — z jempol↔telunjuk saat pinch
> membuat jarak membengkak (2 cm asli → 7.3 cm). Pakai **xy-plane** (bidang telapak):
> 2→2.2, 5→4.7, 8→7.7 cm ✅; terbuka penuh 13 cm asli → 9.6 cm (under ~26%, skala model
> rata-rata). Keputusan: kalibrasi per-user (min/max cm) untuk mapping volume.
>
> **Temuan unik (25 Agu 2026):** skala world coordinates **bergantung pose** — saat 5 jari
> terbuka lebar, estimasi menyusut (13 cm asli → ~9 cm); saat hanya jempol+telunjuk terbuka
> (jari lain menutup), pembacaan akurat (13 cm ✅). Konfirmasi: kalibrasi per-user (M/X)
> adalah pendekatan yang tepat — dipertahankan di aplikasi final.

---

# Phase 5 — Milestone 2: Windows Audio (pycaw)

- [✓] Implementasi **WindowsAudio** (`src/utils/windows_audio.py`) — get/set volume & mute
      memakai `pycaw` 20251023 (API: `AudioDevice.EndpointVolume`) — **teruji: volume naik/turun halus**
- [✓] `src/debug/debug_audio.py` — pipeline penuh pinch → volume Windows nyata — **teruji sukses**
- [✓] Integrasi pipeline penuh:
      `HandTracker → pinch cm → PinchGesture → VolumeMapper → RateLimiter → WindowsAudio`
- [~] `src/main.py` — entry point aplikasi final + kalibrasi tersimpan ke `config.json`
      (M/X otomatis simpan, dimuat saat start) — dibuat, menunggu uji
- [✓] Penanganan kondisi: kamera tidak terbuka (pesan error ramah), tangan hilang dari frame
      (volume dipertahankan / rate limiter hold)

> 📝 **Catatan fase:** **SUKSES 🎉** — volume Windows berhasil dikontrol dengan pinch gesture
> (naik/turun halus). Pelajaran: pycaw 20251023 memakai API baru — `AudioDevice` tidak punya
> `Activate`/`volume_percent`; yang benar: `AudioDevice.EndpointVolume` → `IAudioEndpointVolume`
> (`Get/SetMasterVolumeLevelScalar`). Versi develop punya `volume_percent`, tapi rilis ini belum.
> `config.json` (root project) menyimpan kalibrasi M/X; jangan di-commit jika tidak ingin
> menyimpan nilai pribadi — atau tambahkan ke .gitignore.
>
> **STATUS: Tujuan utama project TERCAPAI.** Sisa: main.py uji, gesture lain (fase 6),
> GUI (fase 7), packaging (fase 8) — opsional sesuai kebutuhan.

---

# Phase 6 — Gesture Lainnya (setelah Milestone 1 & 2 stabil)

- [ ] **Fist** (`src/gesture/fist.py` — placeholder kosong) + `src/debug/debug_fist.py`
- [ ] **Rotate** (`src/gesture/rotate.py` — placeholder kosong) + `src/debug/debug_rotate.py`
- [ ] **Swipe** (`src/gesture/swipe.py` — placeholder kosong)
- [ ] `src/utils/debug_ui.py` (utilitas UI debug — masih kosong)
- [ ] Mode / pemilihan gesture aktif agar antar-gesture tidak bentrok

> 📝 **Catatan fase:** File placeholder sudah dibuat di tahap awal. Jangan diisi sebelum pipeline pinch
> benar-benar stabil — prinsip project: fokus, hindari refactoring/abstraksi berlebihan.

---

# Phase 7 — GUI (PySide6)

- [ ] Settings (pilih kamera, threshold, kalibrasi)
- [ ] Camera preview
- [ ] Kalibrasi interaktif min/max ratio
- [ ] Profile / konfigurasi tersimpan

> 📝 **Catatan fase:** Belum dimulai. PySide6 sudah ada di requirements.

---

# Phase 8 — Release

- [ ] Packaging menjadi `.exe` (PyInstaller / Nuitka)
- [ ] Dokumentasi final (README lengkap; rapikan `docs/architecture.md` yang saat ini dump 1,16 MB)
- [ ] Demo video (`assets/demo/`)
- [ ] Release v1.0

> 📝 **Catatan fase:** Belum dimulai. `docs/architecture.md` (12.059 baris dump tree) dan
> `docs/roadmap.md` lama perlu dirapikan/diganti.

---

# Testing

- [✓] Pytest terpasang dan berjalan
- [✓] Test EMA — 10/10 passed → `pytest tests/test_ema_filter.py -v`
- [✓] Test Dead Zone — 8/8 passed → `pytest tests/test_dead_zone.py -v`
- [✓] Test One Euro Filter & LandmarkSmoother — 11/11 passed
- [ ] **Perbaiki `tests/test_geometry.py`** — saat ini rusak: meng-import `normalize` dari
      `src.utils.geometry`, padahal fungsi itu tidak ada (yang ada `map_range` / `normalize_vector`)
- [ ] Unit test untuk Hysteresis, RateLimiter, VolumeMapper (ikut setiap komponen baru dibuat)

---

# Catatan / Masalah Terbuka

1. `docs/roadmap.md` lama masih berisi roadmap versi awal (Phase 0–5). **File ini**
   (`roadmap.md` di root) adalah versi terbaru.
2. `docs/architecture.md` = 12.059 baris dump `tree /F /A` (1,16 MB) — tidak praktis, perlu diganti ringkasan.
3. `src/landmark_reader.py` meng-import `from utils.drawing import ...` tanpa prefix `src.`
   — akan error jika dijalankan via `python -m src.landmark_reader`.
4. `MIN_PINCH_RATIO` / `MAX_PINCH_RATIO` (0.20/1.20) belum dipakai — `VolumeMapper` masih
   memakai nilai hardcoded 0.35/0.85.
5. File placeholder masih kosong (0 byte): `debug_audio.py`, `debug_fist.py`, `debug_rotate.py`,
   `fist.py`, `rotate.py`, `swipe.py`, `debug_ui.py`, `windows_audio.py`, `math_utils.py`,
   `app_selector.py`, `volume_control.py`, `docs/changelog.md`.
6. `debug_pinch.py` masih punya import `map_range` tidak terpakai + `print` raw/stable tiap frame
   (sengaja untuk debugging, bisa dirapikan nanti).

---

# Cara Menjalankan

```powershell
# Debug pinch (aktif sekarang)
python -m src.debug.debug_pinch

# Test
pytest tests/test_ema_filter.py -v
pytest tests/test_dead_zone.py -v
pytest tests/test_one_euro_filter.py tests/test_landmark_smoother.py -v
```

---

# 🎯 Target Akhir

> **Mengontrol volume Windows dengan pinch gesture melalui webcam.**
>
> ```text
> Webcam → MediaPipe Hand Landmarker → Landmarks → Landmark Smoothing → pinch cm →
> Filter (EMA/Hysteresis) → RateLimiter → VolumeMapper → pycaw → Volume Windows
> ```
