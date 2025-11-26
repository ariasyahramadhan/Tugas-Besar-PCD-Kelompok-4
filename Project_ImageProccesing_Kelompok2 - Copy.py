import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import cv2
import numpy as np
import webbrowser
from collections import deque

# Atur tema default
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ImageProcessingApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ========================= KONFIGURASI WINDOW UTAMA ========================= #
        self.title("✨ Cipta Mulya | Image Processor")
        self.geometry("1500x850")
        self.minsize(1300, 700)

        # Inisialisasi variabel (TETAP SAMA)
        self.original_image = None
        self.processed_image = None
        self.temp_image_for_preview = None # Untuk preview slider
        self.filename = ""
        self.IMAGE_WIDTH = 600
        self.IMAGE_HEIGHT = 450
        
        self.history = deque(maxlen=20)
        self.redo_stack = deque(maxlen=20)

        # Inisialisasi variabel untuk referensi label nilai slider (PENTING UNTUK FIX INI)
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

        self.create_menubar()

        # ========================= LAYOUT UTAMA (MODERN) ========================= #
        self.grid_columnconfigure(0, weight=0, minsize=350) # Panel Kontrol Kiri (Lebar Tetap/Minimal)
        self.grid_columnconfigure(1, weight=4) # Area Gambar Kanan (Bobot Lebih Besar)
        self.grid_rowconfigure(0, weight=1)

        # ========================= FRAME KONTROL (KIRI) ========================= #
        control_frame = ctk.CTkFrame(self, width=350, corner_radius=15, fg_color="#2A2D30")
        control_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        control_frame.grid_propagate(False)

        # Judul Kontrol
        app_title = ctk.CTkLabel(control_frame, text="⚙️ Panel Kontrol", font=ctk.CTkFont(size=26, weight="bold"))
        app_title.pack(pady=(25, 5))
        
        # Divider visual
        ctk.CTkFrame(control_frame, height=2, fg_color="gray").pack(fill="x", padx=20, pady=(5, 15))
        
        # --- STATIC CONTROLS (I/O & History) ---
        static_controls_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        static_controls_frame.pack(pady=5, fill="x", padx=15)
        static_controls_frame.grid_columnconfigure((0,1), weight=1)
        
        # Tombol I/O lebih menonjol
        ctk.CTkButton(static_controls_frame, text="📂 Buka Gambar", command=self.browse_files, fg_color="#3B82F6", hover_color="#2563EB", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(static_controls_frame, text="💾 Simpan Hasil", command=self.save_image, fg_color="#10B981", hover_color="#059669", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Tombol History
        history_frame = ctk.CTkFrame(static_controls_frame, fg_color="transparent")
        history_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=(10, 5), sticky="ew")
        history_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.undo_button = ctk.CTkButton(history_frame, text="↩️ Undo", command=self.undo_action, state="disabled", fg_color="#4B5563", hover_color="#374151")
        self.undo_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.redo_button = ctk.CTkButton(history_frame, text="↪️ Redo", command=self.redo_action, state="disabled", fg_color="#4B5563", hover_color="#374151")
        self.redo_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Tombol Reset
        self.reset_button = ctk.CTkButton(static_controls_frame, text="🔄 Reset Semua", command=self.reset_image, fg_color="#EF4444", hover_color="#DC2626", state="disabled")
        self.reset_button.grid(row=2, column=0, columnspan=2, padx=5, pady=(5, 10), sticky="ew")
        
        # --- DYNAMIC CONTROLS (SCROLLABLE FRAME) ---
        self.dynamic_controls_frame = ctk.CTkScrollableFrame(control_frame, label_text="Panel Operasi Dinamis", corner_radius=10, label_font=ctk.CTkFont(size=18, weight="bold"), label_fg_color="#374151")
        self.dynamic_controls_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Tombol Keluar di bagian bawah
        exit_button = ctk.CTkButton(control_frame, text="❌ Keluar Aplikasi", command=self.quit, fg_color="#e53e3e", hover_color="#c53030", font=ctk.CTkFont(weight="bold"))
        exit_button.pack(side="bottom", fill="x", padx=20, pady=20)

        # ========================= FRAME GAMBAR (KANAN) ========================= #
        image_display_frame = ctk.CTkFrame(self, fg_color="transparent")
        image_display_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        image_display_frame.grid_columnconfigure((0, 1), weight=1)
        image_display_frame.grid_rowconfigure(1, weight=1)

        # Label judul gambar
        ctk.CTkLabel(image_display_frame, text="🌄 Gambar Original", font=ctk.CTkFont(size=24, weight="bold"), text_color="#FBBF24").grid(row=0, column=0, pady=(0, 10))
        ctk.CTkLabel(image_display_frame, text="💻 Gambar Hasil Proses", font=ctk.CTkFont(size=24, weight="bold"), text_color="#60A5FA").grid(row=0, column=1, pady=(0, 10))

        # Wrapper Gambar Original
        original_wrapper = ctk.CTkFrame(image_display_frame, fg_color="#1F2937", corner_radius=10)
        original_wrapper.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        original_wrapper.grid_rowconfigure(0, weight=1)
        original_wrapper.grid_columnconfigure(0, weight=1)

        self.original_image_label = ctk.CTkLabel(original_wrapper, text="Buka gambar untuk memulai...", corner_radius=10, fg_color="#1F2937")
        self.original_image_label.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Wrapper Gambar Hasil Proses
        processed_wrapper = ctk.CTkFrame(image_display_frame, fg_color="#1F2937", corner_radius=10)
        processed_wrapper.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        processed_wrapper.grid_rowconfigure(0, weight=1)
        processed_wrapper.grid_columnconfigure(0, weight=1)

        self.processed_image_label = ctk.CTkLabel(processed_wrapper, text="Hasil proses akan muncul di sini", corner_radius=10, fg_color="#1F2937")
        self.processed_image_label.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    
    # ========================= FUNGSI MENU BAR (GAYA MODERN) ========================= #
    def create_menubar(self):
        # Definisikan gaya untuk menu
        menu_bg = "#2A2D30"  # Latar belakang gelap, konsisten dengan control_frame
        menu_fg = "#E0E0E0"  # Teks terang
        menu_active_bg = "#1E88E5"  # Warna biru lebih intens saat hover
        menu_active_fg = "white"
        menu_font = ("Arial", 11)  # Font modern dan bersih
        
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
        
        # About Menu
        about_menu = tk.Menu(menubar, **submenu_style)
        menubar.add_cascade(label="About", menu=about_menu)
        
        ABOUT_GITHUB_URL = "https://github.com/ariasyahramadhan" 
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

    def _create_slider_set(self, parent, label_text, from_, to, initial_val, format_str, callback):
        # Frame dengan padding minimal dan corner radius kecil
        frame = ctk.CTkFrame(parent, fg_color="#374151", corner_radius=8)
        frame.pack(fill="x", padx=10, pady=5)
        
        # Label utama
        label = ctk.CTkLabel(frame, text=label_text, width=120, anchor="w", font=ctk.CTkFont(weight="bold"))
        label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Label nilai
        value_label = ctk.CTkLabel(frame, text=format_str.format(initial_val), width=60, anchor="e", fg_color="#4B5563", corner_radius=5)
        value_label.grid(row=0, column=2, padx=(5, 10), pady=5, sticky="e")
        
        # Slider
        # Memastikan value_label dan format_str diteruskan ke callback
        slider = ctk.CTkSlider(frame, from_=from_, to=to, command=lambda val: callback(val, value_label, format_str))
        slider.set(initial_val)
        slider.grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="ew")
        
        frame.grid_columnconfigure(1, weight=1) # Agar slider bisa melebar
        return frame, slider

    # --- SETUP KONTROL DENGAN DESAIN BARU ---
    # *FIXED: Memastikan referensi label tersimpan untuk semua kontrol multi-slider*
    def setup_brightness_contrast_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        self.temp_image_for_preview = self.processed_image.copy()
        ctk.CTkLabel(self.dynamic_controls_frame, text="Kontrol Kecerahan & Kontras", font=ctk.CTkFont(size=16, weight="bold"), text_color="#A78BFA").pack(pady=(10, 5))
        
        bf, self.brightness_slider = self._create_slider_set(self.dynamic_controls_frame, "Kecerahan (Beta)", -100, 100, 0, "{:.0f}", self.preview_brightness_contrast)
        self.brightness_value_label = bf.winfo_children()[2] # Simpan referensi label nilai
        bf.pack(fill="x", padx=10, pady=5)
        
        cf, self.contrast_slider = self._create_slider_set(self.dynamic_controls_frame, "Kontras (Alpha)", 0, 3, 1, "{:.2f}", self.preview_brightness_contrast)
        self.contrast_value_label = cf.winfo_children()[2] # Simpan referensi label nilai
        cf.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Terapkan Perubahan", command=self.commit_brightness_contrast, fg_color="#059669", hover_color="#047857").pack(fill="x", padx=10, pady=15)

    def setup_rotation_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        self.temp_image_for_preview = self.processed_image.copy()
        ctk.CTkLabel(self.dynamic_controls_frame, text="Kontrol Rotasi", font=ctk.CTkFont(size=16, weight="bold"), text_color="#A78BFA").pack(pady=(10, 5))
        rf, self.rotation_slider = self._create_slider_set(self.dynamic_controls_frame, "Sudut Rotasi", 0, 360, 0, "{:.0f}°", self.preview_rotation)
        self.rotation_value_label = rf.winfo_children()[2] # Simpan referensi label nilai
        rf.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Terapkan Rotasi", command=self.commit_rotation, fg_color="#059669", hover_color="#047857").pack(fill="x", padx=10, pady=15)

    def setup_thresholding_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        self.temp_image_for_preview = self.processed_image.copy()
        ctk.CTkLabel(self.dynamic_controls_frame, text="Kontrol Thresholding", font=ctk.CTkFont(size=16, weight="bold"), text_color="#A78BFA").pack(pady=(10, 5))
        tf, self.threshold_slider = self._create_slider_set(self.dynamic_controls_frame, "Nilai Threshold", 0, 255, 127, "{:.0f}", self.preview_thresholding)
        self.threshold_value_label = tf.winfo_children()[2] # Simpan referensi label nilai
        tf.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Terapkan Threshold", command=self.commit_thresholding, fg_color="#059669", hover_color="#047857").pack(fill="x", padx=10, pady=15)

    def setup_translation_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        self.temp_image_for_preview = self.processed_image.copy()
        ctk.CTkLabel(self.dynamic_controls_frame, text="Kontrol Translasi", font=ctk.CTkFont(size=16, weight="bold"), text_color="#A78BFA").pack(pady=(10, 5))
        
        tx_f, self.tx_slider = self._create_slider_set(self.dynamic_controls_frame, "Translasi X", -100, 100, 0, "{:.0f}px", self.preview_translation)
        self.tx_value_label = tx_f.winfo_children()[2] # Simpan referensi label nilai
        tx_f.pack(fill="x", padx=10, pady=5)
        
        ty_f, self.ty_slider = self._create_slider_set(self.dynamic_controls_frame, "Translasi Y", -100, 100, 0, "{:.0f}px", self.preview_translation)
        self.ty_value_label = ty_f.winfo_children()[2] # Simpan referensi label nilai
        ty_f.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Terapkan Translasi", command=self.commit_translation, fg_color="#059669", hover_color="#047857").pack(fill="x", padx=10, pady=15)

    def setup_zoom_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        self.temp_image_for_preview = self.processed_image.copy()
        ctk.CTkLabel(self.dynamic_controls_frame, text="Kontrol Zooming", font=ctk.CTkFont(size=16, weight="bold"), text_color="#A78BFA").pack(pady=(10, 5))
        
        fx_f, self.fx_slider = self._create_slider_set(self.dynamic_controls_frame, "Faktor Zoom X", 0.1, 3, 1, "{:.2f}x", self.preview_zoom)
        self.fx_value_label = fx_f.winfo_children()[2]
        fx_f.pack(fill="x", padx=10, pady=5)
        
        fy_f, self.fy_slider = self._create_slider_set(self.dynamic_controls_frame, "Faktor Zoom Y", 0.1, 3, 1, "{:.2f}x", self.preview_zoom)
        self.fy_value_label = fy_f.winfo_children()[2]
        fy_f.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Terapkan Zoom", command=self.commit_zoom, fg_color="#059669", hover_color="#047857").pack(fill="x", padx=10, pady=15)

    def setup_highboost_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        self.temp_image_for_preview = self.processed_image.copy()
        ctk.CTkLabel(self.dynamic_controls_frame, text="Kontrol Highboost", font=ctk.CTkFont(size=16, weight="bold"), text_color="#A78BFA").pack(pady=(10, 5))
        k_f, self.k_slider = self._create_slider_set(self.dynamic_controls_frame, "K-Factor", 0, 5, 1.2, "{:.2f}", self.preview_highboost)
        self.k_value_label = k_f.winfo_children()[2] # Simpan referensi label nilai
        k_f.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Terapkan Highboost", command=self.commit_highboost, fg_color="#059669", hover_color="#047857").pack(fill="x", padx=10, pady=15)

    def setup_cropping_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        
        ctk.CTkLabel(self.dynamic_controls_frame, text="✂️ Masukkan Koordinat Cropping", font=ctk.CTkFont(size=16, weight="bold"), text_color="#A78BFA").pack(pady=(10, 5))
        
        input_frame = ctk.CTkFrame(self.dynamic_controls_frame, fg_color="#374151", corner_radius=8)
        input_frame.pack(fill="x", padx=10, pady=5)
        input_frame.grid_columnconfigure((0, 1), weight=1)

        H, W = self.processed_image.shape[:2]
        ctk.CTkLabel(input_frame, text="X Kiri (Xmin)").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.xmin_entry = ctk.CTkEntry(input_frame, width=80)
        self.xmin_entry.insert(0, "0")
        self.xmin_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ctk.CTkLabel(input_frame, text="Y Atas (Ymin)").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.ymin_entry = ctk.CTkEntry(input_frame, width=80)
        self.ymin_entry.insert(0, "0")
        self.ymin_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        ctk.CTkLabel(input_frame, text=f"X Kanan (Xmax) [Max:{W}]").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.xmax_entry = ctk.CTkEntry(input_frame, width=80)
        self.xmax_entry.insert(0, str(W))
        self.xmax_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        
        ctk.CTkLabel(input_frame, text=f"Y Bawah (Ymax) [Max:{H}]").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.ymax_entry = ctk.CTkEntry(input_frame, width=80)
        self.ymax_entry.insert(0, str(H))
        self.ymax_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Terapkan Cropping", command=self.commit_cropping, fg_color="#059669", hover_color="#047857").pack(fill="x", padx=10, pady=15)

    def setup_convolution_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        
        ctk.CTkLabel(self.dynamic_controls_frame, text="🎛️ Kernel Konvolusi 3x3", font=ctk.CTkFont(size=16, weight="bold"), text_color="#A78BFA").pack(pady=(10, 5))
        
        kernel_frame = ctk.CTkFrame(self.dynamic_controls_frame, fg_color="#374151", corner_radius=8)
        kernel_frame.pack(pady=5, padx=10)
        
        self.kernel_entries = []
        default_kernel = [0, 0, 0, 0, 1, 0, 0, 0, 0] 
        
        for i in range(3):
            for j in range(3):
                kernel_frame.grid_columnconfigure(j, weight=1)
                
                entry = ctk.CTkEntry(kernel_frame, width=45, justify='center')
                entry.insert(0, str(default_kernel[i*3 + j]))
                entry.grid(row=i, column=j, padx=2, pady=2)
                self.kernel_entries.append(entry)

        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Terapkan Konvolusi", command=self.commit_convolution, fg_color="#059669", hover_color="#047857").pack(fill="x", padx=10, pady=10)
        
        presets_frame = ctk.CTkFrame(self.dynamic_controls_frame, fg_color="transparent")
        presets_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(presets_frame, text="Presets:").pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(presets_frame, text="Blur", command=lambda: self._load_kernel([1/9]*9), width=70).pack(side="left", padx=5)
        ctk.CTkButton(presets_frame, text="Sharpen", command=lambda: self._load_kernel([0, -1, 0, -1, 5, -1, 0, -1, 0]), width=70).pack(side="left", padx=5)
        ctk.CTkButton(presets_frame, text="Edge", command=lambda: self._load_kernel([-1, -1, -1, -1, 8, -1, -1, -1, -1]), width=70).pack(side="left", padx=5)

    def setup_gamma_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        
        ctk.CTkLabel(self.dynamic_controls_frame, text="☀️ Gamma Correction", font=ctk.CTkFont(size=16, weight="bold"), text_color="#A78BFA").pack(pady=(10, 5))
        
        gf, self.gamma_slider = self._create_slider_set(self.dynamic_controls_frame, "Gamma (γ)", 0.1, 5.0, 1.0, "{:.2f}", self.preview_gamma)
        self.gamma_value_label = gf.winfo_children()[2] # Simpan referensi label nilai
        gf.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Terapkan Gamma", command=self.commit_gamma, fg_color="#059669", hover_color="#047857").pack(fill="x", padx=10, pady=15)
        
    def setup_ilpf_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        
        ctk.CTkLabel(self.dynamic_controls_frame, text="Ideal Lowpass Filter (ILPF)", font=ctk.CTkFont(size=16, weight="bold"), text_color="#A78BFA").pack(pady=(10, 5))
        
        H, W = self.processed_image.shape[:2]
        D_max = np.sqrt((H/2)**2 + (W/2)**2)
        
        df, self.ilpf_d0_slider = self._create_slider_set(self.dynamic_controls_frame, "Cutoff (D0)", 1, int(D_max), int(D_max/4), "{:.0f}", self.preview_ilpf)
        self.ilpf_d0_value_label = df.winfo_children()[2] # Simpan referensi label nilai
        df.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Apply ILPF", command=self.commit_ilpf, fg_color="#059669", hover_color="#047857").pack(fill="x", padx=10, pady=15)

    def setup_blpf_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        
        ctk.CTkLabel(self.dynamic_controls_frame, text="Butterworth Lowpass Filter (BLPF)", font=ctk.CTkFont(size=16, weight="bold"), text_color="#A78BFA").pack(pady=(10, 5))
        
        H, W = self.processed_image.shape[:2]
        D_max = np.sqrt((H/2)**2 + (W/2)**2)
        
        df, self.blpf_d0_slider = self._create_slider_set(self.dynamic_controls_frame, "Cutoff (D0)", 1, int(D_max), int(D_max/4), "{:.0f}", self.preview_blpf)
        self.blpf_d0_value_label = df.winfo_children()[2]
        df.pack(fill="x", padx=10, pady=5)

        nf, self.blpf_n_slider = self._create_slider_set(self.dynamic_controls_frame, "Order (n)", 1, 10, 2, "{:.0f}", self.preview_blpf)
        self.blpf_n_value_label = nf.winfo_children()[2]
        nf.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Apply BLPF", command=self.commit_blpf, fg_color="#059669", hover_color="#047857").pack(fill="x", padx=10, pady=15)
        
    def setup_ihpf_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        
        ctk.CTkLabel(self.dynamic_controls_frame, text="Ideal Highpass Filter (IHPF)", font=ctk.CTkFont(size=16, weight="bold"), text_color="#A78BFA").pack(pady=(10, 5))
        
        H, W = self.processed_image.shape[:2]
        D_max = np.sqrt((H/2)**2 + (W/2)**2)
        
        df, self.ihpf_d0_slider = self._create_slider_set(self.dynamic_controls_frame, "Cutoff (D0)", 1, int(D_max), int(D_max/4), "{:.0f}", self.preview_ihpf)
        self.ihpf_d0_value_label = df.winfo_children()[2] # Simpan referensi label nilai
        df.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Apply IHPF", command=self.commit_ihpf, fg_color="#059669", hover_color="#047857").pack(fill="x", padx=10, pady=15)
    
    def setup_bhpf_controls(self):
        if self.processed_image is None: return
        self.clear_dynamic_controls()
        
        ctk.CTkLabel(self.dynamic_controls_frame, text="Butterworth Highpass Filter (BHPF)", font=ctk.CTkFont(size=16, weight="bold"), text_color="#A78BFA").pack(pady=(10, 5))
        
        H, W = self.processed_image.shape[:2]
        D_max = np.sqrt((H/2)**2 + (W/2)**2)
        
        df, self.bhpf_d0_slider = self._create_slider_set(self.dynamic_controls_frame, "Cutoff (D0)", 1, int(D_max), int(D_max/4), "{:.0f}", self.preview_bhpf)
        self.bhpf_d0_value_label = df.winfo_children()[2]
        df.pack(fill="x", padx=10, pady=5)

        nf, self.bhpf_n_slider = self._create_slider_set(self.dynamic_controls_frame, "Order (n)", 1, 10, 2, "{:.0f}", self.preview_bhpf)
        self.bhpf_n_value_label = nf.winfo_children()[2]
        nf.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(self.dynamic_controls_frame, text="✅ Apply BHPF", command=self.commit_bhpf, fg_color="#059669", hover_color="#047857").pack(fill="x", padx=10, pady=15)

    # ========================= LOGIKA PREVIEW & COMMIT (SEMUA SLIDER DIPERBAIKI) ========================= #
    
    # 1. Preview Brightness & Contrast (Multi-slider) - FIXED
    def preview_brightness_contrast(self, value, value_label, format_str):
        if self.temp_image_for_preview is None: return
        
        # Ambil nilai dari kedua slider
        b_val = self.brightness_slider.get() 
        c_val = self.contrast_slider.get()
        
        # Perbarui label yang digeser
        value_label.configure(text=format_str.format(value))
        
        # Perbarui label slider pasangannya
        if value_label == self.brightness_value_label:
            # Update contrast label's text (using its own format string)
            self.contrast_value_label.configure(text=f"{c_val:.2f}")
        elif value_label == self.contrast_value_label:
            # Update brightness label's text (using its own format string)
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
        
        # Perbarui label yang sedang digeser
        value_label.configure(text=format_str.format(value))
        
        # Perbarui label slider lainnya
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
        
        # Perbarui label yang digeser
        value_label.configure(text=format_str.format(value))
        
        # Perbarui label slider pasangannya
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
        
    # ========================= FUNGSI UTAMA (IO, History, dll.) ========================= #
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
        h, w = cv2_image.shape[:2]
        aspect_ratio = w / h
        if w > self.IMAGE_WIDTH or h > self.IMAGE_HEIGHT:
            if aspect_ratio > 1: new_w, new_h = self.IMAGE_WIDTH, int(self.IMAGE_WIDTH / aspect_ratio)
            else: new_w, new_h = int(self.IMAGE_HEIGHT * aspect_ratio), self.IMAGE_HEIGHT
        else: new_w, new_h = w, h
        
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
            self.history.append(self.processed_image.copy())
            self.processed_image = filter_func(self.processed_image.copy(), *args)
            self.display_image(self.processed_image, self.processed_image_label)
            self.redo_stack.clear()
            self.update_button_states()
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan saat menerapkan filter: {e}")
            if self.history: self.processed_image = self.history.pop()
            
    def update_button_states(self):
        self.undo_button.configure(state="normal" if self.history else "disabled")
        self.redo_button.configure(state="normal" if self.redo_stack else "disabled")
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
            self.update_button_states()
            self.clear_dynamic_controls()
            
    def save_image(self):
        if self.processed_image is None: return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
        if path:
            cv2.imwrite(path, self.processed_image)
            messagebox.showinfo("Sukses", f"Gambar disimpan di:\n{path}")
            
    def show_dev_info(self):
        info_text = (
            "Aplikasi ini dikembangkan oleh: Ariasyah Ramadhan\n"
            "- Tim Anda\n"
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
        
    # ========================= FUNGSI PEMROSESAN GAMBAR (INTI ASLI) ========================= #
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
    # Mengganti fungsi geometrics yang tidak digunakan
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
        self.apply_filter(lambda img: self._add_noise_to_image(img, uniform_noise_generator))
    def add_uniform_noise(self):
        def uniform_noise_generator(shape, low=-0.1, high=0.1):
            return np.random.uniform(low, high, size=shape)
        self.apply_filter(lambda img: self._add_noise_to_image(img, uniform_noise_generator))
        
    # ========================= FUNGSI BANTUAN DOMAIN FREKUENSI (ASLI) ========================= #
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