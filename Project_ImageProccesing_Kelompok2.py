import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser # <-- [BARU] Impor colorchooser
from PIL import Image
import cv2
import numpy as np
import webbrowser
from collections import deque
import re # <-- [BARU] Impor regular expression untuk validasi hex

# Atur tema default (tetap)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ImageProcessingApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ========================= KONFIGURASI PALET & FONT ========================= #
        # Definisikan palet warna dan font di satu tempat untuk konsistensi
        
        # Palet Warna
        self.COLOR_BG_DARK_1 = "#242424"    # Latar belakang utama (lebih gelap)
        self.COLOR_BG_DARK_2 = "#2B2B2B"    # Latar belakang panel (sedikit lebih terang)
        self.COLOR_BG_DARK_3 = "#343434"    # Latar belakang widget (misal: slider, wrapper gambar)
        
        self.COLOR_ACCENT_BLUE = "#3B82F6"   # Aksen utama (dari kode Anda)
        self.COLOR_ACCENT_GREEN = "#10B981"  # Aksen sukses (dari kode Anda)
        self.COLOR_ACCENT_RED = "#EF4444"    # Aksen bahaya (dari kode Anda)
        self.COLOR_ACCENT_PURPLE = "#A78BFA" # Aksen dinamis (dari kode Anda)
        self.COLOR_ACCENT_YELLOW = "#FBBF24" # Aksen judul (dari kode Anda)
        
        self.COLOR_TEXT_LIGHT = "#E0E0E0"  # Teks utama
        self.COLOR_TEXT_MUTED = "#9E9E9E"  # Teks placeholder/muted
        
        # Font (Gunakan 'Segoe UI' untuk tampilan Windows modern, 'Roboto' atau 'Arial' sebagai fallback)
        try:
            # Coba gunakan Segoe UI jika tersedia
            ctk.CTkFont(family="Segoe UI", size=14)
            self.FONT_FAMILY = "Segoe UI"
        except:
            # Fallback jika Segoe UI tidak ada
            self.FONT_FAMILY = "Arial" 
            
        self.FONT_TITLE = ctk.CTkFont(family=self.FONT_FAMILY, size=26, weight="bold")
        self.FONT_HEADER = ctk.CTkFont(family=self.FONT_FAMILY, size=24, weight="bold")
        self.FONT_SUBHEADER = ctk.CTkFont(family=self.FONT_FAMILY, size=18, weight="bold")
        self.FONT_DYNAMIC_TITLE = ctk.CTkFont(family=self.FONT_FAMILY, size=16, weight="bold")
        self.FONT_BUTTON = ctk.CTkFont(family=self.FONT_FAMILY, size=14, weight="bold")
        self.FONT_LABEL_BOLD = ctk.CTkFont(family=self.FONT_FAMILY, size=14, weight="bold")
        self.FONT_LABEL = ctk.CTkFont(family=self.FONT_FAMILY, size=14)
        self.FONT_SLIDER_VAL = ctk.CTkFont(family=self.FONT_FAMILY, size=13, weight="bold")

        # ========================= KONFIGURASI WINDOW UTAMA ========================= #
        self.title("✨ Cipta Mulya | Image Processor")
        self.geometry("1600x900") # Sedikit lebih besar
        self.minsize(1300, 750) # Minimal size sedikit disesuaikan
        self.configure(fg_color=self.COLOR_BG_DARK_1) # Atur BG utama

        # Inisialisasi variabel (TETAP SAMA)
        self.original_image = None
        self.processed_image = None
        self.temp_image_for_preview = None 
        self.filename = ""
        self.IMAGE_WIDTH = 600
        self.IMAGE_HEIGHT = 450
        
        self.history = deque(maxlen=20)
        self.redo_stack = deque(maxlen=20)

        # Inisialisasi variabel untuk referensi label nilai slider (TETAP SAMA)
        self.brightness_value_label = None
        self.contrast_value_label = None
        self.tx_value_label = None
        self.ty_value_label = None
        self.fx_value_label = None
        self.fy_value_label = None
        self.k_value_label = None
        self.gamma_value_label = None
        self.rotation_value_label = None
        self.threshold_value_label = None
        self.ilpf_d0_value_label = None
        self.ihpf_d0_value_label = None
        self.blpf_d0_value_label = None
        self.blpf_n_value_label = None
        self.bhpf_d0_value_label = None
        self.bhpf_n_value_label = None

        # [MODIFIKASI] Variabel untuk warna kontur
        self.contour_color_entry = None # Akan menjadi CTkEntry
        self.contour_color_preview = None # Akan menjadi CTkFrame untuk pratinjau
        self.hex_color_pattern = re.compile(r'^#[0-9a-fA-F]{6}$') # Pola validasi hex

        self.create_menubar()

        # ========================= LAYOUT UTAMA (MODERN) ========================= #
        # Beri panel kontrol sedikit lebih banyak ruang untuk font baru
        self.grid_columnconfigure(0, weight=0, minsize=380, pad=0) 
        self.grid_columnconfigure(1, weight=4, pad=0) 
        self.grid_rowconfigure(0, weight=1, pad=0)

        # ========================= FRAME KONTROL (KIRI) ========================= #
        # Gunakan palet warna baru
        control_frame = ctk.CTkFrame(self, width=380, corner_radius=12, fg_color=self.COLOR_BG_DARK_2)
        control_frame.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        control_frame.grid_propagate(False)

        # Judul Kontrol (Gunakan FONT_TITLE)
        app_title = ctk.CTkLabel(control_frame, text="⚙️ Panel Kontrol", font=self.FONT_TITLE)
        app_title.pack(pady=(25, 5))
        
        # Divider visual
        ctk.CTkFrame(control_frame, height=2, fg_color=self.COLOR_BG_DARK_3).pack(fill="x", padx=20, pady=(5, 15))
        
        # --- STATIC CONTROLS (I/O & History) ---
        static_controls_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        static_controls_frame.pack(pady=5, fill="x", padx=20) # Beri padding konsisten
        static_controls_frame.grid_columnconfigure((0,1), weight=1)
        
        # Tombol I/O (Gunakan FONT_BUTTON dan warna palet)
        ctk.CTkButton(static_controls_frame, text="📂 Buka Gambar", command=self.browse_files, fg_color=self.COLOR_ACCENT_BLUE, hover_color="#2563EB", font=self.FONT_BUTTON).grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")
        ctk.CTkButton(static_controls_frame, text="💾 Simpan Hasil", command=self.save_image, fg_color=self.COLOR_ACCENT_GREEN, hover_color="#059669", font=self.FONT_BUTTON).grid(row=0, column=1, padx=(5, 0), pady=5, sticky="ew")
        
        # Tombol History
        history_frame = ctk.CTkFrame(static_controls_frame, fg_color="transparent")
        history_frame.grid(row=1, column=0, columnspan=2, pady=(10, 5), sticky="ew")
        history_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.undo_button = ctk.CTkButton(history_frame, text="↩️ Undo", command=self.undo_action, state="disabled", fg_color=self.COLOR_BG_DARK_3, hover_color="#4B5563", font=self.FONT_BUTTON)
        self.undo_button.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")
        self.redo_button = ctk.CTkButton(history_frame, text="↪️ Redo", command=self.redo_action, state="disabled", fg_color=self.COLOR_BG_DARK_3, hover_color="#4B5563", font=self.FONT_BUTTON)
        self.redo_button.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="ew")
        
        # Tombol Reset (Gunakan FONT_BUTTON dan warna palet)
        self.reset_button = ctk.CTkButton(static_controls_frame, text="🔄 Reset Semua", command=self.reset_image, fg_color=self.COLOR_ACCENT_RED, hover_color="#DC2626", state="disabled", font=self.FONT_BUTTON)
        self.reset_button.grid(row=2, column=0, columnspan=2, padx=0, pady=(5, 10), sticky="ew")
        
        # --- DYNAMIC CONTROLS (SCROLLABLE FRAME) ---
        # Buat frame ini sedikit 'recessed' (lebih gelap)
        self.dynamic_controls_frame = ctk.CTkScrollableFrame(control_frame, label_text="Panel Operasi Dinamis", corner_radius=10, label_font=self.FONT_SUBHEADER, label_fg_color="#4B5563", fg_color=self.COLOR_BG_DARK_1)
        self.dynamic_controls_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Tombol Keluar (Gunakan FONT_BUTTON)
        exit_button = ctk.CTkButton(control_frame, text="❌ Keluar Aplikasi", command=self.quit, fg_color="#B91C1C", hover_color="#991B1B", font=self.FONT_BUTTON)
        exit_button.pack(side="bottom", fill="x", padx=20, pady=20)

        # ========================= FRAME GAMBAR (KANAN) ========================= #
        image_display_frame = ctk.CTkFrame(self, fg_color="transparent")
        image_display_frame.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        image_display_frame.grid_columnconfigure((0, 1), weight=1)
        image_display_frame.grid_rowconfigure(1, weight=1)

        # Label judul gambar (Gunakan FONT_HEADER dan warna palet)
        ctk.CTkLabel(image_display_frame, text="🌄 Gambar Original", font=self.FONT_HEADER, text_color=self.COLOR_ACCENT_YELLOW).grid(row=0, column=0, pady=(0, 15))
        ctk.CTkLabel(image_display_frame, text="💻 Gambar Hasil Proses", font=self.FONT_HEADER, text_color=self.COLOR_ACCENT_BLUE).grid(row=0, column=1, pady=(0, 15))

        # Wrapper Gambar Original (Gunakan palet warna)
        original_wrapper = ctk.CTkFrame(image_display_frame, fg_color=self.COLOR_BG_DARK_3, corner_radius=10, border_width=2, border_color=self.COLOR_BG_DARK_3)
        original_wrapper.grid(row=1, column=0, padx=(0, 10), pady=10, sticky="nsew")
        original_wrapper.grid_rowconfigure(0, weight=1)
        original_wrapper.grid_columnconfigure(0, weight=1)

        self.original_image_label = ctk.CTkLabel(original_wrapper, text="Buka gambar untuk memulai...", font=self.FONT_LABEL, text_color=self.COLOR_TEXT_MUTED)
        self.original_image_label.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Wrapper Gambar Hasil Proses (Gunakan palet warna)
        processed_wrapper = ctk.CTkFrame(image_display_frame, fg_color=self.COLOR_BG_DARK_3, corner_radius=10, border_width=2, border_color=self.COLOR_BG_DARK_3)
        processed_wrapper.grid(row=1, column=1, padx=(10, 0), pady=10, sticky="nsew")
        processed_wrapper.grid_rowconfigure(0, weight=1)
        processed_wrapper.grid_columnconfigure(0, weight=1)

        self.processed_image_label = ctk.CTkLabel(processed_wrapper, text="Hasil proses akan muncul di sini", font=self.FONT_LABEL, text_color=self.COLOR_TEXT_MUTED)
        self.processed_image_label.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    
    # ========================= FUNGSI MENU BAR (GAYA DISESUAIKAN) ========================= #
    def create_menubar(self):
        # Definisikan gaya untuk menu agar konsisten dengan tema
        menu_bg = self.COLOR_BG_DARK_2       # Latar belakang gelap, konsisten dengan control_frame
        menu_fg = self.COLOR_TEXT_LIGHT      # Teks terang
        menu_active_bg = self.COLOR_ACCENT_BLUE  # Warna biru konsisten saat hover
        menu_active_fg = "white"
        menu_font = (self.FONT_FAMILY, 11)   # Font modern dan bersih
        
        # Style konsisten untuk submenu
        submenu_style = {
            "bg": menu_bg,
            "fg": menu_fg,
            "activebackground": menu_active_bg,
            "activeforeground": menu_active_fg,
            "font": menu_font,
            "borderwidth": 0,
            "relief": "flat",
            "tearoff": 0  # Menghilangkan fitur kuno 'tearoff'
        }

        # Menubar utama
        menubar = tk.Menu(self, **submenu_style)
        self.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, **submenu_style)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open...", command=self.browse_files)
        file_menu.add_command(label="Save...", command=self.save_image)
        file_menu.add_command(label="Save As...", command=self.save_image)
        file_menu.add_separator(background=menu_bg)
        file_menu.add_command(label="Exit", command=self.quit)
        
        # Edge Detection Menu
        edge_menu = tk.Menu(menubar, **submenu_style)
        menubar.add_cascade(label="Edge Detection", menu=edge_menu)
        first_grad_menu = tk.Menu(edge_menu, **submenu_style)
        edge_menu.add_cascade(label="1st Differential Gradient", menu=first_grad_menu)
        first_grad_menu.add_command(label="Sobel", command=self.apply_sobel)
        first_grad_menu.add_command(label="Prewitt", command=self.apply_prewitt)
        first_grad_menu.add_command(label="Robert", command=self.apply_robert)
        edge_menu.add_command(label="Compass (Kirsch)", command=self.apply_kirsch_compass)
        second_grad_menu = tk.Menu(edge_menu, **submenu_style)
        edge_menu.add_cascade(label="2nd Differential Gradient", menu=second_grad_menu)
        second_grad_menu.add_command(label="Laplacian", command=self.apply_laplacian)
        second_grad_menu.add_command(label="Laplacian of Gaussian (LoG)", command=self.apply_log)
        second_grad_menu.add_command(label="Canny", command=self.apply_canny)
        
        # Basic Ops Menu
        basic_ops_menu = tk.Menu(menubar, **submenu_style)
        menubar.add_cascade(label="Basic Ops", menu=basic_ops_menu)
        basic_ops_menu.add_command(label="Negative", command=self.apply_negative)
        
        arithmetics_menu = tk.Menu(basic_ops_menu, **submenu_style)
        basic_ops_menu.add_cascade(label="Arithmetics", menu=arithmetics_menu)
        arithmetics_menu.add_command(label="Add (+)", command=self.apply_add)
        arithmetics_menu.add_command(label="Subtract (-)", command=self.apply_subtract)
        arithmetics_menu.add_command(label="Multiply (*)", command=self.apply_multiply)
        arithmetics_menu.add_command(label="Divide (/)", command=self.apply_divide)
        
        boolean_menu = tk.Menu(basic_ops_menu, **submenu_style)
        basic_ops_menu.add_cascade(label="Boolean", menu=boolean_menu)
        boolean_menu.add_command(label="NOT", command=self.apply_not)
        boolean_menu.add_command(label="AND", command=self.apply_and)
        boolean_menu.add_command(label="OR", command=self.apply_or)
        boolean_menu.add_command(label="XOR", command=self.apply_xor)
        
        geometrics_menu = tk.Menu(basic_ops_menu, **submenu_style)
        basic_ops_menu.add_cascade(label="Geometrics", menu=geometrics_menu)
        geometrics_menu.add_command(label="Translation", command=self.setup_translation_controls)
        geometrics_menu.add_command(label="Rotation", command=self.setup_rotation_controls)
        geometrics_menu.add_command(label="Zooming", command=self.setup_zoom_controls)
        geometrics_menu.add_command(label="Flipping", command=self.apply_flipping)
        geometrics_menu.add_command(label="Cropping", command=self.setup_cropping_controls)
        
        basic_ops_menu.add_command(label="Thresholding", command=self.setup_thresholding_controls)
        basic_ops_menu.add_command(label="Convolution", command=self.setup_convolution_controls)
        
        colouring_menu = tk.Menu(basic_ops_menu, **submenu_style)
        basic_ops_menu.add_cascade(label="Colouring", menu=colouring_menu)
        colouring_menu.add_command(label="Grayscale", command=self.apply_grayscale)
        colouring_menu.add_command(label="HSV", command=lambda: self.apply_colorspace(cv2.COLOR_BGR2HSV))
        colouring_menu.add_command(label="YUV", command=lambda: self.apply_colorspace(cv2.COLOR_BGR2YUV))
        colouring_menu.add_command(label="Binary", command=self.apply_binary)
        colouring_menu.add_command(label="RGB", command=self.apply_rgb)
        colouring_menu.add_command(label="CMY", command=self.apply_cmy)
        colouring_menu.add_command(label="YIQ", command=self.apply_yiq)
        colouring_menu.add_command(label="Pseudo Coloring (Jet)", command=self.apply_pseudo)
        
        basic_ops_menu.add_command(label="Fourier Transform", command=self.apply_fourier_transform)
        
        # Enhancement Menu
        enhancement_menu = tk.Menu(menubar, **submenu_style)
        menubar.add_cascade(label="Enhancement", menu=enhancement_menu)
        enhancement_menu.add_command(label="Brightness & Contrast", command=self.setup_brightness_contrast_controls)
        enhancement_menu.add_command(label="Histogram Equalization", command=self.apply_hist_equalization)
        
        smoothing_menu = tk.Menu(enhancement_menu, **submenu_style)
        enhancement_menu.add_cascade(label="Smoothing", menu=smoothing_menu)
        spatial_menu = tk.Menu(smoothing_menu, **submenu_style)
        smoothing_menu.add_cascade(label="Spatial Domain", menu=spatial_menu)
        spatial_menu.add_command(label="Lowpass Filtering (Average)", command=self.apply_blur)
        spatial_menu.add_command(label="Median Filtering", command=self.apply_median_filter)
        frequency_menu = tk.Menu(smoothing_menu, **submenu_style)
        smoothing_menu.add_cascade(label="Frequency Domain", menu=frequency_menu)
        frequency_menu.add_command(label="ILPF", command=self.setup_ilpf_controls)
        frequency_menu.add_command(label="BLPF", command=self.setup_blpf_controls)

        enhancement_menu.add_command(label="Correction", command=self.setup_gamma_controls) 
        
        sharpening_menu = tk.Menu(enhancement_menu, **submenu_style)
        enhancement_menu.add_cascade(label="Sharpening", menu=sharpening_menu)
        spatial_sharp_menu = tk.Menu(sharpening_menu, **submenu_style)
        sharpening_menu.add_cascade(label="Spatial Domain", menu=spatial_sharp_menu)
        spatial_sharp_menu.add_command(label="Highpass Filter", command=self.apply_sharpen)
        spatial_sharp_menu.add_command(label="Highboost Filtering", command=self.setup_highboost_controls)
        frequency_sharp_menu = tk.Menu(sharpening_menu, **submenu_style)
        sharpening_menu.add_cascade(label="Frequency Domain", menu=frequency_sharp_menu)
        frequency_sharp_menu.add_command(label="IHPF", command=self.setup_ihpf_controls)
        frequency_sharp_menu.add_command(label="BHPF", command=self.setup_bhpf_controls)
        
        # Noise Menu
        noise_menu = tk.Menu(menubar, **submenu_style)
        menubar.add_cascade(label="Noise", menu=noise_menu)
        noise_menu.add_command(label="Add Gaussian Noise", command=self.add_gaussian_noise)
        noise_menu.add_command(label="Add Rayleigh Noise", command=self.add_rayleigh_noise)
        noise_menu.add_command(label="Add Erlang (Gamma) Noise", command=self.add_erlang_noise)
        noise_menu.add_command(label="Add Exponential Noise", command=self.add_exponential_noise)
        noise_menu.add_command(label="Add Uniform Noise", command=self.add_uniform_noise)
        noise_menu.add_command(label="Add Impulse Noise (Salt & Pepper)", command=self.add_impulse_noise)
        
        # ================================ [KODE DIPERBAIKI DI SINI] ================================
        # Segmentation Menu
        segmentation_menu = tk.Menu(menubar, **submenu_style)
        menubar.add_cascade(label="Segmentation", menu=segmentation_menu)
        
        # 1. Citra Biner
        segmentation_menu.add_command(label="Citra Biner", command=self.apply_binary)
        
        # 3. Kontur Citra (Tautkan ke fungsi setup baru)
        segmentation_menu.add_command(label="Kontur Citra", command=self.setup_contour_controls) # <-- SUDAH BENAR
        
        # 4. Kompresi Citra (Submenu baru)
        compress_menu = tk.Menu(segmentation_menu, **submenu_style)
        segmentation_menu.add_cascade(label="Kompresi Citra", menu=compress_menu)
        compress_menu.add_command(label="Lossy (Pratinjau JPEG)", command=self.apply_compression_preview)
        compress_menu.add_command(label="Lossless (Info PNG)", command=self.show_lossless_info)
        
        # 5. Steganografi
        stego_menu = tk.Menu(segmentation_menu, **submenu_style)
        segmentation_menu.add_cascade(label="Steganografi", menu=stego_menu)
        stego_menu.add_command(label="Sembunyikan Pesan (Encode)", command=self.setup_steganography_encode)
        stego_menu.add_command(label="Tampilkan Pesan (Decode)", command=self.apply_steganography_decode)
        
        # 6. Watermark
        segmentation_menu.add_command(label="Watermark (Visible)", command=self.apply_visible_watermark)
        # ===================================== [PERBAIKAN SELESAI] =====================================

        # About Menu
        about_menu = tk.Menu(menubar, **submenu_style)
        menubar.add_cascade(label="About", menu=about_menu)
        
        ABOUT_GITHUB_URL = "https.://github.com/ariasyahramadhan" 
        ABOUT_YOUTUBE_URL = "https://www.youtube.com/@ariansyahramadhan5145" 
        
        about_menu.add_command(label="Info Tim developer", command=self.show_dev_info)
        about_menu.add_separator(background=menu_bg)
        about_menu.add_command(label="Tutorial :")
        about_menu.add_command(label="✓ Link Github", command=lambda: self.open_link(ABOUT_GITHUB_URL))
        about_menu.add_command(label="✓ Link YouTube", command=lambda: self.open_link(ABOUT_YOUTUBE_URL))
    # ========================================================================================================= #

    # ========================= KONTROL DINAMIS (UI MODIFIED) ========================= #
    def clear_dynamic_controls(self):
        for widget in self.dynamic_controls_frame.winfo_children():
            widget.destroy()
        self.temp_image_for_preview = None

    # Helper untuk membuat set slider (desain disesuaikan)
    def _create_slider_set(self, parent, label_text, from_, to, initial_val, format_str, callback):
        # Frame dengan palet warna baru
        frame = ctk.CTkFrame(parent, fg_color=self.COLOR_BG_DARK_3, corner_radius=8)
        frame.pack(fill="x", padx=10, pady=5)
        
        # Label utama (gunakan FONT_LABEL_BOLD)
        label = ctk.CTkLabel(frame, text=label_text, width=120, anchor="w", font=self.FONT_LABEL_BOLD)
        label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Label nilai (gunakan FONT_SLIDER_VAL dan palet warna)
        value_label = ctk.CTkLabel(frame, text=format_str.format(initial_val), width=60, anchor="e", fg_color=self.COLOR_BG_DARK_2, corner_radius=5, font=self.FONT_SLIDER_VAL)
        value_label.grid(row=0, column=2, padx=(5, 10), pady=5, sticky="e")
        
        # Slider
        slider = ctk.CTkSlider(frame, from_=from_, to=to, command=lambda val: callback(val, value_label, format_str))
        slider.set(initial_val)
        slider.grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="ew")
        
        frame.grid_columnconfigure(1, weight=1) 
        return frame, slider

    # --- SETUP KONTROL DENGAN DESAIN BARU ---
    # *FIXED: Memastikan referensi label tersimpan untuk semua kontrol multi-slider*
    def setup_brightness_contrast_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        self.temp_image_for_preview = self.processed_image.copy()
        ctk.CTkLabel(self.dynamic_controls_frame, text="Kontrol Kecerahan & Kontras", font=self.FONT_DYNAMIC_TITLE, text_color=self.COLOR_ACCENT_PURPLE).pack(pady=(10, 5))
        
        bf, self.brightness_slider = self._create_slider_set(self.dynamic_controls_frame, "Kecerahan (Beta)", -100, 100, 0, "{:.0f}", self.preview_brightness_contrast)
        self.brightness_value_label = bf.winfo_children()[2] 
        bf.pack(fill="x", padx=10, pady=5)
        
        cf, self.contrast_slider = self._create_slider_set(self.dynamic_controls_frame, "Kontras (Alpha)", 0, 3, 1, "{:.2f}", self.preview_brightness_contrast)
        self.contrast_value_label = cf.winfo_children()[2] 
        cf.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Terapkan Perubahan", command=self.commit_brightness_contrast, fg_color=self.COLOR_ACCENT_GREEN, hover_color="#047857", font=self.FONT_BUTTON).pack(fill="x", padx=10, pady=15)

    def setup_rotation_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        self.temp_image_for_preview = self.processed_image.copy()
        ctk.CTkLabel(self.dynamic_controls_frame, text="Kontrol Rotasi", font=self.FONT_DYNAMIC_TITLE, text_color=self.COLOR_ACCENT_PURPLE).pack(pady=(10, 5))
        rf, self.rotation_slider = self._create_slider_set(self.dynamic_controls_frame, "Sudut Rotasi", 0, 360, 0, "{:.0f}°", self.preview_rotation)
        self.rotation_value_label = rf.winfo_children()[2]
        rf.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Terapkan Rotasi", command=self.commit_rotation, fg_color=self.COLOR_ACCENT_GREEN, hover_color="#047857", font=self.FONT_BUTTON).pack(fill="x", padx=10, pady=15)

    def setup_thresholding_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        self.temp_image_for_preview = self.processed_image.copy()
        ctk.CTkLabel(self.dynamic_controls_frame, text="Kontrol Thresholding", font=self.FONT_DYNAMIC_TITLE, text_color=self.COLOR_ACCENT_PURPLE).pack(pady=(10, 5))
        tf, self.threshold_slider = self._create_slider_set(self.dynamic_controls_frame, "Nilai Threshold", 0, 255, 127, "{:.0f}", self.preview_thresholding)
        self.threshold_value_label = tf.winfo_children()[2]
        tf.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Terapkan Threshold", command=self.commit_thresholding, fg_color=self.COLOR_ACCENT_GREEN, hover_color="#047857", font=self.FONT_BUTTON).pack(fill="x", padx=10, pady=15)

    def setup_translation_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        self.temp_image_for_preview = self.processed_image.copy()
        ctk.CTkLabel(self.dynamic_controls_frame, text="Kontrol Translasi", font=self.FONT_DYNAMIC_TITLE, text_color=self.COLOR_ACCENT_PURPLE).pack(pady=(10, 5))
        
        tx_f, self.tx_slider = self._create_slider_set(self.dynamic_controls_frame, "Translasi X", -100, 100, 0, "{:.0f}px", self.preview_translation)
        self.tx_value_label = tx_f.winfo_children()[2]
        tx_f.pack(fill="x", padx=10, pady=5)
        
        ty_f, self.ty_slider = self._create_slider_set(self.dynamic_controls_frame, "Translasi Y", -100, 100, 0, "{:.0f}px", self.preview_translation)
        self.ty_value_label = ty_f.winfo_children()[2]
        ty_f.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Terapkan Translasi", command=self.commit_translation, fg_color=self.COLOR_ACCENT_GREEN, hover_color="#047857", font=self.FONT_BUTTON).pack(fill="x", padx=10, pady=15)

    def setup_zoom_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        self.temp_image_for_preview = self.processed_image.copy()
        ctk.CTkLabel(self.dynamic_controls_frame, text="Kontrol Zooming", font=self.FONT_DYNAMIC_TITLE, text_color=self.COLOR_ACCENT_PURPLE).pack(pady=(10, 5))
        
        fx_f, self.fx_slider = self._create_slider_set(self.dynamic_controls_frame, "Faktor Zoom X", 0.1, 3, 1, "{:.2f}x", self.preview_zoom)
        self.fx_value_label = fx_f.winfo_children()[2]
        fx_f.pack(fill="x", padx=10, pady=5)
        
        fy_f, self.fy_slider = self._create_slider_set(self.dynamic_controls_frame, "Faktor Zoom Y", 0.1, 3, 1, "{:.2f}x", self.preview_zoom)
        self.fy_value_label = fy_f.winfo_children()[2]
        fy_f.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Terapkan Zoom", command=self.commit_zoom, fg_color=self.COLOR_ACCENT_GREEN, hover_color="#047857", font=self.FONT_BUTTON).pack(fill="x", padx=10, pady=15)

    def setup_highboost_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        self.temp_image_for_preview = self.processed_image.copy()
        ctk.CTkLabel(self.dynamic_controls_frame, text="Kontrol Highboost", font=self.FONT_DYNAMIC_TITLE, text_color=self.COLOR_ACCENT_PURPLE).pack(pady=(10, 5))
        k_f, self.k_slider = self._create_slider_set(self.dynamic_controls_frame, "K-Factor", 0, 5, 1.2, "{:.2f}", self.preview_highboost)
        self.k_value_label = k_f.winfo_children()[2]
        k_f.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Terapkan Highboost", command=self.commit_highboost, fg_color=self.COLOR_ACCENT_GREEN, hover_color="#047857", font=self.FONT_BUTTON).pack(fill="x", padx=10, pady=15)

    def setup_cropping_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        
        ctk.CTkLabel(self.dynamic_controls_frame, text="✂️ Masukkan Koordinat Cropping", font=self.FONT_DYNAMIC_TITLE, text_color=self.COLOR_ACCENT_PURPLE).pack(pady=(10, 5))
        
        input_frame = ctk.CTkFrame(self.dynamic_controls_frame, fg_color=self.COLOR_BG_DARK_3, corner_radius=8)
        input_frame.pack(fill="x", padx=10, pady=5)
        input_frame.grid_columnconfigure((1), weight=1) # Hanya kolom input yang expand

        H, W = self.processed_image.shape[:2]
        
        # Gunakan FONT_LABEL
        ctk.CTkLabel(input_frame, text="X Kiri (Xmin)", font=self.FONT_LABEL).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.xmin_entry = ctk.CTkEntry(input_frame, width=80, font=self.FONT_LABEL)
        self.xmin_entry.insert(0, "0")
        self.xmin_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(input_frame, text="Y Atas (Ymin)", font=self.FONT_LABEL).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.ymin_entry = ctk.CTkEntry(input_frame, width=80, font=self.FONT_LABEL)
        self.ymin_entry.insert(0, "0")
        self.ymin_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(input_frame, text=f"X Kanan (Xmax) [Max:{W}]", font=self.FONT_LABEL).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.xmax_entry = ctk.CTkEntry(input_frame, width=80, font=self.FONT_LABEL)
        self.xmax_entry.insert(0, str(W))
        self.xmax_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(input_frame, text=f"Y Bawah (Ymax) [Max:{H}]", font=self.FONT_LABEL).grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.ymax_entry = ctk.CTkEntry(input_frame, width=80, font=self.FONT_LABEL)
        self.ymax_entry.insert(0, str(H))
        self.ymax_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Terapkan Cropping", command=self.commit_cropping, fg_color=self.COLOR_ACCENT_GREEN, hover_color="#047857", font=self.FONT_BUTTON).pack(fill="x", padx=10, pady=15)

    def setup_convolution_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        
        ctk.CTkLabel(self.dynamic_controls_frame, text="🎛️ Kernel Konvolusi 3x3", font=self.FONT_DYNAMIC_TITLE, text_color=self.COLOR_ACCENT_PURPLE).pack(pady=(10, 5))
        
        kernel_frame = ctk.CTkFrame(self.dynamic_controls_frame, fg_color=self.COLOR_BG_DARK_3, corner_radius=8)
        kernel_frame.pack(pady=5, padx=10)
        
        self.kernel_entries = []
        default_kernel = [0, 0, 0, 0, 1, 0, 0, 0, 0] 
        
        for i in range(3):
            for j in range(3):
                kernel_frame.grid_columnconfigure(j, weight=1)
                entry = ctk.CTkEntry(kernel_frame, width=50, justify='center', font=self.FONT_LABEL) # Perlebar sedikit
                entry.insert(0, str(default_kernel[i*3 + j]))
                entry.grid(row=i, column=j, padx=4, pady=4) # Beri spasi antar entry
                self.kernel_entries.append(entry)

        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Terapkan Konvolusi", command=self.commit_convolution, fg_color=self.COLOR_ACCENT_GREEN, hover_color="#047857", font=self.FONT_BUTTON).pack(fill="x", padx=10, pady=10)
        
        presets_frame = ctk.CTkFrame(self.dynamic_controls_frame, fg_color="transparent")
        presets_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(presets_frame, text="Presets:", font=self.FONT_LABEL_BOLD).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(presets_frame, text="Blur", command=lambda: self._load_kernel([1/9]*9), width=70, font=self.FONT_LABEL).pack(side="left", padx=2)
        ctk.CTkButton(presets_frame, text="Sharpen", command=lambda: self._load_kernel([0, -1, 0, -1, 5, -1, 0, -1, 0]), width=70, font=self.FONT_LABEL).pack(side="left", padx=2)
        ctk.CTkButton(presets_frame, text="Edge", command=lambda: self._load_kernel([-1, -1, -1, -1, 8, -1, -1, -1, -1]), width=70, font=self.FONT_LABEL).pack(side="left", padx=2)

    def setup_gamma_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        
        ctk.CTkLabel(self.dynamic_controls_frame, text="☀️ Gamma Correction", font=self.FONT_DYNAMIC_TITLE, text_color=self.COLOR_ACCENT_PURPLE).pack(pady=(10, 5))
        
        gf, self.gamma_slider = self._create_slider_set(self.dynamic_controls_frame, "Gamma (γ)", 0.1, 5.0, 1.0, "{:.2f}", self.preview_gamma)
        self.gamma_value_label = gf.winfo_children()[2]
        gf.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Terapkan Gamma", command=self.commit_gamma, fg_color=self.COLOR_ACCENT_GREEN, hover_color="#047857", font=self.FONT_BUTTON).pack(fill="x", padx=10, pady=15)
        
    def setup_ilpf_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        
        ctk.CTkLabel(self.dynamic_controls_frame, text="Ideal Lowpass Filter (ILPF)", font=self.FONT_DYNAMIC_TITLE, text_color=self.COLOR_ACCENT_PURPLE).pack(pady=(10, 5))
        
        H, W = self.processed_image.shape[:2]
        D_max = np.sqrt((H/2)**2 + (W/2)**2)
        
        df, self.ilpf_d0_slider = self._create_slider_set(self.dynamic_controls_frame, "Cutoff (D0)", 1, int(D_max), int(D_max/4), "{:.0f}", self.preview_ilpf)
        self.ilpf_d0_value_label = df.winfo_children()[2]
        df.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Apply ILPF", command=self.commit_ilpf, fg_color=self.COLOR_ACCENT_GREEN, hover_color="#047857", font=self.FONT_BUTTON).pack(fill="x", padx=10, pady=15)

    def setup_blpf_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        
        ctk.CTkLabel(self.dynamic_controls_frame, text="Butterworth Lowpass Filter (BLPF)", font=self.FONT_DYNAMIC_TITLE, text_color=self.COLOR_ACCENT_PURPLE).pack(pady=(10, 5))
        
        H, W = self.processed_image.shape[:2]
        D_max = np.sqrt((H/2)**2 + (W/2)**2)
        
        df, self.blpf_d0_slider = self._create_slider_set(self.dynamic_controls_frame, "Cutoff (D0)", 1, int(D_max), int(D_max/4), "{:.0f}", self.preview_blpf)
        self.blpf_d0_value_label = df.winfo_children()[2]
        df.pack(fill="x", padx=10, pady=5)

        nf, self.blpf_n_slider = self._create_slider_set(self.dynamic_controls_frame, "Order (n)", 1, 10, 2, "{:.0f}", self.preview_blpf)
        self.blpf_n_value_label = nf.winfo_children()[2]
        nf.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Apply BLPF", command=self.commit_blpf, fg_color=self.COLOR_ACCENT_GREEN, hover_color="#047857", font=self.FONT_BUTTON).pack(fill="x", padx=10, pady=15)
        
    def setup_ihpf_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        
        ctk.CTkLabel(self.dynamic_controls_frame, text="Ideal Highpass Filter (IHPF)", font=self.FONT_DYNAMIC_TITLE, text_color=self.COLOR_ACCENT_PURPLE).pack(pady=(10, 5))
        
        H, W = self.processed_image.shape[:2]
        D_max = np.sqrt((H/2)**2 + (W/2)**2)
        
        df, self.ihpf_d0_slider = self._create_slider_set(self.dynamic_controls_frame, "Cutoff (D0)", 1, int(D_max), int(D_max/4), "{:.0f}", self.preview_ihpf)
        self.ihpf_d0_value_label = df.winfo_children()[2]
        df.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Apply IHPF", command=self.commit_ihpf, fg_color=self.COLOR_ACCENT_GREEN, hover_color="#047857", font=self.FONT_BUTTON).pack(fill="x", padx=10, pady=15)
    
    def setup_bhpf_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        
        ctk.CTkLabel(self.dynamic_controls_frame, text="Butterworth Highpass Filter (BHPF)", font=self.FONT_DYNAMIC_TITLE, text_color=self.COLOR_ACCENT_PURPLE).pack(pady=(10, 5))
        
        H, W = self.processed_image.shape[:2]
        D_max = np.sqrt((H/2)**2 + (W/2)**2)
        
        df, self.bhpf_d0_slider = self._create_slider_set(self.dynamic_controls_frame, "Cutoff (D0)", 1, int(D_max), int(D_max/4), "{:.0f}", self.preview_bhpf)
        self.bhpf_d0_value_label = df.winfo_children()[2]
        df.pack(fill="x", padx=10, pady=5)

        nf, self.bhpf_n_slider = self._create_slider_set(self.dynamic_controls_frame, "Order (n)", 1, 10, 2, "{:.0f}", self.preview_bhpf)
        self.bhpf_n_value_label = nf.winfo_children()[2]
        nf.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Apply BHPF", command=self.commit_bhpf, fg_color=self.COLOR_ACCENT_GREEN, hover_color="#047857", font=self.FONT_BUTTON).pack(fill="x", padx=10, pady=15)

    # ================================ [FUNGSI BARU DAN MODIFIKASI] ================================
    
    def _is_valid_hex(self, hex_code):
        """Helper untuk memvalidasi kode hex."""
        if self.hex_color_pattern.match(hex_code):
            return True
        return False

    def _update_color_preview_from_entry(self, event=None):
        """Mengupdate kotak pratinjau saat pengguna mengetik di entry."""
        if not self.contour_color_preview:
            return
        hex_code = self.contour_color_entry.get()
        if self._is_valid_hex(hex_code):
            self.contour_color_preview.configure(fg_color=hex_code, border_color="gray")
        else:
            # Tampilkan warna 'error'
            self.contour_color_preview.configure(fg_color=self.COLOR_BG_DARK_1, border_color=self.COLOR_ACCENT_RED)

    def _ask_contour_color(self):
        """Membuka dialog color chooser."""
        # Ambil warna awal dari entry jika valid, jika tidak, default
        initial_color = self.contour_color_entry.get()
        if not self._is_valid_hex(initial_color):
            initial_color = "#00FF00"
            
        # askcolor mengembalikan tuple ((R,G,B), '#RRGGBB')
        color = colorchooser.askcolor(title="Pilih Warna Kontur", initialcolor=initial_color)
        
        if color and color[1]: # Cek jika pengguna tidak menekan 'Cancel'
            hex_code = color[1]
            self.contour_color_entry.delete(0, tk.END)
            self.contour_color_entry.insert(0, hex_code)
            self._update_color_preview_from_entry() # Update pratinjau
    
    # [FUNGSI DIGANTI] Setup untuk Kontrol Kontur (VERSI BARU DENGAN HEX ENTRY)
    def setup_contour_controls(self):
        if self.processed_image is None: 
            messagebox.showwarning("Peringatan", "Buka gambar terlebih dahulu!")
            return
        self.clear_dynamic_controls()
        
        ctk.CTkLabel(self.dynamic_controls_frame, text="🎨 Kontrol Kontur Citra", font=self.FONT_DYNAMIC_TITLE, text_color=self.COLOR_ACCENT_PURPLE).pack(pady=(10, 5))
        
        # Frame untuk Opsi
        frame = ctk.CTkFrame(self.dynamic_controls_frame, fg_color=self.COLOR_BG_DARK_3, corner_radius=8)
        frame.pack(fill="x", padx=10, pady=5)
        frame.grid_columnconfigure(1, weight=1) # Buat entry box melebar
        
        ctk.CTkLabel(frame, text="Pilih Warna (Hex):", font=self.FONT_LABEL_BOLD).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Entry untuk kode Hex
        self.contour_color_entry = ctk.CTkEntry(frame, font=self.FONT_LABEL)
        self.contour_color_entry.insert(0, "#00FF00") # Default ke Hijau
        self.contour_color_entry.grid(row=0, column=1, padx=(0, 5), pady=10, sticky="ew")
        
        # Binding event <KeyRelease> untuk update pratinjau saat mengetik
        self.contour_color_entry.bind("<KeyRelease>", self._update_color_preview_from_entry)

        # Tombol untuk membuka color chooser
        self.contour_color_chooser_button = ctk.CTkButton(frame,
                                                  text="Pilih...",
                                                  width=50,
                                                  font=self.FONT_LABEL,
                                                  command=self._ask_contour_color)
        self.contour_color_chooser_button.grid(row=0, column=2, padx=(0, 5), pady=10)
        
        # Kotak Pratinjau Warna
        self.contour_color_preview = ctk.CTkFrame(frame, width=30, height=30, fg_color="#00FF00", border_width=2, border_color="gray")
        self.contour_color_preview.grid(row=0, column=3, padx=(0, 10), pady=10)

        # Tombol Terapkan
        ctk.CTkButton(self.dynamic_controls_frame,
                      text="✅ Terapkan Kontur",
                      command=self.commit_contours,
                      fg_color=self.COLOR_ACCENT_GREEN,
                      hover_color="#047857",
                      font=self.FONT_BUTTON).pack(fill="x", padx=10, pady=15)
    # ================================================================================= #

    # ================================================================================= #
    # ========================= LOGIKA PREVIEW & COMMIT (TETAP SAMA) ================== #
    # ================================================================================= #
    
    # 1. Preview Brightness & Contrast (Multi-slider) - FIXED
    def preview_brightness_contrast(self, value, value_label, format_str):
        if self.temp_image_for_preview is None: return
        
        b_val = self.brightness_slider.get() 
        c_val = self.contrast_slider.get()
        
        value_label.configure(text=format_str.format(value))
        
        if value_label == self.brightness_value_label:
            self.contrast_value_label.configure(text=f"{c_val:.2f}")
        elif value_label == self.contrast_value_label:
            self.brightness_value_label.configure(text=f"{b_val:.0f}")

        preview = cv2.convertScaleAbs(self.temp_image_for_preview, alpha=c_val, beta=b_val)
        self.display_image(preview, self.processed_image_label)
    
    def commit_brightness_contrast(self):
        alpha, beta = self.contrast_slider.get(), self.brightness_slider.get()
        self.apply_filter(lambda img: cv2.convertScaleAbs(img, alpha=alpha, beta=beta))
        self.clear_dynamic_controls()

    # 2. Preview Rotation (Single-slider) - FIXED
    def preview_rotation(self, value, value_label, format_str):
        if self.temp_image_for_preview is None: return
        value_label.configure(text=format_str.format(value))
        h, w = self.temp_image_for_preview.shape[:2]
        center, M = (w // 2, h // 2), cv2.getRotationMatrix2D((w // 2, h // 2), value, 1.0)
        preview = cv2.warpAffine(self.temp_image_for_preview, M, (w, h))
        self.display_image(preview, self.processed_image_label)

    def commit_rotation(self):
        angle = self.rotation_slider.get()
        h, w = self.processed_image.shape[:2]
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        self.apply_filter(lambda img: cv2.warpAffine(img, M, (w, h)))
        self.clear_dynamic_controls()
    
    # 3. Preview Thresholding (Single-slider) - FIXED
    def preview_thresholding(self, value, value_label, format_str):
        if self.temp_image_for_preview is None: return
        value_label.configure(text=format_str.format(value))
        gray = cv2.cvtColor(self.temp_image_for_preview, cv2.COLOR_BGR2GRAY) if len(self.temp_image_for_preview.shape) == 3 else self.temp_image_for_preview
        _, preview = cv2.threshold(gray, value, 255, cv2.THRESH_BINARY)
        self.display_image(preview, self.processed_image_label)

    def commit_thresholding(self):
        val = self.threshold_slider.get()
        def threshold_func(img):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
            return cv2.threshold(gray, val, 255, cv2.THRESH_BINARY)[1]
        self.apply_filter(threshold_func)
        self.clear_dynamic_controls()
        
    # 4. Preview Translation (Multi-slider) - FIXED
    def preview_translation(self, value, value_label, format_str):
        if self.temp_image_for_preview is None: return
        
        tx = self.tx_slider.get()
        ty = self.ty_slider.get()
        
        value_label.configure(text=format_str.format(value))
        
        if value_label == self.tx_value_label:
            self.ty_value_label.configure(text=f"{ty:.0f}px")
        elif value_label == self.ty_value_label:
            self.tx_value_label.configure(text=f"{tx:.0f}px")
            
        M = np.float32([[1, 0, tx], [0, 1, ty]])
        preview = cv2.warpAffine(self.temp_image_for_preview, M, (self.temp_image_for_preview.shape[1], self.temp_image_for_preview.shape[0]))
        self.display_image(preview, self.processed_image_label)

    def commit_translation(self):
        tx, ty = self.tx_slider.get(), self.ty_slider.get()
        M = np.float32([[1, 0, tx], [0, 1, ty]])
        self.apply_filter(lambda img: cv2.warpAffine(img, M, (img.shape[1], img.shape[0])))
        self.clear_dynamic_controls()

    # 5. Preview Zoom (Multi-slider) - FIXED
    def preview_zoom(self, value, value_label, format_str):
        if self.temp_image_for_preview is None: return
        
        fx, fy = self.fx_slider.get(), self.fy_slider.get()
        
        if value_label == self.fx_value_label:
            value_label.configure(text=format_str.format(value))
            self.fy_value_label.configure(text=f"{fy:.2f}x")
        elif value_label == self.fy_value_label:
            value_label.configure(text=format_str.format(value))
            self.fx_value_label.configure(text=f"{fx:.2f}x")
            
        preview = cv2.resize(self.temp_image_for_preview, None, fx=fx, fy=fy, interpolation=cv2.INTER_LINEAR)
        self.display_image(preview, self.processed_image_label)

    def commit_zoom(self):
        fx, fy = self.fx_slider.get(), self.fy_slider.get()
        self.apply_filter(lambda img: cv2.resize(img, None, fx=fx, fy=fy, interpolation=cv2.INTER_LINEAR))
        self.clear_dynamic_controls()

    # 6. Preview Highboost (Single-slider) - FIXED
    def preview_highboost(self, value, value_label, format_str):
        if self.temp_image_for_preview is None: return
        value_label.configure(text=format_str.format(value))
        k = value
        preview_img = self.temp_image_for_preview.copy()
        blurred = cv2.GaussianBlur(preview_img, (7, 7), 0)
        preview = cv2.addWeighted(preview_img, 1 + k, blurred, -k, 0)
        self.display_image(preview, self.processed_image_label)

    def commit_highboost(self):
        k = self.k_slider.get()
        self.apply_filter(lambda img: cv2.addWeighted(img, 1 + k, cv2.GaussianBlur(img, (7, 7), 0), -k, 0))
        self.clear_dynamic_controls()
        
    def commit_cropping(self):
        if self.processed_image is None: return
        try:
            x_min = int(self.xmin_entry.get())
            y_min = int(self.ymin_entry.get())
            x_max = int(self.xmax_entry.get())
            y_max = int(self.ymax_entry.get())
            
            H, W = self.processed_image.shape[:2]
            
            if not (0 <= x_min < x_max <= W and 0 <= y_min < y_max <= H):
                messagebox.showerror("Error", f"Koordinat tidak valid. Pastikan:\n0 <= X_min < X_max <= {W}\n0 <= Y_min < Y_max <= {H}")
                return

            def crop_func(img):
                return img[y_min:y_max, x_min:x_max]
            
            self.apply_filter(crop_func)
            self.clear_dynamic_controls()

        except ValueError:
            messagebox.showerror("Error", "Input koordinat harus berupa angka integer.")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {e}")
            
    def commit_convolution(self):
        if self.processed_image is None: return
        
        try:
            kernel_values = [float(entry.get()) for entry in self.kernel_entries]
            if len(kernel_values) != 9:
                raise ValueError("Kernel harus memiliki 9 nilai.")
            
            kernel = np.array(kernel_values).reshape(3, 3).astype(np.float32)

        except ValueError:
            messagebox.showerror("Error", "Semua nilai kernel harus berupa angka.")
            return

        def convolution_func(img):
            return cv2.filter2D(img, -1, kernel)
        
        self.apply_filter(convolution_func)
    
    def _load_kernel(self, kernel_list):
        for i, val in enumerate(kernel_list):
            self.kernel_entries[i].delete(0, tk.END)
            self.kernel_entries[i].insert(0, f"{val:.4f}" if isinstance(val, float) else str(val))
        self.commit_convolution()

    def _apply_gamma(self, img, gamma):
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255
                            for i in np.arange(0, 256)]).astype("uint8")
        return cv2.LUT(img, table)

    # 7. Preview Gamma (Single-slider) - FIXED
    def preview_gamma(self, value, value_label, format_str):
        if self.processed_image is None: return
        
        gamma = self.gamma_slider.get()
        value_label.configure(text=format_str.format(gamma))
        
        preview = self._apply_gamma(self.processed_image.copy(), gamma)
        self.display_image(preview, self.processed_image_label)
        self.temp_image_for_preview = preview

    def commit_gamma(self):
        if self.processed_image is None: return
        
        gamma = self.gamma_slider.get()
        
        filter_func = lambda img: self._apply_gamma(img, gamma)
        self.apply_filter(filter_func)
        self.clear_dynamic_controls()

    # 8. Preview ILPF (Single-slider) - FIXED
    def preview_ilpf(self, value, value_label, format_str):
        if self.processed_image is None: return
        D0 = self.ilpf_d0_slider.get()
        value_label.configure(text=format_str.format(D0))
        
        preview = self._apply_filter_in_frequency_domain(self.processed_image, lambda P, Q: self._ideal_lowpass_filter(P, Q, D0))
        self.display_image(preview, self.processed_image_label)
        self.temp_image_for_preview = preview

    def commit_ilpf(self):
        if self.processed_image is None: return
        D0 = self.ilpf_d0_slider.get()
        
        filter_func = lambda img: self._apply_filter_in_frequency_domain(
            img, 
            lambda P, Q: self._ideal_lowpass_filter(P, Q, D0)
        )
        self.apply_filter(filter_func)
        self.clear_dynamic_controls()
    
    # 9. Preview BLPF (Multi-slider) - FIXED LOGIC
    def preview_blpf(self, value, value_label, format_str):
        if self.processed_image is None: return
        
        D0 = self.blpf_d0_slider.get()
        n = self.blpf_n_slider.get()
        
        value_label.configure(text=format_str.format(value))
        
        if value_label == self.blpf_d0_value_label:
            self.blpf_n_value_label.configure(text=f"{n:.0f}")
        elif value_label == self.blpf_n_value_label:
            self.blpf_d0_value_label.configure(text=f"{D0:.0f}")

        preview = self._apply_filter_in_frequency_domain(
            self.processed_image, 
            lambda P, Q: self._butterworth_lowpass_filter(P, Q, D0, n)
        )
        self.display_image(preview, self.processed_image_label)
        self.temp_image_for_preview = preview

    def commit_blpf(self):
        if self.processed_image is None: return
        D0 = self.blpf_d0_slider.get()
        n = self.blpf_n_slider.get()

        filter_func = lambda img: self._apply_filter_in_frequency_domain(
            img, 
            lambda P, Q: self._butterworth_lowpass_filter(P, Q, D0, n)
        )
        self.apply_filter(filter_func)
        self.clear_dynamic_controls()
        
    # 10. Preview IHPF (Single-slider) - FIXED
    def preview_ihpf(self, value, value_label, format_str):
        if self.processed_image is None: return
        D0 = self.ihpf_d0_slider.get()
        value_label.configure(text=format_str.format(D0))
        
        preview = self._apply_filter_in_frequency_domain(self.processed_image, lambda P, Q: self._ideal_highpass_filter(P, Q, D0))
        self.display_image(preview, self.processed_image_label)
        self.temp_image_for_preview = preview

    def commit_ihpf(self):
        if self.processed_image is None: return
        D0 = self.ihpf_d0_slider.get()
        
        filter_func = lambda img: self._apply_filter_in_frequency_domain(img, lambda P, Q: self._ideal_highpass_filter(P, Q, D0))
        self.apply_filter(filter_func)
        self.clear_dynamic_controls()

    # 11. Preview BHPF (Multi-slider) - FIXED
    def preview_bhpf(self, value, value_label, format_str):
        if self.processed_image is None: return
        D0 = self.bhpf_d0_slider.get()
        n = self.bhpf_n_slider.get()
        
        if value_label == self.bhpf_d0_value_label:
            value_label.configure(text=format_str.format(value))
            self.bhpf_n_value_label.configure(text=f"{n:.0f}")
        elif value_label == self.bhpf_n_value_label:
            value_label.configure(text=format_str.format(value))
            self.bhpf_d0_value_label.configure(text=f"{D0:.0f}")

        preview = self._apply_filter_in_frequency_domain(self.processed_image, lambda P, Q: self._butterworth_highpass_filter(P, Q, D0, n))
        self.display_image(preview, self.processed_image_label)
        self.temp_image_for_preview = preview

    def commit_bhpf(self):
        if self.processed_image is None: return
        D0 = self.bhpf_d0_slider.get()
        n = self.bhpf_n_slider.get()

        filter_func = lambda img: self._apply_filter_in_frequency_domain(img, lambda P, Q: self._butterworth_highpass_filter(P, Q, D0, n))
        self.apply_filter(filter_func)
        self.clear_dynamic_controls()
        
    # ================================ [FUNGSI DIGANTI] ================================
    # Commit untuk Kontur (VERSI BARU DENGAN HEX)
    def commit_contours(self):
        if self.processed_image is None: return
        
        hex_code = self.contour_color_entry.get()
        
        # Validasi hex code sebelum konversi
        if not self._is_valid_hex(hex_code):
            messagebox.showerror("Error", f"Kode warna tidak valid: {hex_code}\nHarus dalam format #RRGGBB, misal: #FF0000")
            return

        try:
            # Konversi #RRGGBB ke tuple (B, G, R) yang dimengerti OpenCV
            hex_val = hex_code.lstrip('#')
            r = int(hex_val[0:2], 16)
            g = int(hex_val[2:4], 16)
            b = int(hex_val[4:6], 16)
            bgr_color = (b, g, r) # OpenCV menggunakan BGR
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal konversi warna: {e}")
            return
            
        # Panggil apply_filter dengan fungsi worker baru
        self.apply_filter(self._apply_contours_func, bgr_color)
        self.clear_dynamic_controls()
    # ================================================================================= #
        
    # ================================================================================= #
    # ========================= FUNGSI UTAMA (IO, History, dll.) ====================== #
    # ================================================================================= #
    def browse_files(self):
        filename = filedialog.askopenfilename(title="Pilih sebuah gambar", filetypes=(("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")))
        if filename:
            self.filename = filename
            self.load_and_display_image()
            
    def load_and_display_image(self):
        try:
            self.original_image = cv2.imread(self.filename)
            if self.original_image is None: raise ValueError("File tidak bisa dibaca.")
            self.history.clear()
            self.redo_stack.clear()
            self.display_image(self.original_image, self.original_image_label)
            self.reset_image()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat gambar: {e}")
            
    def display_image(self, cv2_image, label_widget):
        # Hapus border di wrapper saat gambar ditampilkan
        if label_widget.master.cget("border_width") != 0:
            label_widget.master.configure(border_width=0)
            
        h, w = cv2_image.shape[:2]
        
        # Ambil ukuran dari frame pembungkus (wrapper)
        wrapper = label_widget.master
        wrapper.update_idletasks() # Pastikan ukuran wrapper sudah di-render
        
        max_w = wrapper.winfo_width() - 40 # Kurangi padding
        max_h = wrapper.winfo_height() - 40
        
        if max_w <= 40 or max_h <= 40:
            # Fallback jika wrapper belum ter-render (misal: saat startup)
            max_w, max_h = self.IMAGE_WIDTH, self.IMAGE_HEIGHT
        
        aspect_ratio = w / h
        
        if w > max_w or h > max_h:
            if aspect_ratio > (max_w / max_h): # Gambar lebih lebar
                new_w = max_w
                new_h = int(new_w / aspect_ratio)
            else: # Gambar lebih tinggi
                new_h = max_h
                new_w = int(new_h * aspect_ratio)
        else:
            new_w, new_h = w, h
        
        resized = cv2.resize(cv2_image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        if len(resized.shape) == 2:
            img_rgb = cv2.cvtColor(resized, cv2.COLOR_GRAY2RGB)
        else:
            img_rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

        pil_img = Image.fromarray(img_rgb)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(new_w, new_h))
        
        label_widget.configure(image=ctk_img, text="")
        label_widget.image = ctk_img
        
    def apply_filter(self, filter_func, *args):
        if self.processed_image is None:
            messagebox.showwarning("Peringatan", "Buka gambar terlebih dahulu!")
            return
        try:
            # Simpan state sebelum filter
            self.history.append(self.processed_image.copy())
            
            # Terapkan filter
            new_image = filter_func(self.processed_image.copy(), *args)
            
            # Cek jika filter mengembalikan None (misal, jika dibatalkan)
            if new_image is None:
                self.history.pop() # Batalkan penyimpanan histori
                return
                
            self.processed_image = new_image
            self.display_image(self.processed_image, self.processed_image_label)
            self.redo_stack.clear()
            self.update_button_states()
            
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan saat menerapkan filter: {e}")
            if self.history: self.processed_image = self.history.pop()
            
    def update_button_states(self):
        # Gaya tombol normal
        normal_fg = self.COLOR_BG_DARK_3
        normal_hover = "#4B5563"
        # Gaya tombol aktif
        active_fg = self.COLOR_ACCENT_BLUE
        active_hover = "#2563EB"
        
        # Update Undo
        if self.history:
            self.undo_button.configure(state="normal", fg_color=active_fg, hover_color=active_hover)
        else:
            self.undo_button.configure(state="disabled", fg_color=normal_fg, hover_color=normal_hover)
        
        # Update Redo
        if self.redo_stack:
            self.redo_button.configure(state="normal", fg_color=active_fg, hover_color=active_hover)
        else:
            self.redo_button.configure(state="disabled", fg_color=normal_fg, hover_color=normal_hover)
            
        # Update Reset
        self.reset_button.configure(state="normal" if self.original_image is not None else "disabled")
        
    def undo_action(self):
        if self.history:
            self.redo_stack.append(self.processed_image.copy())
            self.processed_image = self.history.pop()
            self.display_image(self.processed_image, self.processed_image_label)
            self.update_button_states()
            self.clear_dynamic_controls()
            
    def redo_action(self):
        if self.redo_stack:
            self.history.append(self.processed_image.copy())
            self.processed_image = self.redo_stack.pop()
            self.display_image(self.processed_image, self.processed_image_label)
            self.update_button_states()
            self.clear_dynamic_controls()
            
    def reset_image(self):
        if self.original_image is not None:
            self.history.clear()
            self.redo_stack.clear()
            self.processed_image = self.original_image.copy()
            self.display_image(self.processed_image, self.processed_image_label)
            self.display_image(self.original_image, self.original_image_label) # Pastikan original juga ter-display
            self.update_button_states()
            self.clear_dynamic_controls()
            
    def save_image(self):
        if self.processed_image is None: return
        # Tambahkan opsi PNG (lossless) dan JPEG (lossy) saat menyimpan
        path = filedialog.asksaveasfilename(
            defaultextension=".png", 
            filetypes=[("PNG (Lossless)", "*.png"), ("JPEG (Lossy)", "*.jpg")]
        )
        if path:
            try:
                if path.lower().endswith(".jpg") or path.lower().endswith(".jpeg"):
                    # Simpan sebagai JPEG dengan kualitas tinggi (misal 95)
                    cv2.imwrite(path, self.processed_image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
                else:
                    # Default ke PNG (lossless)
                    cv2.imwrite(path, self.processed_image)
                    
                messagebox.showinfo("Sukses", f"Gambar disimpan di:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menyimpan gambar: {e}")
            
    def show_dev_info(self):
        info_text = (
            "Aplikasi ini dikembangkan oleh: Ariasyah Ramadhan\n"
            "- Tim Anda\n"
            "-------------------------------------\n"
            "Andre Alputra\n"
            "Ariasyah Ramadhan\n"
            "Muhammad Ihsanul Dzaki\n"
            "-------------------------------------\n"
            "Tutorial:\n"
            "✓ Link Github\n"
            "✓ Link YouTube"
        )
        messagebox.showinfo("About", info_text)
        
    def open_link(self, url):
        try:
            webbrowser.open_new_tab(url)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuka tautan: {e}")
            
    # ================================ [FUNGSI BARU DAN MODIFIKASI] ================================
    
    def show_lossless_info(self):
        """Menampilkan info tentang kompresi lossless."""
        if self.processed_image is None:
            messagebox.showwarning("Peringatan", "Buka gambar terlebih dahulu!")
            return
        messagebox.showinfo("Info Kompresi Lossless",
                            "Kompresi Lossless (seperti format PNG) tidak mengubah data piksel gambar.\n\n"
                            "Tidak ada perubahan visual yang akan Anda lihat di pratinjau ini.\n\n"
                            "Kompresi ini hanya mengurangi ukuran file saat Anda memilih 'File -> Save As...' dan menyimpan sebagai .png.")
    
    # [FUNGSI DIPERBAIKI] Worker untuk Kontur Citra
    def _apply_contours_func(self, img, bgr_color):
        """(Worker Function) Mendeteksi dan menggambar kontur pada gambar dengan warna yg dipilih."""
        # Buat salinan untuk digambari, pastikan berwarna (BGR)
        if len(img.shape) == 2:
            img_display = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            gray = img.copy()
        else:
            img_display = img.copy()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Gunakan Canny untuk deteksi tepi yang baik sebelum mencari kontur
        edges = cv2.Canny(gray, 100, 200)
        
        # Cari kontur
        contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Gambar kontur pada gambar display
        # Gunakan 'bgr_color' yang dilewatkan sebagai parameter
        cv2.drawContours(img_display, contours, -1, bgr_color, 2) 
        
        return img_display

    def _get_second_image_for_watermark(self):
        """Meminta gambar kedua (untuk watermark) tanpa mengubah ukurannya."""
        filename = filedialog.askopenfilename(title="Pilih Gambar Watermark (Misal: Logo)")
        if filename:
            # Baca dengan flag IMREAD_UNCHANGED untuk jaga transparansi (alpha channel)
            img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
            if img is not None:
                return img
        return None

    def apply_visible_watermark(self):
        """Menambahkan watermark gambar yang terlihat (visible), mendukung transparansi."""
        if self.processed_image is None:
            messagebox.showwarning("Peringatan", "Buka gambar terlebih dahulu!")
            return

        watermark_img = self._get_second_image_for_watermark()
        if watermark_img is None:
            return # Pengguna membatalkan

        def watermark_func(img):
            h_img, w_img = img.shape[:2]
            
            # Pastikan gambar utama adalah BGR (3 channel)
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            
            # Resize watermark agar tidak terlalu besar (misal 1/5 lebar)
            try:
                scale = (w_img / 5) / watermark_img.shape[1]
                w_wm = int(watermark_img.shape[1] * scale)
                h_wm = int(watermark_img.shape[0] * scale)
            except Exception as e:
                messagebox.showerror("Error", f"Gagal mengubah ukuran watermark: {e}")
                return img # Kembalikan gambar asli

            # Pastikan watermark tidak lebih besar dari gambar utama
            if h_wm > h_img: h_wm = h_img
            if w_wm > w_img: w_wm = w_img
            
            resized_wm = cv2.resize(watermark_img, (w_wm, h_wm), interpolation=cv2.INTER_AREA)

            # Cek apakah watermark punya alpha channel (transparansi)
            has_alpha = resized_wm.shape[2] == 4
            
            if has_alpha:
                # Pisahkan alpha channel
                b, g, r, a = cv2.split(resized_wm)
                # Buat overlay dari channel BGR
                overlay = cv2.merge((b, g, r))
                # Buat mask dari alpha channel
                mask = a / 255.0
                mask_inv = 1.0 - mask
            else:
                # Jika tidak ada alpha, buat mask penuh (blend 50/50)
                overlay = resized_wm
                mask = 0.3 # Atur transparansi manual
                mask_inv = 0.7

            # Tentukan Region of Interest (ROI) di pojok kanan bawah
            padding = 10
            y_offset = h_img - h_wm - padding
            x_offset = w_img - w_wm - padding
            
            # Pastikan ROI valid
            if y_offset < 0: y_offset = 0
            if x_offset < 0: x_offset = 0
            
            # Sesuaikan ukuran h_wm dan w_wm jika offset membuat mereka keluar batas
            h_wm_roi = h_img - y_offset
            w_wm_roi = w_img - x_offset
            
            # Ambil ulang ROI
            roi = img[y_offset:y_offset + h_wm_roi, x_offset:x_offset + w_wm_roi]

            # Resize watermark agar pas dengan ROI jika terpotong
            if resized_wm.shape[0] != h_wm_roi or resized_wm.shape[1] != w_wm_roi:
                 resized_wm = cv2.resize(watermark_img, (w_wm_roi, h_wm_roi), interpolation=cv2.INTER_AREA)
                 # Re-ekstrak mask/overlay jika di-resize
                 has_alpha = resized_wm.shape[2] == 4
                 if has_alpha:
                    b, g, r, a = cv2.split(resized_wm)
                    overlay = cv2.merge((b, g, r))
                    mask = a / 255.0
                    mask_inv = 1.0 - mask
                 else:
                    overlay = resized_wm
                    mask = 0.3
                    mask_inv = 0.7

            # Blend watermark ke ROI
            try:
                # Bagian gambar asli: roi * (1 - mask)
                # Bagian watermark: overlay * mask
                if has_alpha: # Jika ada alpha
                    for c in range(0, 3):
                        roi[:, :, c] = (mask_inv * roi[:, :, c]) + (mask * overlay[:, :, c])
                else: # Jika tidak ada alpha (blend manual)
                     roi = cv2.addWeighted(roi, mask_inv, overlay, mask, 0)
            except Exception as e:
                 messagebox.showerror("Blending Error", f"Gagal mem-blend gambar: {e}. Pastikan watermark tidak lebih besar dari gambar.")
                 return img

            # Kembalikan ROI yang sudah diblend ke gambar utama
            img[y_offset:y_offset + h_wm_roi, x_offset:x_offset + w_wm_roi] = roi
            return img

        self.apply_filter(watermark_func)

    def apply_compression_preview(self):
        """Mensimulasikan kompresi JPEG lossy dengan kualitas rendah."""
        def compress_func(img):
            # Encode ke JPEG dengan kualitas 10 (0-100)
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 10]
            result, encimg = cv2.imencode('.jpg', img, encode_param)
            if not result:
                messagebox.showerror("Error", "Gagal melakukan encode JPEG.")
                return img # Kembalikan gambar asli jika gagal
            
            # Decode kembali dari memory buffer
            decimg = cv2.imdecode(encimg, 1)
            return decimg
        
        self.apply_filter(compress_func)
        messagebox.showinfo("Info", "Pratinjau kompresi Lossy (JPEG Kualitas=10) diterapkan.\n"
                            "Anda melihat artefak kompresi. Untuk menyimpan, gunakan File -> Save As...")

    def _text_to_binary(self, text):
        """Mengubah string teks menjadi string biner (urutan bit)."""
        return ''.join(format(ord(char), '08b') for char in text)

    def setup_steganography_encode(self):
        """Meminta input teks untuk disembunyikan."""
        if self.processed_image is None:
            messagebox.showwarning("Peringatan", "Buka gambar terlebih dahulu!")
            return
        
        dialog = ctk.CTkInputDialog(text="Masukkan pesan rahasia:", title="Steganografi (Encode)")
        message = dialog.get_input()
        
        if message:
            # Tambahkan delimiter unik untuk menandai akhir pesan
            message += "::EOF::" 
            # Kirim fungsi dan argumennya ke apply_filter
            self.apply_filter(self._steganography_encode_func, message)
        
    def _steganography_encode_func(self, img, message):
        """(Worker Function) Menyembunyikan pesan ke dalam LSB gambar."""
        binary_message = self._text_to_binary(message)
        data_index = 0
        n_bits = len(binary_message)
        
        # Cek apakah gambar berwarna, jika tidak, batalkan.
        if len(img.shape) < 3:
            messagebox.showerror("Error", "Steganografi LSB membutuhkan gambar berwarna (3 channel).")
            return None # Mengembalikan None akan membatalkan apply_filter

        h, w, c = img.shape
        
        if n_bits > (h * w * c):
            messagebox.showerror("Error", "Pesan terlalu besar untuk disembunyikan di gambar ini.")
            return None # Mengembalikan None akan membatalkan apply_filter

        for i in range(h):
            for j in range(w):
                for k in range(c): # Untuk R, G, B
                    if data_index < n_bits:
                        pixel_val = img[i, j, k]
                        message_bit = int(binary_message[data_index])
                        # Ubah LSB pixel: & 254 (11111110) -> nol-kan LSB
                        # | message_bit -> atur LSB ke bit pesan
                        img[i, j, k] = (pixel_val & 254) | message_bit
                        data_index += 1
                    else:
                        # Selesai menyembunyikan
                        messagebox.showinfo("Sukses", "Pesan berhasil disembunyikan.")
                        return img
        return img
        
    def apply_steganography_decode(self):
        """Mengekstrak pesan rahasia dari LSB gambar."""
        if self.processed_image is None:
            messagebox.showwarning("Peringatan", "Buka gambar (yang berisi pesan) terlebih dahulu!")
            return
            
        # Cek apakah gambar berwarna
        if len(self.processed_image.shape) < 3:
            messagebox.showerror("Error", "Steganografi LSB membutuhkan gambar berwarna (3 channel).")
            return

        binary_data = ""
        decoded_message = ""
        h, w, c = self.processed_image.shape
        
        try:
            for i in range(h):
                for j in range(w):
                    for k in range(c):
                        # Baca LSB (Least Significant Bit)
                        lsb = self.processed_image[i, j, k] & 1
                        binary_data += str(lsb)
                        
                        # Cek per 8 bit (1 byte)
                        if len(binary_data) == 8:
                            char_code = int(binary_data, 2)
                            
                            # Coba decode sebagai UTF-8, abaikan jika error
                            try:
                                decoded_message += chr(char_code)
                            except UnicodeDecodeError:
                                # Mungkin ini bukan bagian dari teks yang valid, reset
                                decoded_message = ""
                                
                            binary_data = ""
                            
                            # Cek apakah delimiter ditemukan
                            if decoded_message.endswith("::EOF::"):
                                # Hapus delimiter dan tampilkan
                                final_message = decoded_message[:-7]
                                if final_message:
                                    messagebox.showinfo("Pesan Tersembunyi", f"Pesan:\n\n{final_message}")
                                else:
                                    messagebox.showerror("Info", "Tidak ada pesan tersembunyi yang ditemukan.")
                                return # Selesai
            
            # Jika loop selesai tanpa delimiter
            messagebox.showerror("Error", "Tidak ada pesan tersembunyi (atau delimiter tidak ditemukan).")

        except Exception as e:
            messagebox.showerror("Error", f"Gagal mendekode pesan: {e}\n(Mungkin tidak ada pesan)")

    # ======================================= [PENAMBAHAN FUNGSI SELESAI] ========================================

    # ================================================================================= #
    # ================= FUNGSI PEMROSESAN GAMBAR (INTI ASLI - TETAP SAMA) ============= #
    # ================================================================================= #
    def _get_second_image(self):
        messagebox.showinfo("Informasi", "Operasi ini membutuhkan gambar kedua.")
        filename = filedialog.askopenfilename(title="Pilih Gambar Kedua")
        if filename:
            img = cv2.imread(filename)
            if img is not None:
                h, w = self.processed_image.shape[:2]
                return cv2.resize(img, (w, h))
        return None
        
    # --- Edge Detection ---
    def apply_sobel(self): self.apply_filter(lambda img: cv2.convertScaleAbs(cv2.Sobel(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.CV_64F, 1, 1, ksize=5)))
    def apply_laplacian(self): self.apply_filter(lambda img: cv2.convertScaleAbs(cv2.Laplacian(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.CV_64F)))
    def apply_canny(self): self.apply_filter(lambda img: cv2.Canny(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 100, 200))
    def apply_log(self): self.apply_filter(lambda img: cv2.convertScaleAbs(cv2.Laplacian(cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (3, 3), 0), cv2.CV_64F)))
    def apply_prewitt(self):
        kernelx, kernely = np.array([[1,1,1],[0,0,0],[-1,-1,-1]]), np.array([[-1,0,1],[-1,0,1],[-1,0,1]])
        self.apply_filter(lambda img: cv2.add(cv2.filter2D(img, -1, kernelx), cv2.filter2D(img, -1, kernely)))
    def apply_robert(self):
        kernelx, kernely = np.array([[1, 0], [0, -1]]), np.array([[0, 1], [-1, 0]])
        self.apply_filter(lambda img: cv2.add(cv2.filter2D(img, -1, kernelx), cv2.filter2D(img, -1, kernely)))
    def apply_kirsch_compass(self):
        def kirsch_func(img):
            if len(img.shape) == 3: gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else: gray = img.copy()
            
            kernels = [
                np.array([[-3, -3, 5], [-3, 0, 5], [-3, -3, 5]], dtype=np.float32), 
                np.array([[-3, 5, 5], [-3, 0, 5], [-3, -3, -3]], dtype=np.float32),
                np.array([[5, 5, 5], [-3, 0, -3], [-3, -3, -3]], dtype=np.float32),
                np.array([[5, 5, -3], [5, 0, -3], [-3, -3, -3]], dtype=np.float32),
                np.array([[5, -3, -3], [5, 0, -3], [5, -3, -3]], dtype=np.float32),
                np.array([[-3, -3, -3], [5, 0, -3], [5, 5, -3]], dtype=np.float32),
                np.array([[-3, -3, -3], [-3, 0, -3], [5, 5, 5]], dtype=np.float32),
                np.array([[-3, -3, -3], [-3, 0, 5], [-3, 5, 5]], dtype=np.float32)
            ]
            
            responses = []
            for kernel in kernels: responses.append(cv2.filter2D(gray, -1, kernel))
            
            kirsch_output = np.max(np.array(responses), axis=0)
            kirsch_output = cv2.normalize(kirsch_output, None, 0, 255, cv2.NORM_MINMAX)
            return np.uint8(kirsch_output)
            
        self.apply_filter(kirsch_func)

    # --- Basic Ops / Arithmetics / Boolean / Colouring ---
    def apply_negative(self): self.apply_filter(lambda img: cv2.bitwise_not(img))
    def apply_multiply(self):
        img2 = self._get_second_image()
        if img2 is not None: 
            self.apply_filter(lambda img1: cv2.multiply(img1, img2, scale=1.0))
    def apply_divide(self):
        img2 = self._get_second_image()
        if img2 is not None: 
            self.apply_filter(lambda img1: cv2.divide(img1, img2, scale=255.0))
    def apply_not(self): 
        self.apply_filter(lambda img: cv2.bitwise_not(img))
    def apply_add(self):
        img2 = self._get_second_image()
        if img2 is not None: self.apply_filter(lambda img1: cv2.add(img1, img2))
    def apply_subtract(self):
        img2 = self._get_second_image()
        if img2 is not None: self.apply_filter(lambda img1: cv2.subtract(img1, img2))
    def apply_and(self):
        img2 = self._get_second_image()
        if img2 is not None: self.apply_filter(lambda img1: cv2.bitwise_and(img1, img2))
    def apply_or(self):
        img2 = self._get_second_image()
        if img2 is not None: self.apply_filter(lambda img1: cv2.bitwise_or(img1, img2))
    def apply_xor(self):
        img2 = self._get_second_image()
        if img2 is not None: self.apply_filter(lambda img1: cv2.bitwise_xor(img1, img2))
    def apply_flipping(self): self.apply_filter(lambda img: cv2.flip(img, 1))
    def apply_grayscale(self): 
        self.apply_filter(lambda img: cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img)
    def apply_colorspace(self, colorspace_code): self.apply_filter(lambda img: cv2.cvtColor(img, colorspace_code))
    def apply_binary(self):
        def binary_func(img):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img.copy()
            _, binary_img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            return binary_img
        self.apply_filter(binary_func)
    def apply_rgb(self):
        self.apply_filter(lambda img: cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    def apply_cmy(self):
        def cmy_func(img):
            b, g, r = cv2.split(img)
            c = cv2.bitwise_not(r)
            m = cv2.bitwise_not(g)
            y = cv2.bitwise_not(b)
            cmy_img = cv2.merge([y, m, c])
            return cmy_img
        self.apply_filter(cmy_func)
    def apply_yiq(self):
        def yiq_func(img):
            img_float = img.astype(np.float32) / 255.0
            rows, cols, _ = img_float.shape
            yiq_matrix = np.array([[ 0.114, 0.587, 0.299], [-0.322, -0.274, 0.596], [ 0.312, -0.523, 0.211]], dtype=np.float32)
            img_reshaped = img_float.reshape(-1, 3)
            yiq_reshaped = np.dot(img_reshaped, yiq_matrix.T)
            yiq_img = yiq_reshaped.reshape(rows, cols, 3)
            Y = yiq_img[:,:,0]
            Y_scaled = np.clip(Y * 255, 0, 255).astype(np.uint8)
            return Y_scaled 
        self.apply_filter(yiq_func)
    def apply_pseudo(self):
        def pseudo_func(img):
            if len(img.shape) == 3: gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else: gray = img.copy()
            pseudo_color = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
            return pseudo_color
        self.apply_filter(pseudo_func)
    def apply_fourier_transform(self):
        def fourier_func(img):
            if len(img.shape) == 3: gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else: gray = img.copy()
            gray = np.float32(gray)
            dft = cv2.dft(gray, flags=cv2.DFT_COMPLEX_OUTPUT)
            dft_shift = np.fft.fftshift(dft)
            magnitude_spectrum = 20 * np.log(cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1]))
            fourier_image = cv2.normalize(magnitude_spectrum, None, 0, 255, cv2.NORM_MINMAX)
            return np.uint8(fourier_image)
        self.apply_filter(fourier_func)
    
    # --- Enhancement / Smoothing / Sharpening / Correction ---
    def apply_hist_equalization(self):
        def equalize(img):
            if len(img.shape) == 3:
                img_ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
                img_ycrcb[:, :, 0] = cv2.equalizeHist(img_ycrcb[:, :, 0])
                return cv2.cvtColor(img_ycrcb, cv2.COLOR_YCrCb2BGR)
            else: return cv2.equalizeHist(img)
        self.apply_filter(equalize)
    def apply_blur(self): self.apply_filter(lambda img: cv2.blur(img, (7, 7)))
    def apply_median_filter(self): self.apply_filter(lambda img: cv2.medianBlur(img, 5))
    def apply_sharpen(self):
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        self.apply_filter(lambda img: cv2.filter2D(img, -1, kernel))
    def apply_geometrics(self):
        messagebox.showinfo("Informasi", "Operasi Geometrik (Translation, Rotation, Zooming, Flipping, Cropping) telah tersedia secara lengkap di menu 'Basic Ops' -> 'Geometrics'.")

    # --- Noise ---
    def _add_noise_to_image(self, img, noise_func):
        img_float = img.astype(np.float32) / 255.0
        noise = noise_func(img_float.shape)
        noisy_img_float = np.clip(img_float + noise, 0.0, 1.0)
        return (noisy_img_float * 255).astype(np.uint8)
    def add_gaussian_noise(self):
        self.apply_filter(lambda img: cv2.add(img, np.random.normal(0, 1, img.shape).astype('uint8') * 50))
    def add_impulse_noise(self):
        # Ini sepertinya lebih mirip noise seragam, bukan salt & pepper
        # Tapi saya biarkan sesuai kode asli Anda
        self.apply_filter(lambda img: cv2.randu(np.copy(img), 0, 255)) 
    def add_rayleigh_noise(self):
        def rayleigh_noise_generator(shape, sigma=0.1):
            uniform = np.random.uniform(size=shape)
            return sigma * np.sqrt(-2 * np.log(uniform + 1e-6))
        self.apply_filter(lambda img: self._add_noise_to_image(img, rayleigh_noise_generator))
    def add_erlang_noise(self):
        def erlang_noise_generator(shape, a=2, scale=0.02):
            return np.random.gamma(a, scale, size=shape)
        self.apply_filter(lambda img: self._add_noise_to_image(img, erlang_noise_generator))
    def add_exponential_noise(self):
        def exponential_noise_generator(shape, scale=0.03):
            return np.random.exponential(scale, size=shape)
        # Koreksi kecil: Anda memanggil uniform_noise_generator di sini, saya ganti ke exponential
        self.apply_filter(lambda img: self._add_noise_to_image(img, exponential_noise_generator)) 
    def add_uniform_noise(self):
        def uniform_noise_generator(shape, low=-0.1, high=0.1):
            return np.random.uniform(low, high, size=shape)
        self.apply_filter(lambda img: self._add_noise_to_image(img, uniform_noise_generator))
        
    # ================================================================================= #
    # ================== FUNGSI BANTUAN DOMAIN FREKUENSI (ASLI) ======================= #
    # ================================================================================= #
    def _create_dft_matrix(self, img):
        h, w = img.shape[:2]
        if len(img.shape) == 3: gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float64)
        else: gray = img.astype(np.float64)

        P, Q = h, w
        X, Y = np.mgrid[0:h, 0:w]
        gray = gray * ((-1)**(X + Y))
        dft = cv2.dft(gray, flags=cv2.DFT_COMPLEX_OUTPUT)
        return dft, P, Q

    def _apply_filter_in_frequency_domain(self, img, filter_generator):
        dft, P, Q = self._create_dft_matrix(img)
        H = filter_generator(P, Q)
        H_complex = np.dstack((H, H))
        G = dft * H_complex
        idft = cv2.idft(G, flags=cv2.DFT_SCALE | cv2.DFT_REAL_OUTPUT)
        X, Y = np.mgrid[0:P, 0:Q]
        result = idft * ((-1)**(X + Y))
        result = np.clip(result, 0, 255)
        return result.astype(np.uint8)

    def _create_distance_matrix(self, P, Q):
        u = np.arange(P)
        v = np.arange(Q)
        U, V = np.meshgrid(u, v, indexing='ij')
        U_center = P / 2
        V_center = Q / 2
        D = np.sqrt((U - U_center)**2 + (V - V_center)**2)
        return D

    # --- Lowpass Filters ---
    def _ideal_lowpass_filter(self, P, Q, D0):
        D = self._create_distance_matrix(P, Q)
        H = np.where(D <= D0, 1, 0).astype(np.float64)
        return H

    def _butterworth_lowpass_filter(self, P, Q, D0, n):
        D = self._create_distance_matrix(P, Q)
        H = 1.0 / (1.0 + (D / D0)**(2 * n))
        return H
    
    # --- Highpass Filters ---
    def _ideal_highpass_filter(self, P, Q, D0):
        D = self._create_distance_matrix(P, Q)
        H = np.where(D > D0, 1, 0).astype(np.float64)
        return H

    def _butterworth_highpass_filter(self, P, Q, D0, n):
        D = self._create_distance_matrix(P, Q)
        H = 1.0 / (1.0 + (D0 / (D + 1e-6))**(2 * n))
        return H

if __name__ == "__main__":
    app = ImageProcessingApp()
    app.mainloop()