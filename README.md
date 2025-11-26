# ✨ Cipta Mulya | Image Processing App

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?style=for-the-badge&logo=opencv)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blueviolet?style=for-the-badge)

Aplikasi pemrosesan citra digital berbasis GUI modern yang dikembangkan menggunakan Python. Aplikasi ini menyediakan berbagai fitur manipulasi citra mulai dari operasi dasar, deteksi tepi, filtering domain frekuensi, hingga steganografi dan watermarking.

![App Screenshot](assets/screenshot.png)


## 📋 Fitur Utama

Aplikasi ini mencakup berbagai teknik Image Processing (Pengolahan Citra Digital) yang dikelompokkan dalam menu interaktif:

### 1. Operasi Dasar (Basic Ops)
- **Aritmatika:** Penjumlahan, Pengurangan, Perkalian, Pembagian citra.
- **Boolean:** AND, OR, XOR, NOT.
- **Geometri:** Translasi, Rotasi, Zooming, Flipping, Cropping (dengan koordinat).
- **Konvolusi:** Kernel kustom 3x3 dengan preset (Blur, Sharpen, Edge).

### 2. Deteksi Tepi (Edge Detection)
- **Gradient Orde 1:** Sobel, Prewitt, Robert, Compass (Kirsch).
- **Gradient Orde 2:** Laplacian, Laplacian of Gaussian (LoG), Canny.

### 3. Perbaikan Citra (Enhancement)
- **Kecerahan & Kontras:** Pengaturan slider interaktif (Alpha/Beta).
- **Histogram Equalization:** Pemerataan histogram otomatis.
- **Gamma Correction:** Koreksi pencahayaan non-linear.
- **Sharpening:** Highpass Filter, Highboost Filtering.

### 4. Smoothing & Frequency Domain
- **Spatial Domain:** Lowpass Filtering (Average), Median Filtering.
- **Frequency Domain (Fourier Transform):**
  - Ideal Lowpass/Highpass Filter (ILPF/IHPF).
  - Butterworth Lowpass/Highpass Filter (BLPF/BHPF).

### 5. Segmentasi & Warna
- **Konversi Warna:** Grayscale, HSV, YUV, RGB, CMY, YIQ, Binary.
- **Pseudo Coloring:** Pemetaan warna JET.
- **Kontur Citra:** Deteksi kontur dengan pemilihan warna Hex kustom.

### 6. Fitur Tambahan (Advanced)
- **Steganografi (LSB):** Menyembunyikan pesan teks rahasia ke dalam gambar dan membacanya kembali.
- **Watermarking:** Menambahkan watermark (logo/gambar) dengan dukungan transparansi.
- **Kompresi:** Simulasi kompresi Lossy (JPEG) dan info Lossless (PNG).
- **Noise Generator:** Menambahkan Gaussian, Rayleigh, Erlang, Exponential, Uniform, Salt & Pepper noise.

## 🛠️ Teknologi yang Digunakan

* **Python 3.x**
* **CustomTkinter** (UI Modern)
* **OpenCV (cv2)** (Pemrosesan Citra)
* **NumPy** (Operasi Matriks)
* **Pillow (PIL)** (Manipulasi Gambar untuk GUI)

## 🚀 Cara Instalasi & Menjalankan

1.  **Clone Repository ini:**
    ```bash
    git clone [https://github.com/username-kamu/nama-repo-kamu.git](https://github.com/username-kamu/nama-repo-kamu.git)
    cd nama-repo-kamu
    ```

2.  **Install Library yang Dibutuhkan:**
    Pastikan kamu sudah menginstall Python, lalu jalankan perintah berikut di terminal:
    ```bash
    pip install customtkinter opencv-python numpy pillow
    ```

3.  **Jalankan Aplikasi:**
    ```bash
    python Project_ImageProccesing_Kelompok2.py
    ```

## 👥 Tim Pengembang (Kelompok 2)

Proyek ini dikembangkan oleh tim mahasiswa:

* **Andre Alputra**
* **Ariasyah Ramadhan** - [GitHub](https://github.com/ariasyahramadhan)
* **Muhammad Ihsanul Dzaki**

## 📺 Tutorial & Demo

Untuk melihat cara penggunaan dan demo aplikasi, silakan kunjungi:
* [Channel YouTube Ariasyah Ramadhan](https://www.youtube.com/@ariansyahramadhan5145)

## 📄 Lisensi

Proyek ini dibuat untuk tujuan pendidikan dan pembelajaran mata kuliah Pengolahan Citra Digital.

---
*Dibuat dengan ❤️ menggunakan Python.*
