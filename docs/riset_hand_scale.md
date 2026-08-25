# Riset: Metode Normalisasi Hand Scale untuk Pinch Ratio

> Dokumen pendukung **Phase 4 — Stabilisasi** (lihat `roadmap.md` di root).
> Membandingkan metode yang sedang dipakai vs kandidat metode terbaik, **di atas kertas**,
> sebelum diuji langsung lewat `debug_hand_scale.py`.

---

## 1. Metode yang sedang dipakai (Scale A)

Di `src/utils/gesture_utils.py`:

```python
# hand_scale()   = jarak 2D Index MCP (5) ↔ Pinky MCP (17)   → "lebar telapak"
# pinch_ratio()  = jarak 2D Thumb Tip (4) ↔ Index Tip (8) / hand_scale
```

- Koordinat yang dipakai: **image coordinates** (x, y ternormalisasi 0–1 terhadap ukuran gambar).
- Ide dasarnya benar: membagi dengan ukuran tangan membuat rasio **scale-invariant**
  (tidak bergantung jarak kamera) — dalam kondisi ideal.

## 2. Kenapa masih bergeser terhadap jarak kamera?

Kamera bekerja dengan **proyeksi perspektif**, bukan ortografis:

```text
ukuran objek di gambar ≈ (ukuran fisik × focal length) / jarak ke kamera
```

Artinya dua segmen yang berada pada **kedalaman berbeda** diskalakan secara berbeda:

1. **Ujung jari berada di depan telapak** — saat tangan menghadap kamera, Thumb Tip & Index Tip
   lebih dekat ke kamera daripada MCP-MCP di telapak. Saat tangan dekat kamera, efek perspektif
   membesar; saat jauh, mengecil → rasio bergeser walau pose sama.
2. **Pose/rotasi tangan** berubah — orang cenderung memiringkan tangan saat menjulurkan lengan
   (tangan jauh dari badan), mengubah jarak proyeksi antar landmark.
3. **Noise MediaPipe** — saat tangan jauh, tangan hanya beberapa puluh piksel; error landmark
   relatif membesar.

> Kesimpulan: masalahnya **geometris**, bukan sekadar noise — makanya diputuskan tidak ditambal
> pakai filter dulu, melainkan cari reference scale yang lebih stabil.

## 3. Kandidat metode

### Kandidat berbasis 2D (image coordinates)

| Kode | Metode | Kelebihan | Kekurangan |
|---|---|---|---|
| **A** | Index MCP (5) ↔ Pinky MCP (17) — **dipakai sekarang** | Sederhana, sudah jalan, MCP tidak ikut menekuk | Kena distorsi perspektif (jari di depan telapak); baseline |
| **B** | Wrist (0) ↔ Middle MCP (9) | Wrist = landmark paling stabil & paling sedikit noise; MCP tengah = pusat telapak | Masih 2D/perspektif; segmen pendek → nilai rasio besar |
| **C** | Wrist (0) ↔ Middle Tip (12) | Segmen panjang → rasio kecil | **Tip ikut menekuk saat pinch** → skala ikut berubah → diduga paling lemah |
| **D** | Rata-rata beberapa segmen telapak (A + B + Index MCP↔Ring MCP, dst.) | Merata-ratakan noise per segmen | Masih 2D/perspektif; sedikit lebih berat |

### Kandidat berbasis 3D / geometri (paling menjanjikan secara teori)

| Kode | Metode | Kelebihan | Kekurangan |
|---|---|---|---|
| **E** | **World coordinates** (`hand_world_landmarks`): jarak 3D Thumb↔Index / jarak 3D telapak | MediaPipe sudah mengeluarkan koordinat 3D (meter, origin pusat tangan) — **koreksi perspektif otomatis**; bisa juga pakai ambang mutlak (mis. pinch = jarak 3D < 3 cm) | Bergantung akurasi estimasi 3D model; perlu dicek konsistensinya |
| **F** | **Sudut bukaan** (angle antara vektor ibu jari & telunjuk) | Invariant terhadap skala, rotasi, dan jarak (sifat sudut) | Mapping sudut → volume butuh penyesuaian; nilai jenuh saat terbuka lebar |

### Lapisan praktis / catatan lain

| Kode | Metode | Kelebihan | Kekurangan |
|---|---|---|---|
| **G** | Kalibrasi dinamis min/max (running min-max ratio + hysteresis) | Langsung menyelesaikan gejala tanpa peduli penyebab; adaptif terhadap jarak/posisi | Bukan perbaikan geometri; butuh logika adaptif agar tidak salah kalibrasi |
| **H** | ML classifier (MediaPipe GestureRecognizer, gesture "Pinch") | Akurat untuk deteksi on/off | **Diskret — tidak memberi nilai kontinu** → tidak cocok untuk volume kontinu; hanya catatan |

## 4. Analisis & rekomendasi awal (di atas kertas)

1. A/B/C/D semuanya 2D → **sama-sama kena distorsi perspektif**. B & D lebih baik dari A
   (wrist stabil / rata-rata mengurangi noise); C secara teori paling lemah (tip menekuk).
2. **E (world coordinates) adalah kandidat terkuat** — menghilangkan akar masalah perspektif
   karena jarak dihitung di ruang 3D yang sudah dinormalisasi MediaPipe. Bonus: memungkinkan
   ambang mutlak dalam cm.
3. **F (sudut)** paling robust secara teori (bebas skala & rotasi), cocok sebagai pembanding.
4. **G (kalibrasi dinamis)** bukan pengganti, melainkan **jaring pengaman akhir** — tetap
   direkomendasikan dipasang setelah scale terbaik dipilih.
5. Urutan perkiraan: **E > F > D > B > A > C** — tapi ini baru teori;
   keputusan final menunggu data pengukuran dari `debug_hand_scale.py`.

## 5. Rencana pengukuran (untuk debug_hand_scale.py)

Setiap kandidat dihitung real-time dan diukur:

1. **Stabilitas** — std dev / CV (coefficient of variation) saat tangan diam:
   dekat, sedang, jauh. Makin kecil makin baik.
2. **Invariansi jarak** — perubahan nilai rata-rata saat pindah dekat ↔ jauh dengan pose sama.
   Idealnya ~0 untuk scale yang baik.
3. **Separasi** — selisih nilai "pinch penuh" vs "tangan terbuka". Makin besar makin baik.
4. **SNR** = Separasi ÷ noise → skor gabungan untuk memilih pemenang.

Skenario pengujian: ① tangan dekat, ② sedang, ③ jauh, ④ pinch, ⑤ terbuka.

## 6. Hasil Pengukuran (debug_hand_scale.py, 25 Agu 2026)

Urutan pengukuran: ① jauh ② sedang ③ dekat ④ pinch penuh ⑤ terbuka.

| Kandidat | jauh→dekat (drift) | std saat diam | pinch vs terbuka | Penilaian |
|---|---|---|---|---|
| A (IdxMCP-PnkMCP) | 2.32→2.49 (~7%) | ±0.008–0.029 | 0.37 vs 1.41 | ✅ 2D terbaik, tapi range mapping meleset (nilai 0.37–2.5 vs mapper 0.35–0.85) |
| B (Wrist-MidMCP) | 1.34→1.62 (~19%) | ±0.007–0.017 | 0.19 vs 1.51 | ✘ drift besar |
| C (Wrist-MidTip) | 0.66→0.74 (~11%) | ±0.003–0.007 | 0.09 vs 0.71 | ◐ lumayan, tapi tip ikut menekuk saat pinch |
| D (Palm-avg x4) | 2.24→2.53 (~13%) | ±0.009–0.026 | 0.34 vs 1.70 | ✘ rata-rata tidak membantu |
| E (3D ratio) | 1.19→1.45 (~20%) | ±0.011–0.019 | 0.50 vs 1.48 | ✘ membagi dengan palm width 3D justru menambah noise |
| F (Angle) | 20°→31° (~40%) | ±0.6–1.0° | 40° vs 32° (terbalik) | ✘ gagal — sudut membesar saat pinch, tidak monotonic |
| **G: jarak 3D mutlak (cm)** | 9.4 / 8.1 / 9.3 cm | — | **2.9 vs 9.2 cm** | ✅✅ **JUARA** |

### Kesimpulan

- **Gunakan jarak 3D mutlak (cm) dari `hand_world_landmarks`** sebagai sinyal pinch:
  thumb tip ↔ index tip dalam cm. Stabil di 3 jarak kamera (8.1–9.4 cm), separasi besar
  (2.9 cm pinch vs 9.2 cm terbuka), unit intuitif.
- Ambang: pinch ≈ < 4 cm; mapping volume: ~3 cm → 0%, ~9 cm → 100%
  (arah sesuai preferensi: pinch → volume rendah).
- **Tidak perlu membagi dengan reference scale apa pun** — E membuktikan pembagian
  menambah noise. Skala A (2D) hanya terbaik di antara sesama ratio.
- Tambahan nanti: kalibrasi per-user (min/max cm) sebagai lapisan akhir (rencana G).

## 7. Validasi jarak dengan penggaris (debug_distance.py, 25 Agu 2026)

### Temuan penting: pakai xy-plane, bukan 3D penuh

World coordinates MediaPipe: **xy = bidang telapak, z = tegak lurus telapak**.
Jarak 3D penuh (√(dx²+dy²+dz²)) ikut menghitung perbedaan kedalaman jempol↔telunjuk
saat pinch → hasil membengkak (real 2 cm terbaca 7.3 cm).

**Solusi: jarak di bidang telapak (xy saja).** Hasil validasi:

| Posisi (penggaris) | 3D penuh | xy-plane |
|---|---|---|
| Pinch 2 cm | 7.3 cm ❌ | **2.2 cm** ✅ |
| Pinch 5 cm | 10.4 cm ❌ | **4.7 cm** ✅ |
| Pinch 8 cm | 11.7 cm ❌ | **7.7 cm** ✅ |
| Terbuka penuh (~13 cm asli) | 8.7 cm | 9.6 cm (under ~26%) |

- xy-plane akurat untuk jarak kecil (2–8 cm, error ≤ 0.3 cm) — ini yang penting
  untuk kontrol volume.
- Ujung atas di-under-estimasi (13 cm asli → 9.6 cm) karena skala model tangan rata-rata.
- **Implikasi: gunakan kalibrasi per-user (pinch penuh & terbuka penuh) untuk mapping
  volume** — error skala & ukuran tangan terserap otomatis.

### Temuan unik: skala bergantung pose

Saat hanya jempol + telunjuk yang terbuka (jari tengah/manis/kelingking menutup),
pembacaan jarak ujung jempol↔telunjuk **akurat** (13 cm sesuai penggaris).
Saat 5 jari terbuka lebar, pembacaan menyusut (~9 cm untuk 13 cm asli).

Kesimpulan: estimasi skala MediaPipe (model tangan rata-rata) **tidak konstan antar pose**
— error bukan sekadar faktor kali. Inilah alasan utama kenapa pendekatan ratio/skala statis
gagal dan **kalibrasi per-user (min/max) adalah solusi yang tepat**.

## 8. Sumber

- Dokumentasi MediaPipe Hand Landmarker (output: image coordinates + **world coordinates** +
  handedness; model bundle palm detection + landmark):
  https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker
- Prinsip proyeksi perspektif & invariant geometri (pengetahuan umum computer vision).
