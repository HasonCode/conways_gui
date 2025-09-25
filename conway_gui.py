import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import csv
import threading
import time
from PIL import Image, ImageDraw
# Import classes from main.py but avoid running the main code
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# We need to import the classes without running the main code
# Let's define them here to avoid the main.py execution
import random

class Location:
    def __init__(self, i: int, j: int):
        self.i = i
        self.j = j

class ImplCell:
    def __init__(self, location, grid):
        self.location = location
        self.grid = grid

    def process(self):
        pass

    def clone(self, grid):
        pass

    def __str__(self):
        return " "

class DeadCell(ImplCell):
    def __init__(self, row, col, grid):
        super().__init__(Location(row, col), grid)

    def clone(self, grid):
        return DeadCell(self.location.i, self.location.j, grid)

    def process(self):
        curechance = 0.5
        cancer_chance = 0.1
        neighbors = self.grid.count_neighbors(self.location.i, self.location.j)
        if neighbors == 3:
            return AliveCell(self.location.i, self.location.j, self.grid)
        cancer_neighbors = self.grid.count_neighbors(self.location.i, self.location.j, CancerCell)
        if cancer_neighbors >= 1:
            if random.random() < cancer_chance:
                return CancerCell(self.location.i, self.location.j, self.grid)
        if cancer_neighbors >= 5:
            if random.random() < curechance:
                return CureCell(self.location.i, self.location.j, self.grid)
        return DeadCell(self.location.i, self.location.j, self.grid)

    def __str__(self):
        return "🟥"

class AliveCell(ImplCell):
    def __init__(self, row, col, grid):
        super().__init__(Location(row, col), grid)

    def process(self):
        neighbors = self.grid.count_neighbors(self.location.i, self.location.j)
        if neighbors in [2, 3]:
            return AliveCell(self.location.i, self.location.j, self.grid)
        return DeadCell(self.location.i, self.location.j, self.grid)

    def clone(self, grid):
        return AliveCell(self.location.i, self.location.j, grid)

    def __str__(self):
        return "🟩"

class CancerCell(ImplCell):
    def __init__(self, row, col, grid):
        self.cancer_weighting = 0.01
        super().__init__(Location(row, col), grid)

    def process(self):
        loc = self.location
        cure_neighbors = self.grid.count_neighbors(loc.i, loc.j, CureCell)
        cancer_neighbors = self.grid.count_neighbors(loc.i, loc.j, CancerCell)
        if cure_neighbors >= 1 or cancer_neighbors >= 7:
            return AliveCell(loc.i, loc.j, self.grid)
        return CancerCell(loc.i, loc.j, self.grid)

    def clone(self, grid):
        return CancerCell(self.location.i, self.location.j, grid)

    def __str__(self):
        return "⬜"

class CureCell(ImplCell):
    def __init__(self, row, col, grid):
        self.cure_weighting = 0.1
        super().__init__(Location(row, col), grid)

    def process(self):
        loc = self.location
        neighbors = self.grid.count_neighbors(loc.i, loc.j, CureCell)
        dead_neighbors = self.grid.count_neighbors(loc.i, loc.j, DeadCell)
        if dead_neighbors >= 4:
            return DeadCell(loc.i, loc.j, self.grid)
        if neighbors >= 2:
            return DeadCell(loc.i, loc.j, self.grid)
        return CureCell(loc.i, loc.j, self.grid)

    def __str__(self):
        return "🟦"

    def clone(self, grid):
        return CureCell(self.location.i, self.location.j, grid)

class Grid:
    def __init__(self, rows, cols, mode_list=["normal", "normal", "normal", "normal"]):
        self.rows = rows
        self.cols = cols
        self.mode_list = mode_list
        self.cells = [[DeadCell(j, i, self) for i in range(cols)] for j in range(rows)]

    def set_cell(self, cell):
        self.cells[cell.location.i][cell.location.j] = cell

    def clone(self):
        new_grid = Grid(self.rows, self.cols, self.mode_list)
        for i in range(len(self.cells)):
            for j in range(len(self.cells[0])):
                new_grid.cells[i][j] = self.cells[i][j].clone(new_grid)
        return new_grid

    def get_cell(self, row, col):
        return self.cells[row][col]

    def check_left(self, col, mode="normal"):
        if mode == "periodic":
            return col % len(self.cells[0])
        elif mode == "mirror" and col < 0:
            return 0
        elif col < 0:
            return None
        return col

    def check_right(self, col, mode="normal"):
        if mode == "periodic":
            return col % len(self.cells[0])
        elif mode == "mirror" and col > len(self.cells[0]) - 1:
            return len(self.cells[0]) - 1
        elif col > len(self.cells[0]) - 1:
            return None
        return col

    def check_up(self, row, mode="normal"):
        if mode == "periodic":
            return row % len(self.cells)
        elif mode == "mirror" and row < 0:
            return 0
        elif row < 0:
            return None
        return row

    def check_down(self, row, mode="normal"):
        if mode == "periodic":
            return row % len(self.cells)
        elif mode == "mirror" and row > len(self.cells) - 1:
            return len(self.cells) - 1
        elif row > len(self.cells) - 1:
            return None
        return row

    def row_processor(self, row, i, mode_list):
        if i < row:
            return self.check_up(i, mode_list[2])
        elif i > row:
            return self.check_down(i, mode_list[3])
        else:
            return i

    def col_processor(self, col, j, mode_list):
        if j < col:
            return self.check_left(j, mode_list[0])
        elif j > col:
            return self.check_right(j, mode_list[1])
        else:
            return j

    def count_neighbors(self, row, col, cell_type=AliveCell, mode_list=None):
        if mode_list is None:
            mode_list = self.mode_list
        count_cells = 0
        for i in range(row-1, row+2):
            row_val = self.row_processor(row, i, mode_list)
            for j in range(col-1, col+2):
                col_val = self.col_processor(col, j, mode_list)
                if row_val is not None and col_val is not None:
                    if isinstance(self.cells[row_val][col_val], cell_type):
                        count_cells += 1
        if isinstance(self.cells[row][col], cell_type):
            count_cells -= 1
        return count_cells

class GameRunner:
    def __init__(self, grid):
        self.grid = grid

    def update(self):
        temp_grid = self.grid.clone()
        for row in self.grid.cells:
            for cell in row:
                next_cell = cell.process()
                next_cell.grid = temp_grid
                temp_grid.set_cell(next_cell)
        self.grid = temp_grid

class ConwayGUI:
    def __init__(self):
        # Initialize main window
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Conway's Game of Life - Advanced GUI")
        self.root.geometry("1600x1000")  # Increased window size
        self.root.minsize(1200, 800)  # Set minimum window size

        # Game state
        self.grid_size = 30
        self.cell_size = 15
        self.max_canvas_size = 500  # Reduced for better performance
        self.max_grid_size = 60  # Reduced max grid size for better performance
        self.speed = 100  # ms between iterations
        self.running = False
        self.grid = Grid(self.grid_size, self.grid_size)
        self.game_runner = GameRunner(self.grid)
        
        # Cell types and colors
        self.cell_types = {
            "Dead": (DeadCell, "#000000"),
            "Alive": (AliveCell, "#00FF00"),
            "Cancer": (CancerCell, "#FF0000"),
            "Cure": (CureCell, "#0000FF")
        }
        self.selected_cell_type = "Alive"
        
        # Boundary conditions
        self.boundary_modes = ["normal", "normal", "normal", "normal"]  # left, right, up, down
        
        # Statistics tracking
        self.iteration_count = 0
        self.cell_history = []

        # GIF recording
        self.recording_gif = False
        self.gif_frames = []
        self.max_gif_frames = 300  # Limit frames to prevent memory issues
        
        # UI state
        self.is_dragging = False
        self.drag_throttle = 0  # For throttling drag events
        self.last_painted_cell = None  # Prevent painting same cell multiple times
        
        self.setup_ui()
        self.create_cell_sprites()
        self.update_canvas()
        self.update_charts()

        # Bind window resize event
        self.root.bind("<Configure>", self.on_window_resize)
        
    def setup_ui(self):
        """Setup the main UI layout"""
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Left panel for canvas and controls - make it scrollable
        left_panel = ctk.CTkScrollableFrame(main_frame, width=800, height=700)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Canvas frame with scrollable area
        self.canvas_frame = ctk.CTkFrame(left_panel)
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create scrollable frame for canvas
        self.canvas_scroll_frame = ctk.CTkScrollableFrame(
            self.canvas_frame,
            width=min(self.grid_size * self.cell_size + 40, self.max_canvas_size),
            height=min(self.grid_size * self.cell_size + 40, self.max_canvas_size)
        )
        self.canvas_scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Canvas with extra space for boundary indicators
        self.border_margin = 20  # Space for boundary indicators
        canvas_width = self.grid_size * self.cell_size + (2 * self.border_margin)
        canvas_height = self.grid_size * self.cell_size + (2 * self.border_margin)

        self.canvas = tk.Canvas(
            self.canvas_scroll_frame,
            width=canvas_width,
            height=canvas_height,
            bg="black",
            highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=10)
        
        # Bind canvas events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        # Controls frame
        controls_frame = ctk.CTkFrame(left_panel)
        controls_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.setup_controls(controls_frame)
        self.setup_weight_controls(left_panel)
        self.setup_boundary_controls(left_panel)
        
        # Right panel for charts
        right_panel = ctk.CTkFrame(main_frame)
        right_panel.pack(side="right", fill="both", padx=(5, 0))
        
        self.setup_charts(right_panel)
        
    def setup_controls(self, parent):
        """Setup control buttons and sliders"""
        # Row 1: Simulation controls
        sim_frame = ctk.CTkFrame(parent)
        sim_frame.pack(fill="x", padx=5, pady=5)
        
        self.start_btn = ctk.CTkButton(sim_frame, text="Start", command=self.start_simulation)
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = ctk.CTkButton(sim_frame, text="Stop", command=self.stop_simulation)
        self.stop_btn.pack(side="left", padx=5)
        
        self.step_btn = ctk.CTkButton(sim_frame, text="Step", command=self.step_simulation)
        self.step_btn.pack(side="left", padx=5)
        
        self.clear_btn = ctk.CTkButton(sim_frame, text="Clear", command=self.clear_grid)
        self.clear_btn.pack(side="left", padx=5)
        
        # Row 2: Cell type selection
        cell_frame = ctk.CTkFrame(parent)
        cell_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(cell_frame, text="Cell Type:").pack(side="left", padx=5)
        
        self.cell_type_var = ctk.StringVar(value=self.selected_cell_type)
        self.cell_type_menu = ctk.CTkOptionMenu(
            cell_frame,
            variable=self.cell_type_var,
            values=list(self.cell_types.keys()),
            command=self.on_cell_type_change
        )
        self.cell_type_menu.pack(side="left", padx=5)
        
        # Row 3: Sliders
        slider_frame = ctk.CTkFrame(parent)
        slider_frame.pack(fill="x", padx=5, pady=5)
        
        # Speed slider
        speed_frame = ctk.CTkFrame(slider_frame)
        speed_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkLabel(speed_frame, text="Speed (ms):").pack()
        self.speed_slider = ctk.CTkSlider(
            speed_frame,
            from_=10,
            to=1000,
            number_of_steps=99,
            command=self.on_speed_change
        )
        self.speed_slider.set(self.speed)
        self.speed_slider.pack(fill="x", padx=5)
        
        self.speed_label = ctk.CTkLabel(speed_frame, text=f"{self.speed}ms")
        self.speed_label.pack()
        
        # Grid size slider
        size_frame = ctk.CTkFrame(slider_frame)
        size_frame.pack(side="left", fill="x", expand=True, padx=5)

        ctk.CTkLabel(size_frame, text="Grid Size:").pack()
        self.size_slider = ctk.CTkSlider(
            size_frame,
            from_=10,
            to=self.max_grid_size,
            number_of_steps=self.max_grid_size-10,
            command=self.on_size_change
        )
        self.size_slider.set(self.grid_size)
        self.size_slider.pack(fill="x", padx=5)

        self.size_label = ctk.CTkLabel(size_frame, text=f"{self.grid_size}x{self.grid_size}")
        self.size_label.pack()

        # Cell size info
        self.cell_size_label = ctk.CTkLabel(size_frame, text=f"Cell size: {self.cell_size}px", font=("Arial", 10))
        self.cell_size_label.pack()
        
        # Row 4: File operations
        file_frame = ctk.CTkFrame(parent)
        file_frame.pack(fill="x", padx=5, pady=5)

        # First row of file operations
        file_row1 = ctk.CTkFrame(file_frame)
        file_row1.pack(fill="x", pady=2)

        self.save_btn = ctk.CTkButton(file_row1, text="Save Grid", command=self.save_grid)
        self.save_btn.pack(side="left", padx=2, fill="x", expand=True)

        self.load_btn = ctk.CTkButton(file_row1, text="Load Grid", command=self.load_grid)
        self.load_btn.pack(side="left", padx=2, fill="x", expand=True)

        # Second row of file operations
        file_row2 = ctk.CTkFrame(file_frame)
        file_row2.pack(fill="x", pady=2)

        self.save_graph_btn = ctk.CTkButton(file_row2, text="Save Graph", command=self.save_line_graph)
        self.save_graph_btn.pack(side="left", padx=2, fill="x", expand=True)

        self.record_gif_btn = ctk.CTkButton(file_row2, text="Record GIF", command=self.toggle_gif_recording)
        self.record_gif_btn.pack(side="left", padx=2, fill="x", expand=True)

    def setup_weight_controls(self, parent):
        """Setup cell weight controls"""
        weight_frame = ctk.CTkFrame(parent)
        weight_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Header
        header_frame = ctk.CTkFrame(weight_frame)
        header_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(header_frame, text="Cell Weights:", font=("Arial", 14, "bold")).pack(side="left", padx=5)

        # Info text
        info_text = "Range: 0.0001 - 1.0 | Higher values = stronger effect"
        ctk.CTkLabel(header_frame, text=info_text, font=("Arial", 10), text_color="gray").pack(side="right", padx=5)

        # Controls frame
        controls_frame = ctk.CTkFrame(weight_frame)
        controls_frame.pack(fill="x", pady=5, padx=10)

        # Cancer weight
        cancer_frame = ctk.CTkFrame(controls_frame)
        cancer_frame.pack(side="left", fill="x", expand=True, padx=5)

        ctk.CTkLabel(cancer_frame, text="Cancer Weight:", font=("Arial", 12, "bold")).pack(pady=2)
        self.cancer_weight_var = ctk.StringVar(value="0.01")
        self.cancer_weight_entry = ctk.CTkEntry(cancer_frame, textvariable=self.cancer_weight_var, width=100)
        self.cancer_weight_entry.pack(pady=2)
        self.cancer_weight_entry.bind("<KeyRelease>", self.on_cancer_weight_change)

        # Cure weight
        cure_frame = ctk.CTkFrame(controls_frame)
        cure_frame.pack(side="right", fill="x", expand=True, padx=5)

        ctk.CTkLabel(cure_frame, text="Cure Weight:", font=("Arial", 12, "bold")).pack(pady=2)
        self.cure_weight_var = ctk.StringVar(value="0.1")
        self.cure_weight_entry = ctk.CTkEntry(cure_frame, textvariable=self.cure_weight_var, width=100)
        self.cure_weight_entry.pack(pady=2)
        self.cure_weight_entry.bind("<KeyRelease>", self.on_cure_weight_change)

    def setup_boundary_controls(self, parent):
        """Setup boundary condition controls"""
        boundary_frame = ctk.CTkFrame(parent)
        boundary_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Header with info
        header_frame = ctk.CTkFrame(boundary_frame)
        header_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(header_frame, text="Boundary Conditions:", font=("Arial", 14, "bold")).pack(side="left", padx=5)

        # Info button/label
        info_text = "Normal: Dead edges | Periodic: Wrapping | Mirror: Reflective"
        ctk.CTkLabel(header_frame, text=info_text, font=("Arial", 10), text_color="gray").pack(side="right", padx=5)

        # Create boundary controls in a more accessible layout
        grid_frame = ctk.CTkFrame(boundary_frame)
        grid_frame.pack(pady=5, fill="x")

        # Configure grid weights for proper spacing
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        grid_frame.grid_columnconfigure(2, weight=1)
        grid_frame.grid_rowconfigure(0, weight=1)
        grid_frame.grid_rowconfigure(1, weight=1)
        grid_frame.grid_rowconfigure(2, weight=1)

        # Top boundary
        top_frame = ctk.CTkFrame(grid_frame)
        top_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(top_frame, text="Top:", font=("Arial", 12, "bold")).pack(pady=2)
        self.top_boundary = ctk.CTkOptionMenu(
            top_frame,
            values=["normal", "periodic", "mirror"],
            command=lambda x: self.set_boundary(2, x),
            width=120
        )
        self.top_boundary.set("normal")
        self.top_boundary.pack(pady=2)

        # Left boundary
        left_frame = ctk.CTkFrame(grid_frame)
        left_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(left_frame, text="Left:", font=("Arial", 12, "bold")).pack(pady=2)
        self.left_boundary = ctk.CTkOptionMenu(
            left_frame,
            values=["normal", "periodic", "mirror"],
            command=lambda x: self.set_boundary(0, x),
            width=120
        )
        self.left_boundary.set("normal")
        self.left_boundary.pack(pady=2)

        # Center space (for visual balance)
        center_frame = ctk.CTkFrame(grid_frame)
        center_frame.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(center_frame, text="Grid", font=("Arial", 12, "bold")).pack(pady=15)

        # Right boundary
        right_frame = ctk.CTkFrame(grid_frame)
        right_frame.grid(row=1, column=2, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(right_frame, text="Right:", font=("Arial", 12, "bold")).pack(pady=2)
        self.right_boundary = ctk.CTkOptionMenu(
            right_frame,
            values=["normal", "periodic", "mirror"],
            command=lambda x: self.set_boundary(1, x),
            width=120
        )
        self.right_boundary.set("normal")
        self.right_boundary.pack(pady=2)

        # Bottom boundary
        bottom_frame = ctk.CTkFrame(grid_frame)
        bottom_frame.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(bottom_frame, text="Bottom:", font=("Arial", 12, "bold")).pack(pady=2)
        self.bottom_boundary = ctk.CTkOptionMenu(
            bottom_frame,
            values=["normal", "periodic", "mirror"],
            command=lambda x: self.set_boundary(3, x),
            width=120
        )
        self.bottom_boundary.set("normal")
        self.bottom_boundary.pack(pady=2)

        # Add visual indicator legend
        legend_frame = ctk.CTkFrame(boundary_frame)
        legend_frame.pack(pady=10, fill="x")

        ctk.CTkLabel(legend_frame, text="Visual Indicators:", font=("Arial", 12, "bold")).pack(pady=2)

        # Create legend items
        legend_items = [
            ("Normal (Gray Border)", "#808080", "Dead edges - N"),
            ("Periodic (Green Border)", "#00FF00", "Wrapping edges - P"),
            ("Mirror (Orange Border)", "#FF8800", "Reflective edges - M")
        ]

        for text, color, description in legend_items:
            item_frame = ctk.CTkFrame(legend_frame)
            item_frame.pack(fill="x", padx=5, pady=1)

            # Color indicator
            color_label = ctk.CTkLabel(item_frame, text="●", text_color=color, font=("Arial", 16))
            color_label.pack(side="left", padx=5)

            # Description
            desc_label = ctk.CTkLabel(item_frame, text=f"{text}: {description}", font=("Arial", 10))
            desc_label.pack(side="left", padx=5)

    def setup_charts(self, parent):
        """Setup matplotlib charts"""
        charts_frame = ctk.CTkFrame(parent)
        charts_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(charts_frame, text="Statistics", font=("Arial", 16, "bold")).pack(pady=5)

        # Create matplotlib figure
        self.fig = Figure(figsize=(6, 8), facecolor='#2b2b2b')

        # Pie chart
        self.pie_ax = self.fig.add_subplot(2, 1, 1)
        self.pie_ax.set_facecolor('#2b2b2b')

        # Line chart
        self.line_ax = self.fig.add_subplot(2, 1, 2)
        self.line_ax.set_facecolor('#2b2b2b')

        # Embed in tkinter
        self.chart_canvas = FigureCanvasTkAgg(self.fig, charts_frame)
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_cell_sprites(self):
        """Create custom sprites for different cell types"""
        self.sprites = {}

        for cell_type, (_, color) in self.cell_types.items():
            try:
                # Try to load custom sprite files first
                sprite_path = f"sprites/{cell_type.lower()}_sprite.png"
                if os.path.exists(sprite_path):
                    # Load and resize custom sprite
                    img = Image.open(sprite_path)
                    img = img.resize((self.cell_size-1, self.cell_size-1), Image.Resampling.LANCZOS)
                else:
                    # Fallback to generated sprites
                    img = self.create_generated_sprite(cell_type, color)

            except Exception as e:
                print(f"Error loading sprite for {cell_type}: {e}")
                # Fallback to generated sprites
                img = self.create_generated_sprite(cell_type, color)

            self.sprites[cell_type] = img

    def create_generated_sprite(self, cell_type, color):
        """Create a generated sprite for a cell type"""
        # Create a simple colored rectangle sprite
        img = Image.new('RGB', (self.cell_size-1, self.cell_size-1), color)

        # Add some visual distinction for different cell types
        draw = ImageDraw.Draw(img)
        if cell_type == "Cancer":
            # Add a cross pattern for cancer cells
            draw.line([(0, 0), (self.cell_size-2, self.cell_size-2)], fill="white", width=1)
            draw.line([(0, self.cell_size-2), (self.cell_size-2, 0)], fill="white", width=1)
        elif cell_type == "Cure":
            # Add a plus pattern for cure cells
            mid = self.cell_size // 2
            draw.line([(mid, 2), (mid, self.cell_size-3)], fill="white", width=2)
            draw.line([(2, mid), (self.cell_size-3, mid)], fill="white", width=2)
        elif cell_type == "Alive":
            # Add a dot for alive cells
            mid = self.cell_size // 2
            draw.ellipse([mid-2, mid-2, mid+2, mid+2], fill="white")

        return img

    def on_canvas_click(self, event):
        """Handle canvas click events"""
        if self.running:
            return

        self.is_dragging = True
        self.last_painted_cell = None
        self.drag_throttle = 0
        self.paint_cell(event.x, event.y)

    def on_canvas_drag(self, event):
        """Handle canvas drag events with throttling"""
        if self.running or not self.is_dragging:
            return

        # Throttle drag events to reduce lag
        self.drag_throttle += 1
        if self.drag_throttle % 3 == 0:  # Only process every 3rd drag event
            self.paint_cell(event.x, event.y)

    def on_canvas_release(self, event):
        """Handle canvas release events"""
        was_dragging = self.is_dragging
        self.is_dragging = False
        self.last_painted_cell = None

        # Update charts after dragging is complete
        if was_dragging:
            self.update_charts()

    def paint_cell(self, x, y):
        """Paint a cell at the given canvas coordinates with optimization"""
        # Adjust coordinates for border margin
        adjusted_x = x - self.border_margin
        adjusted_y = y - self.border_margin
        col = adjusted_x // self.cell_size
        row = adjusted_y // self.cell_size

        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            # Avoid painting the same cell multiple times during drag
            current_cell = (row, col)
            if self.last_painted_cell == current_cell:
                return

            self.last_painted_cell = current_cell

            cell_class, _ = self.cell_types[self.selected_cell_type]
            new_cell = cell_class(row, col, self.grid)

            # Apply current weight settings for special cells
            if isinstance(new_cell, CancerCell):
                try:
                    new_cell.cancer_weighting = float(self.cancer_weight_var.get())
                except (ValueError, AttributeError):
                    new_cell.cancer_weighting = 0.01  # Default
            elif isinstance(new_cell, CureCell):
                try:
                    new_cell.cure_weighting = float(self.cure_weight_var.get())
                except (ValueError, AttributeError):
                    new_cell.cure_weighting = 0.1  # Default

            self.grid.cells[row][col] = new_cell

            # Only update canvas, skip charts during drag for performance
            self.update_canvas()
            if not self.is_dragging:
                self.update_charts()

    def update_canvas(self):
        """Update the canvas display with optimizations"""
        self.canvas.delete("all")

        # First draw boundary indicators (background)
        self.draw_boundary_indicators()

        # Then draw cells on top, offset by border margin
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x1 = col * self.cell_size + self.border_margin
                y1 = row * self.cell_size + self.border_margin
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                cell = self.grid.cells[row][col]
                cell_type = type(cell).__name__.replace("Cell", "")

                if cell_type in self.cell_types:
                    _, color = self.cell_types[cell_type]

                    # Only draw non-dead cells for better performance on large grids
                    if cell_type != "Dead" or self.grid_size <= 40:
                        outline_color = "gray" if self.grid_size <= 40 else ""
                        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=outline_color)

                        # Simplified visual patterns for better performance
                        if self.cell_size >= 8:  # Only add patterns if cells are large enough
                            if cell_type == "Cancer":
                                # Simple cross pattern
                                self.canvas.create_line(x1+1, y1+1, x2-1, y2-1, fill="white", width=1)
                                self.canvas.create_line(x1+1, y2-1, x2-1, y1+1, fill="white", width=1)
                            elif cell_type == "Cure":
                                # Simple plus pattern
                                mid_x = (x1 + x2) // 2
                                mid_y = (y1 + y2) // 2
                                self.canvas.create_line(mid_x, y1+2, mid_x, y2-2, fill="white", width=1)
                                self.canvas.create_line(x1+2, mid_y, x2-2, mid_y, fill="white", width=1)
                            elif cell_type == "Alive":
                                # Simple dot pattern
                                mid_x = (x1 + x2) // 2
                                mid_y = (y1 + y2) // 2
                                self.canvas.create_oval(mid_x-1, mid_y-1, mid_x+1, mid_y+1, fill="white", outline="white")

    def draw_boundary_indicators(self):
        """Draw visual indicators around the canvas to show boundary conditions"""
        grid_width = self.grid_size * self.cell_size
        grid_height = self.grid_size * self.cell_size

        # Define colors for each boundary mode
        boundary_colors = {
            "normal": "#808080",    # Gray
            "periodic": "#00FF00",  # Green
            "mirror": "#FF8800"     # Orange
        }

        # Draw colored border strips in the margin areas

        # Left boundary (index 0)
        left_color = boundary_colors[self.boundary_modes[0]]
        self.canvas.create_rectangle(2, self.border_margin, self.border_margin - 2,
                                   self.border_margin + grid_height,
                                   fill=left_color, outline=left_color, tags="boundary")

        # Right boundary (index 1)
        right_color = boundary_colors[self.boundary_modes[1]]
        self.canvas.create_rectangle(self.border_margin + grid_width + 2, self.border_margin,
                                   self.border_margin + grid_width + self.border_margin - 2,
                                   self.border_margin + grid_height,
                                   fill=right_color, outline=right_color, tags="boundary")

        # Top boundary (index 2)
        top_color = boundary_colors[self.boundary_modes[2]]
        self.canvas.create_rectangle(self.border_margin, 2,
                                   self.border_margin + grid_width, self.border_margin - 2,
                                   fill=top_color, outline=top_color, tags="boundary")

        # Bottom boundary (index 3)
        bottom_color = boundary_colors[self.boundary_modes[3]]
        self.canvas.create_rectangle(self.border_margin, self.border_margin + grid_height + 2,
                                   self.border_margin + grid_width,
                                   self.border_margin + grid_height + self.border_margin - 2,
                                   fill=bottom_color, outline=bottom_color, tags="boundary")

        # Add text labels
        self.draw_boundary_labels(grid_width, grid_height)

    def draw_boundary_labels(self, grid_width, grid_height):
        """Draw text labels showing boundary modes in the border areas"""
        # Only show labels if there's enough space
        if self.border_margin >= 15:
            # Mode abbreviations for compact display
            mode_text = {
                "normal": "N",
                "periodic": "P",
                "mirror": "M"
            }

            # Text color for visibility
            text_color = "white"
            font_size = max(8, min(12, self.border_margin // 2))

            # Left boundary label
            self.canvas.create_text(self.border_margin // 2,
                                  self.border_margin + grid_height // 2,
                                  text=mode_text[self.boundary_modes[0]],
                                  fill=text_color, font=("Arial", font_size, "bold"),
                                  tags="boundary")

            # Right boundary label
            self.canvas.create_text(self.border_margin + grid_width + self.border_margin // 2,
                                  self.border_margin + grid_height // 2,
                                  text=mode_text[self.boundary_modes[1]],
                                  fill=text_color, font=("Arial", font_size, "bold"),
                                  tags="boundary")

            # Top boundary label
            self.canvas.create_text(self.border_margin + grid_width // 2,
                                  self.border_margin // 2,
                                  text=mode_text[self.boundary_modes[2]],
                                  fill=text_color, font=("Arial", font_size, "bold"),
                                  tags="boundary")

            # Bottom boundary label
            self.canvas.create_text(self.border_margin + grid_width // 2,
                                  self.border_margin + grid_height + self.border_margin // 2,
                                  text=mode_text[self.boundary_modes[3]],
                                  fill=text_color, font=("Arial", font_size, "bold"),
                                  tags="boundary")

    def update_charts(self):
        """Update the pie chart and line graph"""
        # Count cell types
        counts = {"Dead": 0, "Alive": 0, "Cancer": 0, "Cure": 0}

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cell = self.grid.cells[row][col]
                cell_type = type(cell).__name__.replace("Cell", "")
                if cell_type in counts:
                    counts[cell_type] += 1

        # Store history for line graph
        self.cell_history.append(counts.copy())

        # Clear previous plots
        self.pie_ax.clear()
        self.line_ax.clear()

        # Pie chart
        non_zero_counts = {k: v for k, v in counts.items() if v > 0}
        if non_zero_counts:
            colors = [self.cell_types[cell_type][1] for cell_type in non_zero_counts.keys()]
            self.pie_ax.pie(non_zero_counts.values(), labels=non_zero_counts.keys(),
                           colors=colors, autopct='%1.1f%%', textprops={'color': 'white'})
            self.pie_ax.set_title(f"Cell Distribution (Iteration {self.iteration_count})", color='white')

        # Line graph
        if len(self.cell_history) > 1:
            iterations = range(len(self.cell_history))
            for cell_type in counts.keys():
                values = [h[cell_type] for h in self.cell_history]
                color = self.cell_types[cell_type][1]
                self.line_ax.plot(iterations, values, label=cell_type, color=color, linewidth=2)

            self.line_ax.set_xlabel("Iteration", color='white')
            self.line_ax.set_ylabel("Cell Count", color='white')
            self.line_ax.set_title("Cell Population Over Time", color='white')
            self.line_ax.legend()
            self.line_ax.tick_params(colors='white')
            self.line_ax.grid(True, alpha=0.3)

        # Refresh the canvas
        self.chart_canvas.draw()

    def start_simulation(self):
        """Start the simulation"""
        if not self.running:
            self.running = True
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.simulation_thread = threading.Thread(target=self.run_simulation, daemon=True)
            self.simulation_thread.start()

    def stop_simulation(self):
        """Stop the simulation"""
        self.running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

    def save_line_graph(self):
        """Save the line graph as a PNG image"""
        # Check if there's meaningful data to save
        if len(self.cell_history) < 2:
            messagebox.showwarning(
                "No Data",
                "No line graph data available. Run a simulation first to generate data."
            )
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="Save Line Graph"
        )

        if filename:
            try:
                # Create a new figure for saving (independent of GUI)
                save_fig, save_ax = plt.subplots(figsize=(10, 6))
                save_ax.set_title("Cell Population Over Time", fontsize=14, fontweight='bold')
                save_ax.set_xlabel("Iteration", fontsize=12)
                save_ax.set_ylabel("Cell Count", fontsize=12)
                save_ax.grid(True, alpha=0.3)

                # Plot the data
                iterations = list(range(len(self.cell_history)))
                for cell_type in ["Dead", "Alive", "Cancer", "Cure"]:
                    counts = [data[cell_type] for data in self.cell_history]
                    color = self.cell_types[cell_type][1]  # Get color from cell_types
                    save_ax.plot(iterations, counts, label=cell_type, color=color, linewidth=2)

                save_ax.legend(fontsize=10)
                save_ax.set_xlim(0, max(1, len(self.cell_history) - 1))

                # Add metadata text
                metadata_text = (
                    f"Grid Size: {self.grid_size}x{self.grid_size}\n"
                    f"Total Iterations: {len(self.cell_history)}\n"
                    f"Boundary Modes: L:{self.boundary_modes[0]}, R:{self.boundary_modes[1]}, "
                    f"T:{self.boundary_modes[2]}, B:{self.boundary_modes[3]}"
                )
                save_ax.text(0.02, 0.98, metadata_text, transform=save_ax.transAxes,
                           fontsize=9, verticalalignment='top',
                           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

                # Save the figure
                save_fig.tight_layout()
                save_fig.savefig(filename, dpi=300, bbox_inches='tight')
                plt.close(save_fig)  # Clean up

                messagebox.showinfo("Success", f"Line graph saved to {filename}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to save line graph: {str(e)}")

    def toggle_gif_recording(self):
        """Toggle GIF recording on/off"""
        if not self.recording_gif:
            self.start_gif_recording()
        else:
            self.stop_gif_recording()

    def start_gif_recording(self):
        """Start recording frames for GIF"""
        self.recording_gif = True
        self.gif_frames = []
        self.record_gif_btn.configure(text="Stop Recording", fg_color="#dc2626")  # Red color

        # Capture the first frame
        self.capture_gif_frame()

        messagebox.showinfo("Recording Started",
                          f"GIF recording started!\n"
                          f"Maximum frames: {self.max_gif_frames}\n"
                          f"Run your simulation and click 'Stop Recording' when done.")

    def stop_gif_recording(self):
        """Stop recording and offer to save GIF"""
        self.recording_gif = False
        self.record_gif_btn.configure(text="Record GIF", fg_color=["#3B8ED0", "#1F6AA5"])  # Default CTk blue

        if len(self.gif_frames) < 2:
            messagebox.showwarning("No Frames",
                                 "Not enough frames recorded. Need at least 2 frames for a GIF.")
            return

        # Offer to save the GIF
        result = messagebox.askyesno("Save GIF",
                                   f"Recorded {len(self.gif_frames)} frames.\n"
                                   "Would you like to save as animated GIF?")
        if result:
            self.save_gif()

        # Clear frames after handling
        self.gif_frames = []

        # Force button state update
        self.root.update_idletasks()

    def capture_gif_frame(self):
        """Capture current canvas state as a frame for GIF"""
        if not self.recording_gif or len(self.gif_frames) >= self.max_gif_frames:
            return

        try:
            # Get canvas dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Create PIL image from canvas
            # We'll create a simplified version by drawing the grid state
            frame = Image.new('RGB', (canvas_width, canvas_height), 'black')
            draw = ImageDraw.Draw(frame)

            # Draw the grid state
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    cell = self.grid.cells[row][col]
                    cell_type = type(cell).__name__.replace("Cell", "")

                    if cell_type in self.cell_types:
                        color = self.cell_types[cell_type][1]

                        # Calculate cell position with border margin
                        x1 = col * self.cell_size + self.border_margin
                        y1 = row * self.cell_size + self.border_margin
                        x2 = x1 + self.cell_size - 1
                        y2 = y1 + self.cell_size - 1

                        # Only draw non-dead cells for cleaner GIF
                        if cell_type != "Dead":
                            draw.rectangle([x1, y1, x2, y2], fill=color)

            # Add frame number overlay
            frame_text = f"Frame {len(self.gif_frames) + 1}"
            draw.text((10, 10), frame_text, fill="white")

            self.gif_frames.append(frame)

        except Exception as e:
            print(f"Error capturing GIF frame: {e}")

    def save_gif(self):
        """Save the recorded frames as an animated GIF"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".gif",
            filetypes=[("GIF files", "*.gif"), ("All files", "*.*")],
            title="Save Animated GIF"
        )

        if filename:
            try:
                # Save as animated GIF
                duration = max(100, self.speed)  # Use simulation speed, minimum 100ms

                self.gif_frames[0].save(
                    filename,
                    save_all=True,
                    append_images=self.gif_frames[1:],
                    duration=duration,
                    loop=0  # Loop forever
                )

                messagebox.showinfo("Success",
                                  f"Animated GIF saved to {filename}\n"
                                  f"Frames: {len(self.gif_frames)}\n"
                                  f"Duration: {duration}ms per frame")

                # Clear frames to free memory
                self.gif_frames = []

            except Exception as e:
                messagebox.showerror("Error", f"Failed to save GIF: {str(e)}")

    def step_simulation(self):
        """Perform one simulation step"""
        if not self.running:
            self.game_runner.update()
            self.grid = self.game_runner.grid
            self.iteration_count += 1
            self.update_canvas()
            self.update_charts()

            # Capture frame for GIF if recording
            if self.recording_gif:
                self.capture_gif_frame()

    def run_simulation(self):
        """Main simulation loop"""
        while self.running:
            self.game_runner.update()
            self.grid = self.game_runner.grid
            self.iteration_count += 1

            # Update UI in main thread
            self.root.after(0, self.update_canvas)
            self.root.after(0, self.update_charts)

            # Capture frame for GIF if recording
            if self.recording_gif:
                self.root.after(0, self.capture_gif_frame)

            time.sleep(self.speed / 1000.0)

    def clear_grid(self):
        """Clear the grid"""
        if not self.running:
            self.grid = Grid(self.grid_size, self.grid_size)
            self.game_runner = GameRunner(self.grid)
            self.iteration_count = 0
            self.cell_history = []

            # Reset GIF recording
            if self.recording_gif:
                self.stop_gif_recording()

            self.update_canvas()
            self.update_charts()

    def on_cell_type_change(self, value):
        """Handle cell type selection change"""
        self.selected_cell_type = value

    def on_cancer_weight_change(self, event=None):
        """Handle cancer weight change"""
        try:
            weight = float(self.cancer_weight_var.get())
            # Clamp to valid range
            weight = max(0.0001, min(1.0, weight))

            # Update all existing cancer cells
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    cell = self.grid.cells[row][col]
                    if isinstance(cell, CancerCell):
                        cell.cancer_weighting = weight

            # Update the display value if it was clamped
            if weight != float(self.cancer_weight_var.get()):
                self.cancer_weight_var.set(str(weight))

        except ValueError:
            # Invalid input, ignore
            pass

    def on_cure_weight_change(self, event=None):
        """Handle cure weight change"""
        try:
            weight = float(self.cure_weight_var.get())
            # Clamp to valid range
            weight = max(0.0001, min(1.0, weight))

            # Update all existing cure cells
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    cell = self.grid.cells[row][col]
                    if isinstance(cell, CureCell):
                        cell.cure_weighting = weight

            # Update the display value if it was clamped
            if weight != float(self.cure_weight_var.get()):
                self.cure_weight_var.set(str(weight))

        except ValueError:
            # Invalid input, ignore
            pass

    def on_speed_change(self, value):
        """Handle speed slider change"""
        self.speed = int(value)
        self.speed_label.configure(text=f"{self.speed}ms")

    def on_size_change(self, value):
        """Handle grid size change with adaptive scaling"""
        if not self.running:
            new_size = int(value)
            if new_size != self.grid_size:
                self.grid_size = new_size
                self.size_label.configure(text=f"{self.grid_size}x{self.grid_size}")

                # Calculate adaptive cell size to keep canvas manageable
                max_canvas_dimension = self.max_canvas_size
                if self.grid_size * self.cell_size > max_canvas_dimension:
                    self.cell_size = max(1, max_canvas_dimension // self.grid_size)
                else:
                    # Use default cell size for smaller grids
                    self.cell_size = min(15, max(3, max_canvas_dimension // self.grid_size))

                # Update cell size label
                self.cell_size_label.configure(text=f"Cell size: {self.cell_size}px")

                # Calculate new canvas size including border margin
                grid_size = self.grid_size * self.cell_size
                new_canvas_width = grid_size + (2 * self.border_margin)
                new_canvas_height = grid_size + (2 * self.border_margin)

                # Update canvas size
                self.canvas.configure(width=new_canvas_width, height=new_canvas_height)

                # Update scrollable frame size
                scroll_width = min(new_canvas_width + 40, self.max_canvas_size)
                scroll_height = min(new_canvas_height + 40, self.max_canvas_size)
                self.canvas_scroll_frame.configure(width=scroll_width, height=scroll_height)

                # Recreate cell sprites with new size
                self.create_cell_sprites()

                # Create new grid
                self.grid = Grid(self.grid_size, self.grid_size)
                self.game_runner = GameRunner(self.grid)
                self.iteration_count = 0
                self.cell_history = []
                self.update_canvas()
                self.update_charts()

    def set_boundary(self, index, mode):
        """Set boundary condition for a specific edge"""
        self.boundary_modes[index] = mode
        # Update the grid's boundary modes
        if hasattr(self.grid, 'mode_list'):
            self.grid.mode_list = self.boundary_modes.copy()

        # Refresh visual indicators
        self.update_canvas()

    def save_grid(self):
        """Save current grid state and settings to CSV"""
        if not self.running:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )

            if filename:
                try:
                    with open(filename, 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile)

                        # Write settings
                        writer.writerow(["Settings"])
                        writer.writerow(["grid_size", self.grid_size])
                        writer.writerow(["speed", self.speed])
                        writer.writerow(["boundary_modes"] + self.boundary_modes)
                        writer.writerow(["cancer_weight", self.cancer_weight_var.get()])
                        writer.writerow(["cure_weight", self.cure_weight_var.get()])
                        writer.writerow([])  # Empty row separator

                        # Write grid data
                        writer.writerow(["Grid"])
                        for row in range(self.grid_size):
                            grid_row = []
                            for col in range(self.grid_size):
                                cell = self.grid.cells[row][col]
                                cell_type = type(cell).__name__.replace("Cell", "")
                                grid_row.append(cell_type)
                            writer.writerow(grid_row)

                    messagebox.showinfo("Success", f"Grid saved to {filename}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save grid: {str(e)}")

    def load_grid(self):
        """Load grid state and settings from CSV"""
        if not self.running:
            filename = filedialog.askopenfilename(
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )

            if filename:
                try:
                    with open(filename, 'r') as csvfile:
                        reader = csv.reader(csvfile)
                        rows = list(reader)

                    # Parse settings
                    settings_start = 0
                    for i, row in enumerate(rows):
                        if row and row[0] == "Settings":
                            settings_start = i + 1
                            break

                    # Load settings
                    for i in range(settings_start, len(rows)):
                        row = rows[i]
                        if not row:  # Empty row - end of settings
                            break

                        if row[0] == "grid_size":
                            self.grid_size = int(row[1])
                            self.size_slider.set(self.grid_size)
                            self.size_label.configure(text=f"{self.grid_size}x{self.grid_size}")

                            # Update cell size based on loaded grid size
                            max_canvas_dimension = self.max_canvas_size
                            if self.grid_size * self.cell_size > max_canvas_dimension:
                                self.cell_size = max(1, max_canvas_dimension // self.grid_size)
                            else:
                                # Use default cell size for smaller grids
                                self.cell_size = min(15, max(3, max_canvas_dimension // self.grid_size))

                            # Update cell size label
                            self.cell_size_label.configure(text=f"Cell size: {self.cell_size}px")
                        elif row[0] == "speed":
                            self.speed = int(row[1])
                            self.speed_slider.set(self.speed)
                            self.speed_label.configure(text=f"{self.speed}ms")
                        elif row[0] == "boundary_modes":
                            self.boundary_modes = row[1:5]
                            # Update boundary option menus
                            self.left_boundary.set(self.boundary_modes[0])
                            self.right_boundary.set(self.boundary_modes[1])
                            self.top_boundary.set(self.boundary_modes[2])
                            self.bottom_boundary.set(self.boundary_modes[3])
                        elif row[0] == "cancer_weight":
                            try:
                                weight = float(row[1])
                                weight = max(0.0001, min(1.0, weight))  # Clamp to valid range
                                self.cancer_weight_var.set(str(weight))
                            except (ValueError, IndexError):
                                self.cancer_weight_var.set("0.01")  # Default
                        elif row[0] == "cure_weight":
                            try:
                                weight = float(row[1])
                                weight = max(0.0001, min(1.0, weight))  # Clamp to valid range
                                self.cure_weight_var.set(str(weight))
                            except (ValueError, IndexError):
                                self.cure_weight_var.set("0.1")  # Default

                    # Find grid data
                    grid_start = 0
                    for i, row in enumerate(rows):
                        if row and row[0] == "Grid":
                            grid_start = i + 1
                            break

                    # Create new grid
                    self.grid = Grid(self.grid_size, self.grid_size)

                    # Load grid data
                    for row_idx in range(self.grid_size):
                        if grid_start + row_idx < len(rows):
                            row_data = rows[grid_start + row_idx]
                            for col_idx in range(min(len(row_data), self.grid_size)):
                                cell_type = row_data[col_idx]
                                if cell_type in self.cell_types:
                                    cell_class, _ = self.cell_types[cell_type]
                                    new_cell = cell_class(row_idx, col_idx, self.grid)

                                    # Apply loaded weight settings for special cells
                                    if isinstance(new_cell, CancerCell):
                                        try:
                                            new_cell.cancer_weighting = float(self.cancer_weight_var.get())
                                        except (ValueError, AttributeError):
                                            new_cell.cancer_weighting = 0.01
                                    elif isinstance(new_cell, CureCell):
                                        try:
                                            new_cell.cure_weighting = float(self.cure_weight_var.get())
                                        except (ValueError, AttributeError):
                                            new_cell.cure_weighting = 0.1

                                    self.grid.cells[row_idx][col_idx] = new_cell

                    # Update game runner and UI
                    self.game_runner = GameRunner(self.grid)
                    if hasattr(self.grid, 'mode_list'):
                        self.grid.mode_list = self.boundary_modes.copy()

                    # Resize canvas including border margin
                    grid_size = self.grid_size * self.cell_size
                    new_canvas_width = grid_size + (2 * self.border_margin)
                    new_canvas_height = grid_size + (2 * self.border_margin)
                    self.canvas.configure(width=new_canvas_width, height=new_canvas_height)

                    # Update scrollable frame size
                    scroll_width = min(new_canvas_width + 40, self.max_canvas_size)
                    scroll_height = min(new_canvas_height + 40, self.max_canvas_size)
                    self.canvas_scroll_frame.configure(width=scroll_width, height=scroll_height)

                    # Recreate cell sprites with new size
                    self.create_cell_sprites()

                    # Reset statistics for fresh start
                    self.iteration_count = 0
                    self.cell_history = []

                    # Reset GIF recording
                    if self.recording_gif:
                        self.stop_gif_recording()

                    self.update_canvas()
                    self.update_charts()

                    messagebox.showinfo("Success", f"Grid loaded from {filename}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load grid: {str(e)}")

    def on_window_resize(self, event):
        """Handle window resize events"""
        # Only handle resize events for the main window
        if event.widget == self.root:
            # Update max canvas size based on window size
            window_width = self.root.winfo_width()
            window_height = self.root.winfo_height()

            # Reserve space for controls and charts (approximately 400px for charts, 200px for controls)
            available_width = max(300, window_width - 600)
            available_height = max(300, window_height - 300)

            # Update max canvas size
            new_max_size = min(available_width, available_height)
            if abs(new_max_size - self.max_canvas_size) > 50:  # Only update if significant change
                self.max_canvas_size = new_max_size

                # Recalculate cell size if needed
                if self.grid_size * self.cell_size > self.max_canvas_size:
                    self.cell_size = max(1, self.max_canvas_size // self.grid_size)

                    # Update canvas and scroll frame
                    new_canvas_size = self.grid_size * self.cell_size
                    self.canvas.configure(width=new_canvas_size, height=new_canvas_size)

                    scroll_width = min(new_canvas_size + 40, self.max_canvas_size)
                    scroll_height = min(new_canvas_size + 40, self.max_canvas_size)
                    self.canvas_scroll_frame.configure(width=scroll_width, height=scroll_height)

                    # Recreate sprites and update display
                    self.create_cell_sprites()
                    self.update_canvas()

    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ConwayGUI()
    app.run()
