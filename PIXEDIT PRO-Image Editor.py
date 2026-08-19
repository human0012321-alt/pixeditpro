"""
PixEdit Pro - Image Editor with AI Features
A Comprehensive Image Processing Application
Class XII Computer Science Project
"""

import tkinter as tk
from tkinter import filedialog, messagebox, Scale, HORIZONTAL, VERTICAL, ttk, simpledialog, colorchooser
try:
    from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Pillow (PIL) is not installed. Please install it using: pip install Pillow")
    exit(1)

import os
import numpy as np
import math
import random
from collections import Counter

# ============= COLOR SCHEME =============
COLORS = {
    'bg_dark': '#1a1a2e',
    'bg_medium': '#16213e',
    'bg_light': '#0f3460',
    'bg_button': '#1a1a40',
    'bg_button_hover': '#e94560',
    'bg_toolbar': '#0a0a1a',
    'bg_panel': '#1a2a4a',
    'text_primary': '#ffffff',
    'text_secondary': '#a8d8ea',
    'text_accent': '#e94560',
    'text_heading': '#00d4ff',
    'text_label': '#ffffff',
    'text_value': '#ff6b81',
    'accent': '#e94560',
    'accent_light': '#ff6b81',
    'accent_dark': '#c0392b',
    'accent_cyan': '#00d4ff',
    'border': '#2a2a4a',
    'success': '#2ecc71',
    'warning': '#f39c12',
    'error': '#e74c3c',
    'highlight': '#e94560',
    'selection': '#e94560',
    'ai_glow': '#9b59b6',
}

# ============= AI HELPER CLASS =============

class AIImageProcessor:
    """AI-powered image processing utilities - Optimized and robust"""

    @staticmethod
    def smart_enhance(image):
        try:
            img = image.copy()
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img_array = np.array(img, dtype=np.float64)
            mean_brightness = np.mean(img_array)
            std_brightness = np.std(img_array)

            if std_brightness < 40:
                contrast = 1.3
            elif std_brightness > 80:
                contrast = 0.9
            else:
                contrast = 1.1
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast)

            if mean_brightness < 100:
                brightness = 1.2
            elif mean_brightness > 180:
                brightness = 0.85
            else:
                brightness = 1.0
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(brightness)

            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.1)
            return img
        except Exception as e:
            print(f"Smart Enhance error: {e}")
            return image

    @staticmethod
    def remove_background(image):
        """AI-powered background removal - fixed overflow and improved robustness"""
        try:
            img = image.copy()
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            width, height = img.size
            # If image is too large, resize for processing
            if width * height > 1024 * 1024:
                scale = min(1024 / width, 1024 / height)
                new_size = (int(width * scale), int(height * scale))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                width, height = new_size

            data = np.array(img, dtype=np.uint8)

            # Get corner colors - convert to Python int to avoid overflow
            corners = [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)]
            corner_colors = []
            for x, y in corners:
                # Use Python ints for safe subtraction
                r = int(data[y, x, 0])
                g = int(data[y, x, 1])
                b = int(data[y, x, 2])
                corner_colors.append((r, g, b))

            # Find the most common corner color
            bg_color = Counter(corner_colors).most_common(1)[0][0]

            # Create mask using a fast pixel loop with Python ints
            mask = np.zeros((height, width), dtype=np.uint8)
            tolerance = 30
            bg_r, bg_g, bg_b = bg_color

            for y in range(height):
                for x in range(width):
                    # Convert to Python ints before subtraction
                    r = int(data[y, x, 0])
                    g = int(data[y, x, 1])
                    b = int(data[y, x, 2])
                    if (abs(r - bg_r) < tolerance and
                        abs(g - bg_g) < tolerance and
                        abs(b - bg_b) < tolerance):
                        mask[y, x] = 255

            # Apply mask: set alpha to 0 where mask is 255
            data[mask == 255, 3] = 0
            result = Image.fromarray(data)

            # If we resized, scale back to original size
            if result.size != image.size:
                result = result.resize(image.size, Image.Resampling.LANCZOS)
            return result
        except Exception as e:
            print(f"Background removal error: {e}")
            return image

    @staticmethod
    def style_transfer_simple(image, style='oil'):
        try:
            img = image.copy()
            if img.mode != 'RGB':
                img = img.convert('RGB')
            if style == 'oil':
                img = img.filter(ImageFilter.MedianFilter(5))
                img = img.filter(ImageFilter.SHARPEN)
            elif style == 'watercolor':
                img = img.filter(ImageFilter.CONTOUR)
                img = ImageEnhance.Brightness(img).enhance(1.2)
            elif style == 'sketch':
                img = img.convert('L')
                img = ImageOps.invert(img)
                img = img.filter(ImageFilter.GaussianBlur(1))
                img = ImageOps.invert(img)
                img = img.convert('RGB')
            elif style == 'pop_art':
                img = ImageEnhance.Color(img).enhance(2.0)
                img = ImageEnhance.Contrast(img).enhance(1.5)
                img = img.point(lambda p: 255 if p > 128 else 0)
            elif style == 'impressionist':
                img = img.filter(ImageFilter.GaussianBlur(2))
                img = ImageEnhance.Color(img).enhance(1.5)
                img = ImageEnhance.Sharpness(img).enhance(1.5)
            return img
        except Exception as e:
            print(f"Style transfer error: {e}")
            return image

    @staticmethod
    def upscale_image(image, factor=2):
        try:
            if factor < 2 or factor > 3:
                factor = 2
            new_size = (image.width * factor, image.height * factor)
            upscaled = image.resize(new_size, Image.Resampling.LANCZOS)
            upscaled = upscaled.filter(ImageFilter.UnsharpMask(radius=1, percent=50, threshold=2))
            return upscaled
        except Exception as e:
            print(f"Upscale error: {e}")
            return image

    @staticmethod
    def colorize_grayscale(image):
        try:
            if image.mode != 'L':
                image = image.convert('L')
            width, height = image.size
            result = Image.new('RGB', (width, height))
            for y in range(height):
                for x in range(width):
                    intensity = image.getpixel((x, y))
                    if intensity < 64:
                        r, g, b = 50, 50, 150
                    elif intensity < 128:
                        r, g, b = 100, 150, 200
                    elif intensity < 192:
                        r, g, b = 200, 180, 100
                    else:
                        r, g, b = 240, 220, 200
                    result.putpixel((x, y), (r, g, b))
            return result
        except Exception as e:
            print(f"Colorize error: {e}")
            return image

    @staticmethod
    def enhance_face(image):
        try:
            img = image.copy()
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img = img.filter(ImageFilter.GaussianBlur(radius=1))
            img = ImageEnhance.Sharpness(img).enhance(1.3)
            img = ImageEnhance.Brightness(img).enhance(1.1)
            img = ImageEnhance.Contrast(img).enhance(1.2)
            return img
        except Exception as e:
            print(f"Face enhance error: {e}")
            return image

    @staticmethod
    def denoise_image(image):
        try:
            img = image.copy()
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img = img.filter(ImageFilter.MedianFilter(3))
            img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
            img = img.filter(ImageFilter.SHARPEN)
            return img
        except Exception as e:
            print(f"Denoise error: {e}")
            return image

    @staticmethod
    def auto_crop(image):
        try:
            img = image.copy()
            if img.mode != 'RGB':
                img = img.convert('RGB')
            data = np.array(img, dtype=np.uint8)
            non_empty = np.where(np.sum(data, axis=2) > 30)
            if len(non_empty[0]) > 0 and len(non_empty[1]) > 0:
                top = np.min(non_empty[0])
                bottom = np.max(non_empty[0])
                left = np.min(non_empty[1])
                right = np.max(non_empty[1])
                margin = 5
                top = max(0, top - margin)
                bottom = min(img.height, bottom + margin)
                left = max(0, left - margin)
                right = min(img.width, right + margin)
                img = img.crop((left, top, right, bottom))
            return img
        except Exception as e:
            print(f"Auto crop error: {e}")
            return image

    @staticmethod
    def generate_art(image, style='abstract'):
        try:
            img = image.copy()
            if img.mode != 'RGB':
                img = img.convert('RGB')
            width, height = img.size

            if style == 'abstract':
                draw = ImageDraw.Draw(img)
                for _ in range(10):
                    x = random.randint(0, width - 1)
                    y = random.randint(0, height - 1)
                    radius = random.randint(5, 20)
                    color = tuple(random.randint(0, 255) for _ in range(3))
                    draw.ellipse([x - radius, y - radius, x + radius, y + radius],
                                 fill=color, outline=color)
                img = Image.blend(image, img, 0.5)

            elif style == 'mosaic':
                block = 20
                for y in range(0, height, block):
                    for x in range(0, width, block):
                        box = (x, y, min(x + block, width), min(y + block, height))
                        region = image.crop(box)
                        if region.size[0] > 0 and region.size[1] > 0:
                            arr = np.array(region)
                            avg = tuple(map(int, np.mean(arr, axis=(0, 1))))
                            draw = ImageDraw.Draw(img)
                            draw.rectangle(box, fill=avg)

            elif style == 'glitch':
                data = np.array(img)
                for y in range(height):
                    if random.random() < 0.1:
                        shift = random.randint(-20, 20)
                        if shift > 0:
                            data[y, shift:] = data[y, :-shift]
                        elif shift < 0:
                            data[y, :shift] = data[y, -shift:]
                img = Image.fromarray(data)

            return img
        except Exception as e:
            print(f"Art generation error: {e}")
            return image

# ============= MAIN APPLICATION =============

class PixEditPro:
    def __init__(self, root):
        if not PIL_AVAILABLE:
            messagebox.showerror("Error", "Pillow library is required. Please install it using: pip install Pillow")
            root.destroy()
            return

        self.root = root
        self.root.title("PixEdit Pro - AI Image Editor")
        self.root.geometry("1500x950")
        self.root.configure(bg=COLORS['bg_medium'])

        # Application state
        self.original_image = None
        self.current_image = None
        self.filename = None
        self.history = []
        self.history_index = -1
        self.max_history = 50
        self.zoom_factor = 1.0
        self.is_processing = False

        # Layer system
        self.layers = []
        self.active_layer_index = 0

        # Tool states
        self.current_tool = "select"
        self.brush_size = 10
        self.brush_color = "#ffffff"
        self.drawing = False
        self.last_x = 0
        self.last_y = 0
        self.blend_mode = "Normal"

        # Selection state
        self.selection_start = None
        self.selection_end = None
        self.selection_rect = None
        self.copied_image = None

        # Tool buttons
        self.tool_buttons = {}

        # Slider variables and labels
        self.slider_vars = {}
        self.slider_labels = {}

        # AI Processor
        self.ai_processor = AIImageProcessor()

        # Setup UI
        self.style = ttk.Style()
        self.setup_styles()
        self.setup_ui()
        self.setup_keyboard_shortcuts()

        self.status_label.config(text="🤖 Welcome to PixEdit Pro AI! Open an image to start editing.")

    def setup_styles(self):
        self.style.configure('TFrame', background=COLORS['bg_medium'])
        self.style.configure('TLabel', background=COLORS['bg_medium'], foreground=COLORS['text_primary'])
        self.style.configure('TButton', background=COLORS['bg_button'], foreground=COLORS['text_primary'])
        self.style.configure('TCanvas', background=COLORS['bg_dark'])
        self.style.configure('TLabelframe', background=COLORS['bg_panel'], foreground=COLORS['text_heading'])
        self.style.configure('TLabelframe.Label', background=COLORS['bg_panel'], foreground=COLORS['text_heading'])
        self.style.configure('TNotebook', background=COLORS['bg_medium'])
        self.style.configure('TNotebook.Tab', background=COLORS['bg_button'], foreground=COLORS['text_primary'])
        self.style.configure('TEntry', fieldbackground=COLORS['bg_light'], foreground=COLORS['text_primary'])
        self.style.configure('TSpinbox', fieldbackground=COLORS['bg_light'], foreground=COLORS['text_primary'])
        self.style.configure('TScale', background=COLORS['bg_medium'], troughcolor=COLORS['bg_light'])

        self.style.map('TNotebook.Tab',
            background=[('selected', COLORS['bg_button_hover']), ('active', COLORS['accent_light'])],
            foreground=[('selected', COLORS['text_primary']), ('active', COLORS['text_primary'])])

    def setup_keyboard_shortcuts(self):
        """Set up all keyboard shortcuts - works globally regardless of focus"""
        # ---- Override default widget bindings so they don't block our shortcuts ----
        # These classes have default bindings that consume Ctrl+Z, Ctrl+C, etc.
        for widget_class in ('Entry', 'Text', 'Spinbox', 'Combobox'):
            # Override Edit shortcuts (prevent default behavior)
            self.root.bind_class(widget_class, '<Control-z>', lambda e: "break")
            self.root.bind_class(widget_class, '<Control-y>', lambda e: "break")
            self.root.bind_class(widget_class, '<Control-c>', lambda e: "break")
            self.root.bind_class(widget_class, '<Control-v>', lambda e: "break")
            self.root.bind_class(widget_class, '<Control-x>', lambda e: "break")
            # Override tool shortcut keys so they don't get typed into the widget
            self.root.bind_class(widget_class, 'v', lambda e: "break")
            self.root.bind_class(widget_class, 'b', lambda e: "break")
            self.root.bind_class(widget_class, 'e', lambda e: "break")
            self.root.bind_class(widget_class, 't', lambda e: "break")
            self.root.bind_class(widget_class, 'c', lambda e: "break")
            self.root.bind_class(widget_class, 'w', lambda e: "break")
            self.root.bind_class(widget_class, 'g', lambda e: "break")

        # ---- Now bind our own shortcuts globally ----
        # File operations
        self.root.bind_all('<Control-n>', lambda e: self.new_file())
        self.root.bind_all('<Control-o>', lambda e: self.open_image())
        self.root.bind_all('<Control-s>', lambda e: self.save_image())
        self.root.bind_all('<Control-Shift-S>', lambda e: self.save_image_as())
        self.root.bind_all('<Control-q>', lambda e: self.root.quit())

        # Edit operations (prevent default behavior with "break")
        self.root.bind_all('<Control-z>', lambda e: self.undo() or "break")
        self.root.bind_all('<Control-y>', lambda e: self.redo() or "break")
        self.root.bind_all('<Control-c>', lambda e: self.copy_selection() or "break")
        self.root.bind_all('<Control-v>', lambda e: self.paste_selection() or "break")
        self.root.bind_all('<Control-x>', lambda e: self.cut_selection() or "break")

        # Tool shortcuts
        self.root.bind_all('v', lambda e: self.set_tool('select'))
        self.root.bind_all('b', lambda e: self.set_tool('brush'))
        self.root.bind_all('e', lambda e: self.set_tool('eraser'))
        self.root.bind_all('t', lambda e: self.set_tool('text'))
        self.root.bind_all('c', lambda e: self.set_tool('crop'))
        self.root.bind_all('w', lambda e: self.set_tool('magic_wand'))
        self.root.bind_all('g', lambda e: self.set_tool('gradient'))

        # Zoom shortcuts
        self.root.bind_all('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind_all('<Control-equal>', lambda e: self.zoom_in())
        self.root.bind_all('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind_all('<Control-0>', lambda e: self.fit_to_screen())

    def setup_ui(self):
        self.setup_menu()

        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.setup_top_toolbar(main_container)
        self.setup_left_toolbar(main_container)
        self.setup_workspace(main_container)
        self.setup_properties_panel(main_container)
        self.setup_status_bar()

    def setup_menu(self):
        menubar = tk.Menu(self.root, bg=COLORS['bg_medium'], fg=COLORS['text_primary'],
                         activebackground=COLORS['bg_button_hover'],
                         activeforeground=COLORS['text_primary'])
        self.root.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=COLORS['bg_medium'], fg=COLORS['text_primary'],
                           activebackground=COLORS['bg_button_hover'],
                           activeforeground=COLORS['text_primary'])
        menubar.add_cascade(label="📁 File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_image, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_image, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_image_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Export as PNG", command=lambda: self.export_image("png"))
        file_menu.add_command(label="Export as JPG", command=lambda: self.export_image("jpg"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")

        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg=COLORS['bg_medium'], fg=COLORS['text_primary'],
                           activebackground=COLORS['bg_button_hover'],
                           activeforeground=COLORS['text_primary'])
        menubar.add_cascade(label="✏️ Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Copy", command=self.copy_selection, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste_selection, accelerator="Ctrl+V")
        edit_menu.add_command(label="Cut", command=self.cut_selection, accelerator="Ctrl+X")

        # Image Menu
        image_menu = tk.Menu(menubar, tearoff=0, bg=COLORS['bg_medium'], fg=COLORS['text_primary'],
                            activebackground=COLORS['bg_button_hover'],
                            activeforeground=COLORS['text_primary'])
        menubar.add_cascade(label="🖼️ Image", menu=image_menu)
        image_menu.add_command(label="Resize", command=self.resize_image)
        image_menu.add_separator()
        image_menu.add_command(label="Rotate 90° CW", command=lambda: self.rotate_image(90))
        image_menu.add_command(label="Rotate 180°", command=lambda: self.rotate_image(180))
        image_menu.add_command(label="Rotate 90° CCW", command=lambda: self.rotate_image(-90))
        image_menu.add_separator()
        image_menu.add_command(label="Flip Horizontal", command=self.flip_horizontal)
        image_menu.add_command(label="Flip Vertical", command=self.flip_vertical)

        # Filter Menu
        filter_menu = tk.Menu(menubar, tearoff=0, bg=COLORS['bg_medium'], fg=COLORS['text_primary'],
                             activebackground=COLORS['bg_button_hover'],
                             activeforeground=COLORS['text_primary'])
        menubar.add_cascade(label="✨ Filter", menu=filter_menu)

        blur_menu = tk.Menu(filter_menu, tearoff=0, bg=COLORS['bg_medium'], fg=COLORS['text_primary'])
        filter_menu.add_cascade(label="Blur", menu=blur_menu)
        blur_menu.add_command(label="Gaussian Blur", command=lambda: self.apply_blur(5))
        blur_menu.add_command(label="Box Blur", command=lambda: self.apply_filter(ImageFilter.BoxBlur(5)))
        blur_menu.add_command(label="Motion Blur", command=self.apply_motion_blur)
        blur_menu.add_command(label="Median Filter (Noise Reduction)", command=self.apply_median_filter)

        sharpen_menu = tk.Menu(filter_menu, tearoff=0, bg=COLORS['bg_medium'], fg=COLORS['text_primary'])
        filter_menu.add_cascade(label="Sharpen", menu=sharpen_menu)
        sharpen_menu.add_command(label="Sharpen", command=lambda: self.apply_filter(ImageFilter.SHARPEN))
        sharpen_menu.add_command(label="Unsharp Mask", command=self.apply_unsharp_mask)

        artistic_menu = tk.Menu(filter_menu, tearoff=0, bg=COLORS['bg_medium'], fg=COLORS['text_primary'])
        filter_menu.add_cascade(label="Artistic", menu=artistic_menu)
        artistic_menu.add_command(label="Oil Paint", command=self.apply_oil_paint)
        artistic_menu.add_command(label="Watercolor", command=self.apply_watercolor)
        artistic_menu.add_command(label="Sketch", command=self.apply_sketch)
        artistic_menu.add_command(label="Emboss", command=self.apply_emboss)
        artistic_menu.add_command(label="Edge Detection", command=self.apply_edge_detection)
        artistic_menu.add_command(label="Pixelate", command=self.apply_pixelate)

        # AI Menu
        ai_menu = tk.Menu(menubar, tearoff=0, bg=COLORS['bg_medium'], fg=COLORS['text_primary'],
                         activebackground=COLORS['bg_button_hover'],
                         activeforeground=COLORS['text_primary'])
        menubar.add_cascade(label="🤖 AI", menu=ai_menu)
        ai_menu.add_command(label="Smart Enhance", command=self.ai_smart_enhance)
        ai_menu.add_command(label="Remove Background", command=self.ai_remove_background)
        ai_menu.add_separator()
        ai_menu.add_command(label="Oil Painting Style", command=lambda: self.ai_style_transfer('oil'))
        ai_menu.add_command(label="Watercolor Style", command=lambda: self.ai_style_transfer('watercolor'))
        ai_menu.add_command(label="Sketch Style", command=lambda: self.ai_style_transfer('sketch'))
        ai_menu.add_command(label="Pop Art Style", command=lambda: self.ai_style_transfer('pop_art'))
        ai_menu.add_command(label="Impressionist Style", command=lambda: self.ai_style_transfer('impressionist'))
        ai_menu.add_separator()
        ai_menu.add_command(label="AI Upscale (2x)", command=self.ai_upscale)
        ai_menu.add_command(label="AI Colorize", command=self.ai_colorize)
        ai_menu.add_command(label="AI Denoise", command=self.ai_denoise)
        ai_menu.add_command(label="AI Auto Crop", command=self.ai_auto_crop)
        ai_menu.add_command(label="AI Enhance Face", command=self.ai_enhance_face)
        ai_menu.add_separator()
        ai_menu.add_command(label="Generate Abstract Art", command=lambda: self.ai_generate_art('abstract'))
        ai_menu.add_command(label="Generate Mosaic Art", command=lambda: self.ai_generate_art('mosaic'))
        ai_menu.add_command(label="Generate Glitch Art", command=lambda: self.ai_generate_art('glitch'))

        # Layer Menu
        layer_menu = tk.Menu(menubar, tearoff=0, bg=COLORS['bg_medium'], fg=COLORS['text_primary'],
                            activebackground=COLORS['bg_button_hover'],
                            activeforeground=COLORS['text_primary'])
        menubar.add_cascade(label="📐 Layer", menu=layer_menu)
        layer_menu.add_command(label="New Layer", command=self.new_layer)
        layer_menu.add_command(label="Duplicate Layer", command=self.duplicate_layer)
        layer_menu.add_command(label="Delete Layer", command=self.delete_layer)
        layer_menu.add_separator()
        layer_menu.add_command(label="Merge Layers", command=self.merge_layers)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=COLORS['bg_medium'], fg=COLORS['text_primary'],
                           activebackground=COLORS['bg_button_hover'],
                           activeforeground=COLORS['text_primary'])
        menubar.add_cascade(label="❓ Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)

    def setup_top_toolbar(self, parent):
        toolbar_frame = tk.Frame(parent, bg=COLORS['bg_toolbar'], height=50)
        toolbar_frame.pack(fill=tk.X, pady=(0, 5))
        toolbar_frame.pack_propagate(False)

        toolbar = tk.Frame(toolbar_frame, bg=COLORS['bg_toolbar'])
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        tools = [
            ("🔍", "select", "Selection Tool (V)"),
            ("✏️", "brush", "Brush Tool (B)"),
            ("🧽", "eraser", "Eraser Tool (E)"),
            ("🅰️", "text", "Text Tool (T)"),
            ("✂️", "crop", "Crop Tool (C)"),
            ("✨", "magic_wand", "Magic Wand (W)"),
            ("⬇️", "gradient", "Gradient Tool (G)")
        ]

        for icon, tool, tip in tools:
            btn = tk.Button(toolbar, text=icon,
                           command=lambda t=tool: self.set_tool(t),
                           bg=COLORS['bg_button'], fg=COLORS['text_primary'],
                           relief=tk.RAISED, padx=8, pady=4,
                           font=('Arial', 11),
                           activebackground=COLORS['bg_button_hover'],
                           activeforeground=COLORS['text_primary'],
                           bd=2, cursor='hand2')
            btn.pack(side=tk.LEFT, padx=3)
            self.tool_buttons[tool] = btn
            self.create_tooltip(btn, tip)

        tk.Frame(toolbar, bg=COLORS['border'], width=2, height=30).pack(side=tk.LEFT, padx=10)

        # Brush Size
        size_label = tk.Label(toolbar, text="Size:", bg=COLORS['bg_toolbar'],
                             fg=COLORS['text_secondary'], font=('Arial', 10, 'bold'))
        size_label.pack(side=tk.LEFT, padx=(5, 2))

        self.brush_size_var = tk.IntVar(value=self.brush_size)
        brush_spin = tk.Spinbox(toolbar, from_=1, to=100, width=5,
                                textvariable=self.brush_size_var,
                                command=self.update_brush_size,
                                bg=COLORS['bg_light'], fg=COLORS['text_primary'],
                                relief=tk.FLAT, bd=2,
                                font=('Arial', 10))
        brush_spin.pack(side=tk.LEFT, padx=2)

        tk.Frame(toolbar, bg=COLORS['border'], width=2, height=30).pack(side=tk.LEFT, padx=10)

        # Color Picker
        self.color_btn = tk.Button(toolbar, text="🎨", command=self.choose_color,
                                  bg=COLORS['bg_button'], fg=COLORS['text_primary'],
                                  relief=tk.RAISED, padx=8, pady=4,
                                  activebackground=COLORS['bg_button_hover'],
                                  activeforeground=COLORS['text_primary'],
                                  bd=2, cursor='hand2')
        self.color_btn.pack(side=tk.LEFT, padx=3)
        self.create_tooltip(self.color_btn, "Choose Color")

        self.color_preview = tk.Canvas(toolbar, width=24, height=24,
                                      bg=COLORS['bg_button'],
                                      highlightthickness=2,
                                      highlightbackground=COLORS['border'])
        self.color_preview.pack(side=tk.LEFT, padx=3)
        self.update_color_preview()

        tk.Frame(toolbar, bg=COLORS['border'], width=2, height=30).pack(side=tk.LEFT, padx=10)

        # Opacity
        op_label = tk.Label(toolbar, text="Opacity:", bg=COLORS['bg_toolbar'],
                           fg=COLORS['text_secondary'], font=('Arial', 10, 'bold'))
        op_label.pack(side=tk.LEFT, padx=(5, 2))

        self.opacity_var = tk.IntVar(value=100)
        opacity_scale = tk.Scale(toolbar, from_=1, to=100, variable=self.opacity_var,
                                orient=tk.HORIZONTAL, length=80,
                                bg=COLORS['bg_toolbar'], fg=COLORS['text_primary'],
                                troughcolor=COLORS['bg_light'],
                                highlightthickness=0, bd=0,
                                sliderlength=15)
        opacity_scale.pack(side=tk.LEFT, padx=5)

        tk.Frame(toolbar, bg=COLORS['border'], width=2, height=30).pack(side=tk.LEFT, padx=10)

        # Zoom Controls
        zoom_label = tk.Label(toolbar, text="Zoom:", bg=COLORS['bg_toolbar'],
                             fg=COLORS['text_secondary'], font=('Arial', 10, 'bold'))
        zoom_label.pack(side=tk.LEFT, padx=(5, 2))

        for text, cmd in [("＋", self.zoom_in), ("－", self.zoom_out), ("⬜", self.fit_to_screen)]:
            btn = tk.Button(toolbar, text=text, command=cmd, width=3,
                           bg=COLORS['bg_button'], fg=COLORS['text_primary'],
                           activebackground=COLORS['bg_button_hover'],
                           activeforeground=COLORS['text_primary'],
                           relief=tk.RAISED, bd=2, cursor='hand2',
                           font=('Arial', 10, 'bold'))
            btn.pack(side=tk.LEFT, padx=2)
            self.create_tooltip(btn, text)

        # Blend Mode
        tk.Frame(toolbar, bg=COLORS['border'], width=2, height=30).pack(side=tk.LEFT, padx=10)

        blend_label = tk.Label(toolbar, text="Blend:", bg=COLORS['bg_toolbar'],
                              fg=COLORS['text_secondary'], font=('Arial', 10, 'bold'))
        blend_label.pack(side=tk.LEFT, padx=(5, 2))

        self.blend_var = tk.StringVar(value="Normal")
        blend_combo = ttk.Combobox(toolbar, textvariable=self.blend_var,
                                  values=["Normal", "Multiply", "Screen", "Overlay", "Darken", "Lighten"],
                                  state="readonly", width=8)
        blend_combo.pack(side=tk.LEFT, padx=2)
        blend_combo.bind('<<ComboboxSelected>>', self.on_blend_change)

        # AI Quick Actions
        tk.Frame(toolbar, bg=COLORS['border'], width=2, height=30).pack(side=tk.LEFT, padx=10)

        ai_label = tk.Label(toolbar, text="🤖 AI:", bg=COLORS['bg_toolbar'],
                           fg=COLORS['accent_cyan'], font=('Arial', 10, 'bold'))
        ai_label.pack(side=tk.LEFT, padx=(5, 2))

        for text, cmd in [("✨Enhance", self.ai_smart_enhance),
                         ("🎨Style", lambda: self.ai_style_transfer('oil'))]:
            btn = tk.Button(toolbar, text=text, command=cmd,
                           bg=COLORS['bg_button'], fg=COLORS['text_primary'],
                           activebackground=COLORS['bg_button_hover'],
                           activeforeground=COLORS['text_primary'],
                           relief=tk.RAISED, bd=2, cursor='hand2',
                           font=('Arial', 9, 'bold'))
            btn.pack(side=tk.LEFT, padx=2)
            self.create_tooltip(btn, text)

    def on_blend_change(self, event):
        self.blend_mode = self.blend_var.get()
        self.status_label.config(text=f"Blend Mode: {self.blend_mode}")

    def setup_left_toolbar(self, parent):
        toolbar = tk.Frame(parent, width=70, bg=COLORS['bg_dark'])
        toolbar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        toolbar.pack_propagate(False)

        tools = [
            ("📁", "File", self.show_file_panel),
            ("🎨", "Brush", self.show_brush_panel),
            ("🔄", "Adjust", self.show_adjust_panel),
            ("✨", "Filter", self.show_filter_panel),
            ("🤖", "AI", self.show_ai_panel),
            ("📐", "Layer", self.show_layer_panel),
            ("🖼️", "Image", self.show_image_panel)
        ]

        for icon, name, command in tools:
            btn = tk.Button(toolbar, text=icon, command=command, width=5,
                           bg=COLORS['bg_button'], fg=COLORS['text_primary'],
                           activebackground=COLORS['bg_button_hover'],
                           activeforeground=COLORS['text_primary'],
                           relief=tk.RAISED, bd=2, cursor='hand2',
                           font=('Arial', 14))
            btn.pack(pady=5)
            self.create_tooltip(btn, name)

    def setup_workspace(self, parent):
        workspace = tk.Frame(parent, bg=COLORS['bg_medium'])
        workspace.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        canvas_frame = tk.Frame(workspace, bg=COLORS['bg_dark'])
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg=COLORS['bg_dark'],
                               highlightthickness=2,
                               highlightbackground=COLORS['border'])

        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=VERTICAL, command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=HORIZONTAL, command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)

        self.setup_layers_panel(workspace)

    def setup_layers_panel(self, parent):
        layers_frame = tk.LabelFrame(parent, text="📐 Layers",
                                     bg=COLORS['bg_panel'],
                                     fg=COLORS['text_heading'],
                                     font=('Arial', 10, 'bold'),
                                     relief=tk.GROOVE, bd=2,
                                     height=150)
        layers_frame.pack(fill=tk.X, pady=(5, 0))
        layers_frame.pack_propagate(False)

        self.layers_listbox = tk.Listbox(layers_frame,
                                        bg=COLORS['bg_dark'],
                                        fg=COLORS['text_primary'],
                                        selectbackground=COLORS['bg_button_hover'],
                                        selectforeground=COLORS['text_primary'],
                                        borderwidth=2, relief=tk.FLAT,
                                        font=('Arial', 10))
        self.layers_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.layers_listbox.bind('<<ListboxSelect>>', self.on_layer_select)

        layer_controls = tk.Frame(layers_frame, bg=COLORS['bg_panel'])
        layer_controls.pack(fill=tk.X, padx=5, pady=5)

        for text, cmd in [("➕", self.new_layer), ("📋", self.duplicate_layer),
                          ("🗑️", self.delete_layer), ("👁️", self.toggle_layer_visibility)]:
            btn = tk.Button(layer_controls, text=text, width=3, command=cmd,
                           bg=COLORS['bg_button'], fg=COLORS['text_primary'],
                           activebackground=COLORS['bg_button_hover'],
                           activeforeground=COLORS['text_primary'],
                           relief=tk.RAISED, bd=2, cursor='hand2',
                           font=('Arial', 12))
            btn.pack(side=tk.LEFT, padx=3)
            self.create_tooltip(btn, cmd.__doc__ if cmd.__doc__ else "")

    def setup_properties_panel(self, parent):
        properties_frame = tk.Frame(parent, width=340, bg=COLORS['bg_medium'])
        properties_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        properties_frame.pack_propagate(False)

        self.notebook = ttk.Notebook(properties_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.setup_adjustments_tab()
        self.setup_filters_tab()
        self.setup_ai_tab()
        self.setup_brush_tab()
        self.setup_image_tab()

    def setup_adjustments_tab(self):
        adj_tab = ttk.Frame(self.notebook)
        self.notebook.add(adj_tab, text="🔄 Adjustments")

        # Basic adjustments
        basic_frame = tk.LabelFrame(adj_tab, text=" Basic Adjustments ",
                                   bg=COLORS['bg_panel'],
                                   fg=COLORS['text_heading'],
                                   font=('Arial', 11, 'bold'),
                                   relief=tk.GROOVE, bd=2,
                                   padx=10, pady=10)
        basic_frame.pack(fill=tk.X, pady=5, padx=5)

        adjustments = [
            ("Brightness", "brightness", 0, 2, 1.0),
            ("Contrast", "contrast", 0, 2, 1.0),
            ("Saturation", "saturation", 0, 2, 1.0),
            ("Exposure", "exposure", 0, 2, 1.0),
            ("Vibration", "vibration", 0, 2, 1.0)
        ]

        for text, var_name, from_, to, default in adjustments:
            frame = tk.Frame(basic_frame, bg=COLORS['bg_panel'])
            frame.pack(fill=tk.X, pady=5)

            label = tk.Label(frame, text=text, width=12, anchor='w',
                            bg=COLORS['bg_panel'],
                            fg=COLORS['text_primary'],
                            font=('Arial', 10, 'bold'))
            label.pack(side=tk.LEFT)

            var = tk.DoubleVar(value=default)
            self.slider_vars[var_name] = var

            scale = tk.Scale(frame, from_=from_, to=to, resolution=0.01, variable=var,
                            orient=tk.HORIZONTAL,
                            bg=COLORS['bg_panel'],
                            fg=COLORS['text_primary'],
                            troughcolor=COLORS['bg_dark'],
                            highlightthickness=0, bd=0,
                            sliderlength=15, length=150,
                            command=lambda x, n=var_name: self.apply_adjustments())
            scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

            percent_label = tk.Label(frame, text="100%", width=8,
                                    bg=COLORS['bg_panel'],
                                    fg=COLORS['accent_light'],
                                    font=('Arial', 10, 'bold'))
            percent_label.pack(side=tk.RIGHT)
            self.slider_labels[var_name] = percent_label

            def update_percent(*args, v=var, lbl=percent_label):
                value = v.get()
                percent = int((value / 2.0) * 100)
                if percent > 200:
                    percent = 200
                lbl.config(text=f"{percent}%")

            var.trace('w', update_percent)

        # Color Balance
        color_frame = tk.LabelFrame(adj_tab, text=" Color Balance ",
                                   bg=COLORS['bg_panel'],
                                   fg=COLORS['text_heading'],
                                   font=('Arial', 11, 'bold'),
                                   relief=tk.GROOVE, bd=2,
                                   padx=10, pady=10)
        color_frame.pack(fill=tk.X, pady=5, padx=5)

        color_balances = [
            ("Red", "red_balance", 0, 2, 1.0),
            ("Green", "green_balance", 0, 2, 1.0),
            ("Blue", "blue_balance", 0, 2, 1.0)
        ]

        for text, var_name, from_, to, default in color_balances:
            frame = tk.Frame(color_frame, bg=COLORS['bg_panel'])
            frame.pack(fill=tk.X, pady=3)

            label = tk.Label(frame, text=text, width=12, anchor='w',
                            bg=COLORS['bg_panel'],
                            fg=text,
                            font=('Arial', 10, 'bold'))
            label.pack(side=tk.LEFT)

            var = tk.DoubleVar(value=default)
            self.slider_vars[var_name] = var

            scale = tk.Scale(frame, from_=from_, to=to, resolution=0.01, variable=var,
                            orient=tk.HORIZONTAL,
                            bg=COLORS['bg_panel'],
                            fg=text,
                            troughcolor=COLORS['bg_dark'],
                            highlightthickness=0, bd=0,
                            sliderlength=15, length=150,
                            command=lambda x, n=var_name: self.apply_color_balance())
            scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

            percent_label = tk.Label(frame, text="100%", width=8,
                                    bg=COLORS['bg_panel'],
                                    fg=COLORS['accent_light'],
                                    font=('Arial', 10, 'bold'))
            percent_label.pack(side=tk.RIGHT)
            self.slider_labels[var_name] = percent_label

            def update_percent(*args, v=var, lbl=percent_label):
                value = v.get()
                percent = int((value / 2.0) * 100)
                if percent > 200:
                    percent = 200
                lbl.config(text=f"{percent}%")

            var.trace('w', update_percent)

        btn_frame = tk.Frame(adj_tab, bg=COLORS['bg_medium'])
        btn_frame.pack(fill=tk.X, pady=5, padx=5)

        for text, command in [("Auto Tone", self.auto_tone),
                             ("Auto Contrast", self.auto_contrast),
                             ("Auto Color", self.auto_color),
                             ("Invert", self.invert_image)]:
            btn = tk.Button(btn_frame, text=text, command=command,
                           bg=COLORS['bg_button'],
                           fg=COLORS['text_primary'],
                           activebackground=COLORS['bg_button_hover'],
                           activeforeground=COLORS['text_primary'],
                           relief=tk.RAISED, bd=2, cursor='hand2',
                           font=('Arial', 9, 'bold'))
            btn.pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)

    def setup_filters_tab(self):
        filter_tab = ttk.Frame(self.notebook)
        self.notebook.add(filter_tab, text="✨ Filters")

        # Artistic filters
        artistic_frame = tk.LabelFrame(filter_tab, text=" Artistic Effects ",
                                      bg=COLORS['bg_panel'],
                                      fg=COLORS['text_heading'],
                                      font=('Arial', 11, 'bold'),
                                      relief=tk.GROOVE, bd=2,
                                      padx=10, pady=10)
        artistic_frame.pack(fill=tk.X, pady=5, padx=5)

        for text, command in [("Oil Paint", self.apply_oil_paint),
                             ("Watercolor", self.apply_watercolor),
                             ("Sketch", self.apply_sketch),
                             ("Comic", self.apply_comic),
                             ("Posterize", self.apply_posterize),
                             ("Emboss", self.apply_emboss),
                             ("Edge Detection", self.apply_edge_detection),
                             ("Pixelate", self.apply_pixelate)]:
            btn = tk.Button(artistic_frame, text=text, command=command,
                           bg=COLORS['bg_button'],
                           fg=COLORS['text_primary'],
                           activebackground=COLORS['bg_button_hover'],
                           activeforeground=COLORS['text_primary'],
                           relief=tk.RAISED, bd=2, cursor='hand2',
                           font=('Arial', 9))
            btn.pack(fill=tk.X, pady=3)

        # Photo filters
        photo_frame = tk.LabelFrame(filter_tab, text=" Photo Effects ",
                                   bg=COLORS['bg_panel'],
                                   fg=COLORS['text_heading'],
                                   font=('Arial', 11, 'bold'),
                                   relief=tk.GROOVE, bd=2,
                                   padx=10, pady=10)
        photo_frame.pack(fill=tk.X, pady=5, padx=5)

        for text, command in [("Vintage", self.apply_vintage),
                             ("Sepia", self.apply_sepia),
                             ("B&W", self.apply_grayscale),
                             ("Cool", self.apply_cool),
                             ("Warm", self.apply_warm)]:
            btn = tk.Button(photo_frame, text=text, command=command,
                           bg=COLORS['bg_button'],
                           fg=COLORS['text_primary'],
                           activebackground=COLORS['bg_button_hover'],
                           activeforeground=COLORS['text_primary'],
                           relief=tk.RAISED, bd=2, cursor='hand2',
                           font=('Arial', 9))
            btn.pack(fill=tk.X, pady=3)

        # Blur filters
        blur_frame = tk.LabelFrame(filter_tab, text=" Blur & Sharpen ",
                                  bg=COLORS['bg_panel'],
                                  fg=COLORS['text_heading'],
                                  font=('Arial', 11, 'bold'),
                                  relief=tk.GROOVE, bd=2,
                                  padx=10, pady=10)
        blur_frame.pack(fill=tk.X, pady=5, padx=5)

        for text, command in [("Gaussian Blur", lambda: self.apply_blur(5)),
                             ("Motion Blur", self.apply_motion_blur),
                             ("Median Filter", self.apply_median_filter),
                             ("Sharpen", lambda: self.apply_filter(ImageFilter.SHARPEN)),
                             ("Unsharp Mask", self.apply_unsharp_mask)]:
            btn = tk.Button(blur_frame, text=text, command=command,
                           bg=COLORS['bg_button'],
                           fg=COLORS['text_primary'],
                           activebackground=COLORS['bg_button_hover'],
                           activeforeground=COLORS['text_primary'],
                           relief=tk.RAISED, bd=2, cursor='hand2',
                           font=('Arial', 9))
            btn.pack(fill=tk.X, pady=3)

    def setup_ai_tab(self):
        """AI Features Tab"""
        ai_tab = ttk.Frame(self.notebook)
        self.notebook.add(ai_tab, text="🤖 AI")

        # Smart Enhancements
        enhance_frame = tk.LabelFrame(ai_tab, text=" Smart Enhancements ",
                                     bg=COLORS['bg_panel'],
                                     fg=COLORS['accent_cyan'],
                                     font=('Arial', 11, 'bold'),
                                     relief=tk.GROOVE, bd=2,
                                     padx=10, pady=10)
        enhance_frame.pack(fill=tk.X, pady=5, padx=5)

        for text, command in [("✨ Smart Enhance", self.ai_smart_enhance),
                             ("🧹 Remove Background", self.ai_remove_background),
                             ("🔍 AI Upscale 2x", self.ai_upscale),
                             ("🎨 AI Colorize", self.ai_colorize),
                             ("🧊 AI Denoise", self.ai_denoise),
                             ("✂️ AI Auto Crop", self.ai_auto_crop),
                             ("💄 AI Enhance Face", self.ai_enhance_face)]:
            btn = tk.Button(enhance_frame, text=text, command=command,
                           bg=COLORS['bg_button'],
                           fg=COLORS['text_primary'],
                           activebackground=COLORS['bg_button_hover'],
                           activeforeground=COLORS['text_primary'],
                           relief=tk.RAISED, bd=2, cursor='hand2',
                           font=('Arial', 9))
            btn.pack(fill=tk.X, pady=3)

        # Style Transfer
        style_frame = tk.LabelFrame(ai_tab, text=" AI Style Transfer ",
                                   bg=COLORS['bg_panel'],
                                   fg=COLORS['accent_cyan'],
                                   font=('Arial', 11, 'bold'),
                                   relief=tk.GROOVE, bd=2,
                                   padx=10, pady=10)
        style_frame.pack(fill=tk.X, pady=5, padx=5)

        for text, style in [("🖌️ Oil Painting", 'oil'),
                           ("💧 Watercolor", 'watercolor'),
                           ("✏️ Sketch", 'sketch'),
                           ("🎭 Pop Art", 'pop_art'),
                           ("🎨 Impressionist", 'impressionist')]:
            btn = tk.Button(style_frame, text=text,
                           command=lambda s=style: self.ai_style_transfer(s),
                           bg=COLORS['bg_button'],
                           fg=COLORS['text_primary'],
                           activebackground=COLORS['bg_button_hover'],
                           activeforeground=COLORS['text_primary'],
                           relief=tk.RAISED, bd=2, cursor='hand2',
                           font=('Arial', 9))
            btn.pack(fill=tk.X, pady=3)

        # AI Art Generation
        art_frame = tk.LabelFrame(ai_tab, text=" AI Art Generation ",
                                 bg=COLORS['bg_panel'],
                                 fg=COLORS['accent_cyan'],
                                 font=('Arial', 11, 'bold'),
                                 relief=tk.GROOVE, bd=2,
                                 padx=10, pady=10)
        art_frame.pack(fill=tk.X, pady=5, padx=5)

        for text, style in [("🎨 Abstract Art", 'abstract'),
                           ("🟨 Mosaic Art", 'mosaic'),
                           ("💻 Glitch Art", 'glitch')]:
            btn = tk.Button(art_frame, text=text,
                           command=lambda s=style: self.ai_generate_art(s),
                           bg=COLORS['bg_button'],
                           fg=COLORS['text_primary'],
                           activebackground=COLORS['bg_button_hover'],
                           activeforeground=COLORS['text_primary'],
                           relief=tk.RAISED, bd=2, cursor='hand2',
                           font=('Arial', 9))
            btn.pack(fill=tk.X, pady=3)

    def setup_brush_tab(self):
        brush_tab = ttk.Frame(self.notebook)
        self.notebook.add(brush_tab, text="🎨 Brush Settings")

        type_frame = tk.LabelFrame(brush_tab, text=" Brush Type ",
                                  bg=COLORS['bg_panel'],
                                  fg=COLORS['text_heading'],
                                  font=('Arial', 11, 'bold'),
                                  relief=tk.GROOVE, bd=2,
                                  padx=10, pady=10)
        type_frame.pack(fill=tk.X, pady=5, padx=5)

        brush_types = ["Round", "Square", "Soft Round", "Hard Round", "Texture"]
        self.brush_type = tk.StringVar(value="Round")

        for btype in brush_types:
            radio = tk.Radiobutton(type_frame, text=btype, variable=self.brush_type,
                                  value=btype,
                                  bg=COLORS['bg_panel'],
                                  fg=COLORS['text_primary'],
                                  selectcolor=COLORS['bg_button_hover'],
                                  activebackground=COLORS['bg_panel'],
                                  activeforeground=COLORS['text_primary'],
                                  font=('Arial', 10))
            radio.pack(anchor=tk.W, padx=10, pady=3)

        settings_frame = tk.LabelFrame(brush_tab, text=" Settings ",
                                      bg=COLORS['bg_panel'],
                                      fg=COLORS['text_heading'],
                                      font=('Arial', 11, 'bold'),
                                      relief=tk.GROOVE, bd=2,
                                      padx=10, pady=10)
        settings_frame.pack(fill=tk.X, pady=5, padx=5)

        # Hardness
        hardness_label = tk.Label(settings_frame, text="Hardness:",
                                 bg=COLORS['bg_panel'],
                                 fg=COLORS['text_primary'],
                                 font=('Arial', 10))
        hardness_label.pack(anchor=tk.W, padx=5, pady=(5,0))

        hardness_scale = tk.Scale(settings_frame, from_=0, to=100,
                                 orient=tk.HORIZONTAL,
                                 bg=COLORS['bg_panel'],
                                 fg=COLORS['text_primary'],
                                 troughcolor=COLORS['bg_dark'],
                                 highlightthickness=0, bd=0,
                                 sliderlength=15)
        hardness_scale.set(80)
        hardness_scale.pack(fill=tk.X, padx=5, pady=5)

        # Spacing
        spacing_label = tk.Label(settings_frame, text="Spacing:",
                                bg=COLORS['bg_panel'],
                                fg=COLORS['text_primary'],
                                font=('Arial', 10))
        spacing_label.pack(anchor=tk.W, padx=5, pady=(5,0))

        spacing_scale = tk.Scale(settings_frame, from_=1, to=50,
                                orient=tk.HORIZONTAL,
                                bg=COLORS['bg_panel'],
                                fg=COLORS['text_primary'],
                                troughcolor=COLORS['bg_dark'],
                                highlightthickness=0, bd=0,
                                sliderlength=15)
        spacing_scale.set(25)
        spacing_scale.pack(fill=tk.X, padx=5, pady=5)

    def setup_image_tab(self):
        """Image operations tab"""
        image_tab = ttk.Frame(self.notebook)
        self.notebook.add(image_tab, text="🖼️ Image")

        # Rotate
        rotate_frame = tk.LabelFrame(image_tab, text=" Rotate ",
                                    bg=COLORS['bg_panel'],
                                    fg=COLORS['text_heading'],
                                    font=('Arial', 11, 'bold'),
                                    relief=tk.GROOVE, bd=2,
                                    padx=10, pady=10)
        rotate_frame.pack(fill=tk.X, pady=5, padx=5)

        for text, cmd in [("Rotate 90° CW", lambda: self.rotate_image(90)),
                         ("Rotate 180°", lambda: self.rotate_image(180)),
                         ("Rotate 90° CCW", lambda: self.rotate_image(-90))]:
            btn = tk.Button(rotate_frame, text=text, command=cmd,
                           bg=COLORS['bg_button'],
                           fg=COLORS['text_primary'],
                           activebackground=COLORS['bg_button_hover'],
                           activeforeground=COLORS['text_primary'],
                           relief=tk.RAISED, bd=2, cursor='hand2',
                           font=('Arial', 9))
            btn.pack(fill=tk.X, pady=3)

        # Flip
        flip_frame = tk.LabelFrame(image_tab, text=" Flip ",
                                  bg=COLORS['bg_panel'],
                                  fg=COLORS['text_heading'],
                                  font=('Arial', 11, 'bold'),
                                  relief=tk.GROOVE, bd=2,
                                  padx=10, pady=10)
        flip_frame.pack(fill=tk.X, pady=5, padx=5)

        for text, cmd in [("Flip Horizontal", self.flip_horizontal),
                         ("Flip Vertical", self.flip_vertical)]:
            btn = tk.Button(flip_frame, text=text, command=cmd,
                           bg=COLORS['bg_button'],
                           fg=COLORS['text_primary'],
                           activebackground=COLORS['bg_button_hover'],
                           activeforeground=COLORS['text_primary'],
                           relief=tk.RAISED, bd=2, cursor='hand2',
                           font=('Arial', 9))
            btn.pack(fill=tk.X, pady=3)

        # Resize
        resize_frame = tk.LabelFrame(image_tab, text=" Resize ",
                                    bg=COLORS['bg_panel'],
                                    fg=COLORS['text_heading'],
                                    font=('Arial', 11, 'bold'),
                                    relief=tk.GROOVE, bd=2,
                                    padx=10, pady=10)
        resize_frame.pack(fill=tk.X, pady=5, padx=5)

        btn = tk.Button(resize_frame, text="Resize Image", command=self.resize_image,
                       bg=COLORS['bg_button'],
                       fg=COLORS['text_primary'],
                       activebackground=COLORS['bg_button_hover'],
                       activeforeground=COLORS['text_primary'],
                       relief=tk.RAISED, bd=2, cursor='hand2',
                       font=('Arial', 9))
        btn.pack(fill=tk.X, pady=3)

        # Vignette
        vignette_frame = tk.LabelFrame(image_tab, text=" Vignette ",
                                      bg=COLORS['bg_panel'],
                                      fg=COLORS['text_heading'],
                                      font=('Arial', 11, 'bold'),
                                      relief=tk.GROOVE, bd=2,
                                      padx=10, pady=10)
        vignette_frame.pack(fill=tk.X, pady=5, padx=5)

        btn = tk.Button(vignette_frame, text="Apply Vignette", command=self.apply_vignette,
                       bg=COLORS['bg_button'],
                       fg=COLORS['text_primary'],
                       activebackground=COLORS['bg_button_hover'],
                       activeforeground=COLORS['text_primary'],
                       relief=tk.RAISED, bd=2, cursor='hand2',
                       font=('Arial', 9))
        btn.pack(fill=tk.X, pady=3)

    def setup_status_bar(self):
        self.status_bar = tk.Frame(self.root, bg=COLORS['bg_dark'], relief=tk.SUNKEN, bd=1)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = tk.Label(self.status_bar, text="🤖 Ready",
                                     bg=COLORS['bg_dark'],
                                     fg=COLORS['text_primary'],
                                     font=('Arial', 9), padx=10)
        self.status_label.pack(side=tk.LEFT)

        self.progress_label = tk.Label(self.status_bar, text="",
                                      bg=COLORS['bg_dark'],
                                      fg=COLORS['accent_cyan'],
                                      font=('Arial', 9), padx=10)
        self.progress_label.pack(side=tk.LEFT)

        self.coord_label = tk.Label(self.status_bar, text="x: 0, y: 0",
                                   bg=COLORS['bg_dark'],
                                   fg=COLORS['text_secondary'],
                                   font=('Arial', 9), padx=10)
        self.coord_label.pack(side=tk.RIGHT)

        self.zoom_label = tk.Label(self.status_bar, text="100%",
                                  bg=COLORS['bg_dark'],
                                  fg=COLORS['accent'],
                                  font=('Arial', 9, 'bold'), padx=10)
        self.zoom_label.pack(side=tk.RIGHT)

        shortcut_label = tk.Label(self.status_bar, text="⌨️ Ctrl+Z Undo | Ctrl+Y Redo",
                                 bg=COLORS['bg_dark'],
                                 fg=COLORS['text_secondary'],
                                 font=('Arial', 8), padx=10)
        shortcut_label.pack(side=tk.RIGHT)

        version_label = tk.Label(self.status_bar, text="v3.0 AI",
                                bg=COLORS['bg_dark'],
                                fg=COLORS['accent_cyan'],
                                font=('Arial', 8, 'bold'), padx=10)
        version_label.pack(side=tk.RIGHT)

    def create_tooltip(self, widget, text):
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            x = event.x_root + 10
            y = event.y_root + 10
            tooltip.wm_geometry(f"+{x}+{y}")
            label = tk.Label(tooltip, text=text,
                            background="#ffffe0", foreground='#000000',
                            relief='solid', borderwidth=1, padx=5, pady=3,
                            font=('Arial', 9))
            label.pack()
            widget.tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    # ============ CORE FUNCTIONALITY ============

    def update_color_preview(self):
        self.color_preview.delete("all")
        if self.current_tool == "eraser":
            self.color_preview.create_rectangle(2, 2, 22, 22, fill='white',
                                                outline=COLORS['error'], width=2)
            self.color_preview.create_text(12, 12, text="E", fill=COLORS['error'],
                                          font=('Arial', 10, 'bold'))
        else:
            self.color_preview.create_rectangle(2, 2, 22, 22, fill=self.brush_color,
                                                outline=COLORS['border'], width=2)

    def ensure_rgb(self, image):
        if image.mode != 'RGB':
            return image.convert('RGB')
        return image

    def add_to_history(self):
        if self.current_image:
            img_copy = self.current_image.copy()
            self.history = self.history[:self.history_index + 1]
            if len(self.history) > self.max_history:
                self.history.pop(0)
            self.history.append(img_copy)
            self.history_index = len(self.history) - 1

    def get_image_coords(self, canvas_x, canvas_y):
        try:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
        except:
            return 0, 0

        if not self.current_image:
            return 0, 0

        img_width, img_height = self.current_image.size
        display_width = int(img_width * self.zoom_factor)
        display_height = int(img_height * self.zoom_factor)

        img_x = int((canvas_x - canvas_width//2 + display_width//2) / self.zoom_factor)
        img_y = int((canvas_y - canvas_height//2 + display_height//2) / self.zoom_factor)

        return img_x, img_y

    def show_image(self):
        if not self.current_image:
            return

        try:
            self.canvas.update_idletasks()
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
        except:
            return

        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 800
            canvas_height = 600

        img_width, img_height = self.current_image.size
        display_width = int(img_width * self.zoom_factor)
        display_height = int(img_height * self.zoom_factor)

        if display_width > canvas_width * 0.9 or display_height > canvas_height * 0.9:
            scale = min(canvas_width / img_width, canvas_height / img_height) * 0.9
            display_width = int(img_width * scale)
            display_height = int(img_height * scale)
            self.zoom_factor = scale

        try:
            resized_image = self.current_image.resize((display_width, display_height),
                                                      Image.Resampling.LANCZOS)
            self.display_image = ImageTk.PhotoImage(resized_image)

            self.canvas.delete("all")
            self.canvas.create_image(canvas_width // 2, canvas_height // 2,
                                    image=self.display_image, anchor=tk.CENTER)

            self.zoom_label.config(text=f"{int(self.zoom_factor * 100)}%")
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except Exception as e:
            print(f"Error displaying image: {e}")

    # ============ FILE OPERATIONS ============

    def new_file(self):
        width = simpledialog.askinteger("New File", "Width:", initialvalue=800)
        height = simpledialog.askinteger("New File", "Height:", initialvalue=600)
        if width and height:
            self.original_image = Image.new('RGB', (width, height), 'white')
            self.current_image = self.original_image.copy()
            self.layers = [{'name': 'Background', 'image': self.current_image.copy(),
                          'visible': True, 'opacity': 100}]
            self.active_layer_index = 0
            self.update_layers_list()
            self.history = [self.current_image.copy()]
            self.history_index = 0
            self.zoom_factor = 1.0
            self.show_image()
            self.reset_sliders()
            self.status_label.config(text=f"New file created: {width}×{height}")

    def open_image(self):
        filename = filedialog.askopenfilename(
            title="Open Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"),
                      ("All files", "*.*")]
        )
        if filename:
            try:
                self.filename = filename
                self.original_image = Image.open(filename)
                self.current_image = self.original_image.copy()

                if self.current_image.mode != 'RGB':
                    self.current_image = self.current_image.convert('RGB')

                self.layers = [{'name': 'Background', 'image': self.current_image.copy(),
                              'visible': True, 'opacity': 100}]
                self.active_layer_index = 0
                self.update_layers_list()

                self.history = [self.current_image.copy()]
                self.history_index = 0

                self.zoom_factor = 1.0
                self.show_image()
                self.reset_sliders()

                width, height = self.current_image.size
                self.status_label.config(text=f"Loaded: {os.path.basename(filename)} ({width}×{height})")

            except Exception as e:
                messagebox.showerror("Error", f"Could not open image: {str(e)}")

    def save_image(self):
        if self.current_image:
            if self.filename:
                self.current_image.save(self.filename)
                self.status_label.config(text="Image saved")
            else:
                self.save_image_as()

    def save_image_as(self):
        if self.current_image:
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
            )
            if filename:
                self.current_image.save(filename)
                self.filename = filename
                self.status_label.config(text=f"Saved as {filename}")

    def export_image(self, format_type):
        if self.current_image:
            filename = filedialog.asksaveasfilename(
                defaultextension=f".{format_type}",
                filetypes=[(f"{format_type.upper()} files", f"*.{format_type}"), ("All files", "*.*")]
            )
            if filename:
                self.current_image.save(filename)
                self.status_label.config(text=f"Exported as {filename}")

    # ============ ZOOM CONTROLS ============

    def zoom_in(self):
        self.zoom_factor *= 1.2
        self.show_image()

    def zoom_out(self):
        self.zoom_factor /= 1.2
        if self.zoom_factor < 0.1:
            self.zoom_factor = 0.1
        self.show_image()

    def fit_to_screen(self):
        self.zoom_factor = 1.0
        self.show_image()

    # ============ TOOL MANAGEMENT ============

    def set_tool(self, tool):
        self.current_tool = tool
        self.status_label.config(text=f"Tool: {tool.title()}")

        for t, btn in self.tool_buttons.items():
            if t == tool:
                btn.config(bg=COLORS['bg_button_hover'], relief=tk.SUNKEN)
            else:
                btn.config(bg=COLORS['bg_button'], relief=tk.RAISED)

        self.update_color_preview()

    def update_brush_size(self):
        self.brush_size = self.brush_size_var.get()

    def choose_color(self):
        color = colorchooser.askcolor(title="Choose color", initialcolor=self.brush_color)
        if color[1]:
            self.brush_color = color[1]
            self.update_color_preview()

    # ============ LAYER MANAGEMENT ============

    def new_layer(self):
        if self.current_image:
            new_layer = {
                'name': f'Layer {len(self.layers)}',
                'image': Image.new('RGBA', self.current_image.size, (0, 0, 0, 0)),
                'visible': True,
                'opacity': 100
            }
            self.layers.append(new_layer)
            self.active_layer_index = len(self.layers) - 1
            self.update_layers_list()
            self.status_label.config(text="New layer created")
            self.update_current_image()

    def duplicate_layer(self):
        if self.layers:
            layer = self.layers[self.active_layer_index]
            new_layer = {
                'name': f'{layer["name"]} copy',
                'image': layer['image'].copy(),
                'visible': True,
                'opacity': 100
            }
            self.layers.append(new_layer)
            self.active_layer_index = len(self.layers) - 1
            self.update_layers_list()
            self.status_label.config(text="Layer duplicated")
            self.update_current_image()

    def delete_layer(self):
        if len(self.layers) > 1:
            if self.active_layer_index < len(self.layers):
                self.layers.pop(self.active_layer_index)
                self.active_layer_index = min(self.active_layer_index, len(self.layers) - 1)
                self.update_layers_list()
                self.update_current_image()
                self.status_label.config(text="Layer deleted")

    def toggle_layer_visibility(self):
        if self.layers:
            layer = self.layers[self.active_layer_index]
            layer['visible'] = not layer['visible']
            self.update_layers_list()
            self.update_current_image()

    def on_layer_select(self, event):
        if self.layers_listbox.curselection():
            self.active_layer_index = self.layers_listbox.curselection()[0]
            self.update_current_image()

    def update_layers_list(self):
        self.layers_listbox.delete(0, tk.END)
        for i, layer in enumerate(self.layers):
            visibility = "👁️" if layer['visible'] else "🙈"
            self.layers_listbox.insert(tk.END, f"{visibility} {layer['name']}")
        if self.layers and self.active_layer_index < len(self.layers):
            self.layers_listbox.selection_set(self.active_layer_index)

    def update_current_image(self):
        if self.layers:
            visible_layers = [layer for layer in self.layers if layer['visible']]
            if visible_layers:
                base = visible_layers[0]['image'].convert('RGBA')
                for layer in visible_layers[1:]:
                    layer_img = layer['image']
                    if layer_img.mode != 'RGBA':
                        layer_img = layer_img.convert('RGBA')
                    opacity = layer.get('opacity', 100) / 100.0
                    if opacity < 1.0:
                        alpha = layer_img.split()[3]
                        alpha = alpha.point(lambda p: int(p * opacity))
                        layer_img.putalpha(alpha)
                    base = Image.alpha_composite(base, layer_img)
                self.current_image = base.convert('RGB')
                self.show_image()

    def merge_layers(self):
        if len(self.layers) > 1:
            self.update_current_image()
            self.layers = [{
                'name': 'Merged',
                'image': self.current_image.copy(),
                'visible': True,
                'opacity': 100
            }]
            self.active_layer_index = 0
            self.update_layers_list()
            self.add_to_history()
            self.status_label.config(text="Layers merged")

    # ============ MOUSE EVENT HANDLERS ============

    def on_canvas_click(self, event):
        img_x, img_y = self.get_image_coords(event.x, event.y)

        if self.current_tool == "brush":
            self.start_drawing(event)
        elif self.current_tool == "select":
            self.start_selection(event)
        elif self.current_tool == "eraser":
            self.start_erasing(event)
        elif self.current_tool == "text":
            self.add_text(event)
        elif self.current_tool == "magic_wand":
            self.magic_wand_select(event)
        elif self.current_tool == "gradient":
            self.start_gradient(event)
        elif self.current_tool == "crop":
            self.start_crop(event)

        self.coord_label.config(text=f"x: {img_x}, y: {img_y}")

    def on_canvas_drag(self, event):
        if self.current_tool == "brush":
            self.continue_drawing(event)
        elif self.current_tool == "select":
            self.update_selection(event)
        elif self.current_tool == "eraser":
            self.continue_erasing(event)
        elif self.current_tool == "gradient":
            self.update_gradient(event)
        elif self.current_tool == "crop":
            self.update_crop(event)

    def on_canvas_release(self, event):
        if self.current_tool == "brush":
            self.end_drawing()
        elif self.current_tool == "select":
            self.end_selection(event)
        elif self.current_tool == "eraser":
            self.end_erasing()
        elif self.current_tool == "gradient":
            self.apply_gradient(event)
        elif self.current_tool == "crop":
            self.apply_crop(event)

    def on_mousewheel(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    # ============ DRAWING METHODS ============

    def start_drawing(self, event):
        if self.current_image:
            self.drawing = True
            self.last_x = event.x
            self.last_y = event.y
            self.draw_point(event.x, event.y)

    def continue_drawing(self, event):
        if hasattr(self, 'drawing') and self.drawing:
            self.draw_line(self.last_x, self.last_y, event.x, event.y)
            self.last_x = event.x
            self.last_y = event.y

    def end_drawing(self):
        if hasattr(self, 'drawing'):
            self.drawing = False
            self.add_to_history()

    def draw_point(self, x, y):
        if self.current_image:
            draw_image = self.current_image.copy()
            draw = ImageDraw.Draw(draw_image)

            img_x, img_y = self.get_image_coords(x, y)
            img_width, img_height = self.current_image.size

            if 0 <= img_x < img_width and 0 <= img_y < img_height:
                radius = int(self.brush_size / 2)
                draw.ellipse([img_x - radius, img_y - radius, img_x + radius, img_y + radius],
                           fill=self.brush_color)
                self.current_image = draw_image
                self.show_image()

    def draw_line(self, x1, y1, x2, y2):
        if self.current_image:
            draw_image = self.current_image.copy()
            draw = ImageDraw.Draw(draw_image)

            img_x1, img_y1 = self.get_image_coords(x1, y1)
            img_x2, img_y2 = self.get_image_coords(x2, y2)
            img_width, img_height = self.current_image.size

            if (0 <= img_x1 < img_width and 0 <= img_y1 < img_height and
                0 <= img_x2 < img_width and 0 <= img_y2 < img_height):
                draw.line([img_x1, img_y1, img_x2, img_y2],
                         fill=self.brush_color, width=self.brush_size)
                self.current_image = draw_image
                self.show_image()

    # ============ ERASER METHODS ============

    def start_erasing(self, event):
        if self.current_image:
            self.drawing = True
            self.last_x = event.x
            self.last_y = event.y
            self.erase_point(event.x, event.y)
            self.status_label.config(text="Erasing...")

    def continue_erasing(self, event):
        if hasattr(self, 'drawing') and self.drawing:
            self.erase_line(self.last_x, self.last_y, event.x, event.y)
            self.last_x = event.x
            self.last_y = event.y

    def end_erasing(self):
        if hasattr(self, 'drawing'):
            self.drawing = False
            self.add_to_history()
            self.status_label.config(text="Eraser stopped")

    def erase_point(self, x, y):
        if self.current_image:
            draw_image = self.current_image.copy()
            draw = ImageDraw.Draw(draw_image)

            img_x, img_y = self.get_image_coords(x, y)
            img_width, img_height = self.current_image.size

            if 0 <= img_x < img_width and 0 <= img_y < img_height:
                radius = int(self.brush_size / 2)
                draw.ellipse([img_x - radius, img_y - radius, img_x + radius, img_y + radius],
                           fill='white')
                self.current_image = draw_image
                self.show_image()

    def erase_line(self, x1, y1, x2, y2):
        if self.current_image:
            draw_image = self.current_image.copy()
            draw = ImageDraw.Draw(draw_image)

            img_x1, img_y1 = self.get_image_coords(x1, y1)
            img_x2, img_y2 = self.get_image_coords(x2, y2)
            img_width, img_height = self.current_image.size

            if (0 <= img_x1 < img_width and 0 <= img_y1 < img_height and
                0 <= img_x2 < img_width and 0 <= img_y2 < img_height):
                draw.line([img_x1, img_y1, img_x2, img_y2],
                         fill='white', width=self.brush_size)
                self.current_image = draw_image
                self.show_image()

    # ============ TEXT TOOL ============

    def add_text(self, event):
        if self.current_image:
            text = simpledialog.askstring("Add Text", "Enter text:")
            if text:
                font_size = simpledialog.askinteger("Font Size", "Enter font size:", initialvalue=30)
                if font_size:
                    try:
                        font = ImageFont.truetype("arial.ttf", font_size)
                    except:
                        try:
                            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
                        except:
                            font = ImageFont.load_default()

                    draw_image = self.current_image.copy()
                    draw = ImageDraw.Draw(draw_image)

                    img_x, img_y = self.get_image_coords(event.x, event.y)
                    img_width, img_height = self.current_image.size

                    if 0 <= img_x < img_width and 0 <= img_y < img_height:
                        draw.text((img_x, img_y), text, fill=self.brush_color, font=font)
                        self.current_image = draw_image
                        self.add_to_history()
                        self.show_image()
                        self.status_label.config(text=f"Text added: {text}")

    # ============ MAGIC WAND TOOL ============

    def magic_wand_select(self, event):
        """Magic Wand tool - selects and removes similar colored areas"""
        if not self.current_image:
            return

        self.status_label.config(text="Magic Wand: Selecting similar colors...")

        img_x, img_y = self.get_image_coords(event.x, event.y)
        img_width, img_height = self.current_image.size

        if not (0 <= img_x < img_width and 0 <= img_y < img_height):
            self.status_label.config(text="Magic Wand: Click inside the image")
            return

        try:
            # Convert to RGB to avoid RGBA issues
            img_rgb = self.current_image.convert('RGB')
            pixel_color = img_rgb.getpixel((img_x, img_y))
            tolerance = 30

            # Create a mask using PIL
            mask = Image.new('L', img_rgb.size, 0)
            pixels = img_rgb.load()
            mask_pixels = mask.load()

            width, height = img_rgb.size
            for y in range(height):
                for x in range(width):
                    r, g, b = pixels[x, y]
                    if (abs(r - pixel_color[0]) <= tolerance and
                        abs(g - pixel_color[1]) <= tolerance and
                        abs(b - pixel_color[2]) <= tolerance):
                        mask_pixels[x, y] = 255

            # Convert to numpy arrays for processing
            result_array = np.array(img_rgb)  # shape (H, W, 3)
            mask_array = np.array(mask) > 0   # boolean mask (H, W)

            # Replace selected pixels with white
            result_array[mask_array] = [255, 255, 255]

            # Convert back to PIL Image
            self.current_image = Image.fromarray(result_array)
            self.add_to_history()
            self.show_image()
            self.status_label.config(text=f"Magic Wand: Removed color {pixel_color}")

        except Exception as e:
            self.status_label.config(text=f"Magic Wand Error: {str(e)}")
            messagebox.showerror("Magic Wand Error", f"An error occurred: {str(e)}")

    # ============ GRADIENT TOOL ============

    def start_gradient(self, event):
        self.selection_start = (event.x, event.y)
        self.status_label.config(text="Gradient: Click and drag to apply gradient")

    def update_gradient(self, event):
        if self.selection_start:
            if self.selection_rect:
                self.canvas.delete(self.selection_rect)
            x1, y1 = self.selection_start
            x2, y2 = event.x, event.y
            self.selection_rect = self.canvas.create_line(
                x1, y1, x2, y2, fill=COLORS['accent'], width=2, dash=(4, 2)
            )

    def apply_gradient(self, event):
        if self.selection_start and self.current_image:
            x1, y1 = self.selection_start
            x2, y2 = event.x, event.y

            img_x1, img_y1 = self.get_image_coords(x1, y1)
            img_x2, img_y2 = self.get_image_coords(x2, y2)
            img_width, img_height = self.current_image.size

            if (0 <= img_x1 < img_width and 0 <= img_y1 < img_height and
                0 <= img_x2 < img_width and 0 <= img_y2 < img_height):

                draw_image = self.current_image.copy()
                draw = ImageDraw.Draw(draw_image)

                steps = max(abs(img_x2 - img_x1), abs(img_y2 - img_y1))
                if steps < 1:
                    steps = 100

                for i in range(steps):
                    t = i / steps
                    r = int(255 * t)
                    g = int(128 * t)
                    b = int(0 * t)
                    color = (r, g, b)

                    x = int(img_x1 + (img_x2 - img_x1) * t)
                    y = int(img_y1 + (img_y2 - img_y1) * t)

                    radius = int(self.brush_size * (0.5 + 0.5 * t))
                    draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color)

                self.current_image = draw_image
                self.add_to_history()
                self.show_image()

                if self.selection_rect:
                    self.canvas.delete(self.selection_rect)
                    self.selection_rect = None
                self.selection_start = None
                self.status_label.config(text="Gradient applied")

    # ============ CROP TOOL ============

    def start_crop(self, event):
        self.selection_start = (event.x, event.y)
        self.status_label.config(text="Crop: Select area to crop")
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)

    def update_crop(self, event):
        if self.selection_start:
            if self.selection_rect:
                self.canvas.delete(self.selection_rect)
            x1, y1 = self.selection_start
            x2, y2 = event.x, event.y
            self.selection_rect = self.canvas.create_rectangle(
                x1, y1, x2, y2, outline=COLORS['accent'], width=2, dash=(4, 2)
            )

    def apply_crop(self, event):
        if self.selection_start and self.current_image:
            x1, y1 = self.selection_start
            x2, y2 = event.x, event.y

            img_x1, img_y1 = self.get_image_coords(x1, y1)
            img_x2, img_y2 = self.get_image_coords(x2, y2)
            img_width, img_height = self.current_image.size

            if (0 <= img_x1 < img_width and 0 <= img_y1 < img_height and
                0 <= img_x2 < img_width and 0 <= img_y2 < img_height):

                if abs(img_x2 - img_x1) > 10 and abs(img_y2 - img_y1) > 10:
                    left = min(img_x1, img_x2)
                    top = min(img_y1, img_y2)
                    right = max(img_x1, img_x2)
                    bottom = max(img_y1, img_y2)

                    self.current_image = self.current_image.crop((left, top, right, bottom))
                    self.add_to_history()
                    self.zoom_factor = 1.0
                    self.show_image()

                    if self.selection_rect:
                        self.canvas.delete(self.selection_rect)
                        self.selection_rect = None
                    self.selection_start = None
                    self.status_label.config(text=f"Cropped: {right-left}×{bottom-top}")

    # ============ SELECTION METHODS ============

    def start_selection(self, event):
        self.selection_start = (event.x, event.y)
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)

    def update_selection(self, event):
        if self.selection_start:
            if self.selection_rect:
                self.canvas.delete(self.selection_rect)
            x1, y1 = self.selection_start
            x2, y2 = event.x, event.y
            self.selection_rect = self.canvas.create_rectangle(
                x1, y1, x2, y2, outline=COLORS['accent'], dash=(4, 2), width=2
            )

    def end_selection(self, event):
        self.selection_end = (event.x, event.y)
        if self.selection_start and self.selection_end:
            x1, y1 = self.selection_start
            x2, y2 = self.selection_end
            if self.selection_rect:
                self.canvas.delete(self.selection_rect)
            self.selection_rect = self.canvas.create_rectangle(
                x1, y1, x2, y2, outline=COLORS['accent'], dash=(4, 2), width=2
            )
            self.status_label.config(text=f"Selection: ({x1},{y1}) to ({x2},{y2})")

    def copy_selection(self):
        if self.selection_rect:
            coords = self.canvas.coords(self.selection_rect)
            if coords:
                x1, y1, x2, y2 = coords
                img_x1, img_y1 = self.get_image_coords(x1, y1)
                img_x2, img_y2 = self.get_image_coords(x2, y2)
                img_width, img_height = self.current_image.size

                if (0 <= img_x1 < img_width and 0 <= img_y1 < img_height and
                    0 <= img_x2 < img_width and 0 <= img_y2 < img_height and
                    img_x1 < img_x2 and img_y1 < img_y2):

                    self.copied_image = self.current_image.crop((img_x1, img_y1, img_x2, img_y2))
                    self.status_label.config(text="Selection copied")

    def paste_selection(self):
        if self.copied_image and self.current_image:
            img_width, img_height = self.current_image.size
            paste_x = (img_width - self.copied_image.width) // 2
            paste_y = (img_height - self.copied_image.height) // 2

            self.current_image.paste(self.copied_image, (paste_x, paste_y))
            self.add_to_history()
            self.show_image()
            self.status_label.config(text="Selection pasted")

    def cut_selection(self):
        if self.selection_rect:
            self.copy_selection()
            coords = self.canvas.coords(self.selection_rect)
            if coords:
                x1, y1, x2, y2 = coords
                img_x1, img_y1 = self.get_image_coords(x1, y1)
                img_x2, img_y2 = self.get_image_coords(x2, y2)
                img_width, img_height = self.current_image.size

                if (0 <= img_x1 < img_width and 0 <= img_y1 < img_height and
                    0 <= img_x2 < img_width and 0 <= img_y2 < img_height and
                    img_x1 < img_x2 and img_y1 < img_y2):

                    draw_image = self.current_image.copy()
                    draw = ImageDraw.Draw(draw_image)
                    draw.rectangle([img_x1, img_y1, img_x2, img_y2], fill='white')
                    self.current_image = draw_image
                    self.add_to_history()
                    self.show_image()
                    self.status_label.config(text="Selection cut")

    # ============ AI-POWERED FEATURES ============

    def run_ai_operation(self, operation, *args):
        """Run AI operation with progress indicator"""
        if self.is_processing:
            return

        if not self.current_image:
            messagebox.showwarning("Warning", "Please open an image first.")
            return

        self.is_processing = True
        self.progress_label.config(text="🤖 AI Processing...")
        self.status_label.config(text="AI is working on your image...")
        self.root.update()

        try:
            result = operation(*args)
            if result is not None:
                self.current_image = result
                self.add_to_history()
                self.show_image()
                self.progress_label.config(text="✅ Done!")
                self.status_label.config(text="AI operation completed successfully")
            else:
                self.progress_label.config(text="❌ Failed")
                self.status_label.config(text="AI operation returned None")
        except Exception as e:
            self.progress_label.config(text="❌ Error")
            self.status_label.config(text=f"Error: {str(e)[:50]}")
            messagebox.showerror("AI Error", f"An error occurred:\n{str(e)}")

        self.is_processing = False
        self.root.after(3000, lambda: self.progress_label.config(text=""))

    def ai_smart_enhance(self):
        """AI-powered smart enhancement"""
        self.run_ai_operation(self.ai_processor.smart_enhance, self.current_image)

    def ai_remove_background(self):
        """AI-powered background removal"""
        self.run_ai_operation(self.ai_processor.remove_background, self.current_image)

    def ai_style_transfer(self, style):
        """AI style transfer"""
        self.run_ai_operation(self.ai_processor.style_transfer_simple, self.current_image, style)

    def ai_upscale(self):
        """AI upscale image"""
        factor = simpledialog.askinteger("Upscale", "Upscale factor (2 or 3):",
                                         initialvalue=2, minvalue=2, maxvalue=3)
        if factor:
            self.run_ai_operation(self.ai_processor.upscale_image, self.current_image, factor)

    def ai_colorize(self):
        """AI colorize grayscale image"""
        if self.current_image.mode == 'L' or self.current_image.mode == 'LA':
            self.run_ai_operation(self.ai_processor.colorize_grayscale, self.current_image)
        else:
            gray = self.current_image.convert('L')
            self.run_ai_operation(self.ai_processor.colorize_grayscale, gray)

    def ai_denoise(self):
        """AI-powered denoising"""
        self.run_ai_operation(self.ai_processor.denoise_image, self.current_image)

    def ai_auto_crop(self):
        """AI-powered auto crop"""
        self.run_ai_operation(self.ai_processor.auto_crop, self.current_image)

    def ai_enhance_face(self):
        """AI face enhancement"""
        self.run_ai_operation(self.ai_processor.enhance_face, self.current_image)

    def ai_generate_art(self, style):
        """AI art generation"""
        self.run_ai_operation(self.ai_processor.generate_art, self.current_image, style)

    # ============ IMAGE OPERATIONS ============

    def resize_image(self):
        if self.current_image:
            width = simpledialog.askinteger("Resize", "New Width:", initialvalue=self.current_image.width)
            height = simpledialog.askinteger("Resize", "New Height:", initialvalue=self.current_image.height)
            if width and height:
                self.current_image = self.current_image.resize((width, height), Image.Resampling.LANCZOS)
                self.add_to_history()
                self.show_image()
                self.status_label.config(text=f"Resized to {width}×{height}")

    def rotate_image(self, angle):
        if self.current_image:
            self.current_image = self.current_image.rotate(angle, expand=True)
            self.add_to_history()
            self.show_image()
            self.status_label.config(text=f"Rotated {angle}°")

    def flip_horizontal(self):
        if self.current_image:
            self.current_image = ImageOps.mirror(self.current_image)
            self.add_to_history()
            self.show_image()
            self.status_label.config(text="Flipped Horizontal")

    def flip_vertical(self):
        if self.current_image:
            self.current_image = ImageOps.flip(self.current_image)
            self.add_to_history()
            self.show_image()
            self.status_label.config(text="Flipped Vertical")

    def invert_image(self):
        if self.current_image:
            self.current_image = ImageOps.invert(self.current_image)
            self.add_to_history()
            self.show_image()
            self.status_label.config(text="Image inverted")

    # ============ FILTER METHODS ============

    def apply_median_filter(self):
        if self.current_image:
            self.current_image = self.current_image.filter(ImageFilter.MedianFilter(3))
            self.add_to_history()
            self.show_image()
            self.status_label.config(text="Median filter applied (Noise reduction)")

    def apply_emboss(self):
        if self.current_image:
            self.current_image = self.current_image.filter(ImageFilter.EMBOSS)
            self.add_to_history()
            self.show_image()
            self.status_label.config(text="Emboss effect applied")

    def apply_edge_detection(self):
        if self.current_image:
            self.current_image = self.current_image.filter(ImageFilter.FIND_EDGES)
            self.add_to_history()
            self.show_image()
            self.status_label.config(text="Edge detection applied")

    def apply_pixelate(self):
        if self.current_image:
            width, height = self.current_image.size
            pixel_size = 10
            small = self.current_image.resize((width // pixel_size, height // pixel_size),
                                             Image.Resampling.NEAREST)
            self.current_image = small.resize((width, height), Image.Resampling.NEAREST)
            self.add_to_history()
            self.show_image()
            self.status_label.config(text="Pixelate effect applied")

    def apply_vignette(self):
        if self.current_image:
            img = self.current_image.copy()
            width, height = img.size

            mask = Image.new('L', (width, height), 0)
            draw = ImageDraw.Draw(mask)

            center_x, center_y = width // 2, height // 2
            radius = min(width, height) // 2

            for i in range(radius):
                t = i / radius
                brightness = int(255 * (1 - t * t))
                if brightness < 0:
                    brightness = 0
                draw.ellipse([center_x - i, center_y - i, center_x + i, center_y + i],
                           fill=brightness)

            img.putalpha(mask)
            background = Image.new('RGB', (width, height), 'black')
            background.paste(img, (0, 0), img)

            self.current_image = background
            self.add_to_history()
            self.show_image()
            self.status_label.config(text="Vignette applied")

    # ============ ADJUSTMENT METHODS ============

    def apply_adjustments(self):
        if self.current_image and self.original_image:
            self.current_image = self.original_image.copy()

            adjustments = ['brightness', 'contrast', 'saturation', 'exposure', 'vibration']
            for adjustment in adjustments:
                if adjustment in self.slider_vars:
                    value = self.slider_vars[adjustment].get()
                    if adjustment == 'brightness':
                        enhancer = ImageEnhance.Brightness(self.current_image)
                    elif adjustment == 'contrast':
                        enhancer = ImageEnhance.Contrast(self.current_image)
                    elif adjustment == 'saturation':
                        enhancer = ImageEnhance.Color(self.current_image)
                    elif adjustment == 'exposure':
                        enhancer = ImageEnhance.Brightness(self.current_image)
                    elif adjustment == 'vibration':
                        enhancer = ImageEnhance.Color(self.current_image)
                    self.current_image = enhancer.enhance(value)

            self.show_image()

    def apply_color_balance(self):
        """Apply color balance adjustments"""
        if self.current_image and self.original_image:
            self.current_image = self.original_image.copy()

            r_balance = self.slider_vars.get('red_balance', tk.DoubleVar(value=1.0)).get()
            g_balance = self.slider_vars.get('green_balance', tk.DoubleVar(value=1.0)).get()
            b_balance = self.slider_vars.get('blue_balance', tk.DoubleVar(value=1.0)).get()

            r, g, b = self.current_image.split()

            r = ImageEnhance.Brightness(r).enhance(r_balance)
            g = ImageEnhance.Brightness(g).enhance(g_balance)
            b = ImageEnhance.Brightness(b).enhance(b_balance)

            self.current_image = Image.merge('RGB', (r, g, b))
            self.show_image()

    def auto_tone(self):
        if self.current_image:
            self.current_image = ImageOps.autocontrast(self.current_image)
            self.add_to_history()
            self.show_image()
            self.status_label.config(text="Auto tone applied")

    def auto_contrast(self):
        if self.current_image:
            self.current_image = ImageOps.autocontrast(self.current_image)
            self.add_to_history()
            self.show_image()
            self.status_label.config(text="Auto contrast applied")

    def auto_color(self):
        if self.current_image:
            self.current_image = ImageEnhance.Color(self.current_image).enhance(1.2)
            self.add_to_history()
            self.show_image()
            self.status_label.config(text="Auto color applied")

    # ============ PHOTO EFFECTS ============

    def apply_grayscale(self):
        if self.current_image:
            self.current_image = self.current_image.convert('L').convert('RGB')
            self.add_to_history()
            self.show_image()
            self.status_label.config(text="Grayscale applied")

    def apply_sepia(self):
        if self.current_image:
            temp_image = self.ensure_rgb(self.current_image)
            width, height = temp_image.size
            pixels = temp_image.load()

            for py in range(height):
                for px in range(width):
                    r, g, b = temp_image.getpixel((px, py))
                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                    pixels[px, py] = (min(255, tr), min(255, tg), min(255, tb))

            self.current_image = temp_image
            self.add_to_history()
            self.show_image()
            self.status_label.config(text="Sepia applied")

    def apply_cool(self):
        if self.current_image:
            try:
                temp_image = self.ensure_rgb(self.current_image)
                r, g, b = temp_image.split()
                b = ImageEnhance.Brightness(b).enhance(1.3)
                self.current_image = Image.merge('RGB', (r, g, b))
                self.add_to_history()
                self.show_image()
                self.status_label.config(text="Cool filter applied")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot apply cool filter: {str(e)}")

    def apply_warm(self):
        if self.current_image:
            try:
                temp_image = self.ensure_rgb(self.current_image)
                r, g, b = temp_image.split()
                r = ImageEnhance.Brightness(r).enhance(1.3)
                self.current_image = Image.merge('RGB', (r, g, b))
                self.add_to_history()
                self.show_image()
                self.status_label.config(text="Warm filter applied")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot apply warm filter: {str(e)}")

    def apply_vintage(self):
        if self.current_image:
            temp_image = self.ensure_rgb(self.current_image)
            temp_image = ImageEnhance.Color(temp_image).enhance(0.7)
            temp_image = ImageEnhance.Brightness(temp_image).enhance(0.9)
            self.current_image = temp_image
            self.add_to_history()
            self.show_image()
            self.status_label.config(text="Vintage filter applied")

    # ============ FILTER METHODS ============

    def apply_filter(self, filter_obj):
        if self.current_image:
            self.current_image = self.current_image.filter(filter_obj)
            self.add_to_history()
            self.show_image()
            self.status_label.config(text="Filter applied")

    def apply_blur(self, radius):
        if self.current_image:
            self.current_image = self.current_image.filter(ImageFilter.GaussianBlur(radius))
            self.add_to_history()
            self.show_image()
            self.status_label.config(text=f"Gaussian blur (radius={radius}) applied")

    def apply_motion_blur(self):
        if self.current_image:
            self.current_image = self.current_image.filter(ImageFilter.GaussianBlur(5))
            self.add_to_history()
            self.show_image()
            self.status_label.config(text="Motion blur applied")

    def apply_unsharp_mask(self):
        if self.current_image:
            self.current_image = self.current_image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
            self.add_to_history()
            self.show_image()
            self.status_label.config(text="Unsharp mask applied")

    def apply_oil_paint(self):
        if self.current_image:
            self.current_image = self.current_image.filter(ImageFilter.MedianFilter(5))
            self.add_to_history()
            self.show_image()
            self.status_label.config(text="Oil paint effect applied")

    def apply_watercolor(self):
        if self.current_image:
            self.current_image = self.current_image.filter(ImageFilter.CONTOUR)
            self.add_to_history()
            self.show_image()
            self.status_label.config(text="Watercolor effect applied")

    def apply_sketch(self):
        if self.current_image:
            self.current_image = self.current_image.filter(ImageFilter.CONTOUR)
            self.add_to_history()
            self.show_image()
            self.status_label.config(text="Sketch effect applied")

    def apply_comic(self):
        if self.current_image:
            self.current_image = self.current_image.filter(ImageFilter.EDGE_ENHANCE_MORE)
            self.add_to_history()
            self.show_image()
            self.status_label.config(text="Comic effect applied")

    def apply_posterize(self):
        if self.current_image:
            self.current_image = ImageOps.posterize(self.current_image, 4)
            self.add_to_history()
            self.show_image()
            self.status_label.config(text="Posterize applied")

    # ============ UNDO / REDO ============

    def reset_sliders(self):
        defaults = {'brightness': 1.0, 'contrast': 1.0, 'saturation': 1.0,
                   'exposure': 1.0, 'vibration': 1.0,
                   'red_balance': 1.0, 'green_balance': 1.0, 'blue_balance': 1.0}
        for var_name, default in defaults.items():
            if var_name in self.slider_vars:
                self.slider_vars[var_name].set(default)
                if var_name in self.slider_labels:
                    self.slider_labels[var_name].config(text="100%")

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.current_image = self.history[self.history_index].copy()
            self.show_image()
            self.status_label.config(text="Undo")

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_image = self.history[self.history_index].copy()
            self.show_image()
            self.status_label.config(text="Redo")

    # ============ HELP METHODS ============

    def show_about(self):
        about_text = """
        ╔══════════════════════════════════════════════════╗
        ║               PIXEDIT PRO AI                   ║
        ║         AI-Powered Image Editor                ║
        ╚══════════════════════════════════════════════════╝

        Version 3.0 - AI Edition

        A Comprehensive Image Processing Application
        with AI-Powered Features
        Developed for Class XII Computer Science Project

        🤖 AI FEATURES:
        • Smart Enhancement
        • Background Removal
        • Style Transfer (Oil, Watercolor, Sketch, Pop Art, Impressionist)
        • AI Upscaling
        • AI Colorization
        • AI Denoising
        • AI Auto Crop
        • Face Enhancement
        • AI Art Generation (Abstract, Mosaic, Glitch)

        ✨ Traditional Features:
        • Working Keyboard Shortcuts
        • Blend Modes
        • Image Rotation & Flip
        • Color Balance
        • Edge Detection
        • Emboss Effect
        • Pixelate Effect
        • Vignette Effect
        • Noise Reduction
        • Resize Image
        • Percentage display for sliders

        Technologies Used:
        • Python 3.x
        • Tkinter (GUI)
        • Pillow/PIL (Image Processing)
        • NumPy (Array Processing)

        Keyboard Shortcuts:
        Ctrl+N  - New    Ctrl+O  - Open
        Ctrl+S  - Save   Ctrl+Z  - Undo
        Ctrl+Y  - Redo   Ctrl+C  - Copy
        Ctrl+V  - Paste  Ctrl+X  - Cut

        V - Select   B - Brush   E - Eraser
        T - Text     C - Crop    W - Magic Wand

        © 2024 All Rights Reserved
        """
        messagebox.showinfo("About PixEdit Pro AI", about_text)

    def show_shortcuts(self):
        shortcuts_text = """
        ╔══════════════════════════════════════════════════╗
        ║         KEYBOARD SHORTCUTS                     ║
        ╚══════════════════════════════════════════════════╝

        File Operations:
        Ctrl+N  - New File
        Ctrl+O  - Open Image
        Ctrl+S  - Save Image
        Ctrl+Shift+S - Save As
        Ctrl+Q  - Exit

        Edit Operations:
        Ctrl+Z  - Undo
        Ctrl+Y  - Redo
        Ctrl+C  - Copy Selection
        Ctrl+V  - Paste Selection
        Ctrl+X  - Cut Selection

        Tools:
        V       - Selection Tool
        B       - Brush Tool
        E       - Eraser Tool
        T       - Text Tool
        C       - Crop Tool
        W       - Magic Wand
        G       - Gradient Tool

        View:
        Ctrl++  - Zoom In
        Ctrl+-  - Zoom Out
        Ctrl+0  - Fit to Screen

        AI Features available in AI menu!
        """
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)

    # ============ PANEL SHOW METHODS ============

    def show_file_panel(self):
        self.notebook.select(0)

    def show_brush_panel(self):
        self.notebook.select(3)

    def show_adjust_panel(self):
        self.notebook.select(0)

    def show_filter_panel(self):
        self.notebook.select(1)

    def show_ai_panel(self):
        self.notebook.select(2)

    def show_layer_panel(self):
        self.notebook.select(0)

    def show_image_panel(self):
        self.notebook.select(4)

# ============ MAIN APPLICATION ============

if __name__ == "__main__":
    root = tk.Tk()
    app = PixEditPro(root)
    root.mainloop()
