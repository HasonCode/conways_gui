import classes
import dearpygui.dearpygui as dpg
import time


class ConwayRenderer:
    def __init__(self, game_runner, cell_size=10, update_interval=0.1):
        """
        Initialize the Conway's Game of Life renderer using DearPyGUI

        Args:
            game_runner: GameRunner instance containing the grid
            cell_size: Size of each cell in pixels
            update_interval: Time between updates in seconds
        """
        self.game_runner = game_runner
        self.grid = game_runner.grid
        self.cell_size = cell_size
        self.update_interval = update_interval
        self.running = False
        self.paused = False
        self.generation = 0
        self.last_update_time = 0

        # Cell editing state
        self.selected_cell_type = "AliveCell"
        self.editing_enabled = True
        self.is_dragging = False
        self.last_painted_cell = None

        # Boundary mode state
        self.boundary_modes = ["default", "default", "default", "default"]  # [left, right, up, down]

        # Color mapping for different cell types
        self.cell_colors = {
            classes.DeadCell: [100, 100, 100, 255],      # Dark gray
            classes.AliveCell: [0, 255, 0, 255],         # Green
            classes.CancerCell: [255, 255, 255, 255],    # White
            classes.CureCell: [0, 0, 255, 255]           # Blue
        }

        # Calculate window dimensions
        self.window_width = self.grid.cols * self.cell_size + 250  # Extra space for controls
        self.window_height = self.grid.rows * self.cell_size + 150  # Extra space for controls

        # Initialize DearPyGUI
        dpg.create_context()
        self.setup_gui()

    def setup_gui(self):
        """Setup the DearPyGUI interface"""
        # Create viewport
        dpg.create_viewport(
            title="Conway's Game of Life",
            width=self.window_width,
            height=self.window_height
        )

        # Main window
        with dpg.window(label="Conway's Game of Life", tag="main_window"):
            # Control buttons
            with dpg.group(horizontal=True):
                dpg.add_button(label="Start", callback=self.start_simulation)
                dpg.add_button(label="Pause", callback=self.pause_simulation)
                dpg.add_button(label="Stop", callback=self.stop_simulation)
                dpg.add_button(label="Step", callback=self.step_simulation)
                dpg.add_button(label="Clear All", callback=self.clear_grid)

            # Speed control
            with dpg.group(horizontal=True):
                dpg.add_text("Speed:")
                dpg.add_slider_float(
                    label="Update Interval",
                    default_value=self.update_interval,
                    min_value=0.01,
                    max_value=2.0,
                    callback=self.update_speed,
                    tag="speed_slider"
                )

            # Cell type selection for editing
            with dpg.group(horizontal=True):
                dpg.add_text("Paint with:")
                dpg.add_combo(
                    ["DeadCell", "AliveCell", "CancerCell", "CureCell"],
                    default_value="AliveCell",
                    callback=self.change_cell_type,
                    tag="cell_type_combo"
                )
                dpg.add_text("(Click grid when stopped to paint)", color=[150, 150, 150])

            dpg.add_separator()

            # Boundary mode controls
            dpg.add_text("Boundary Modes:")

            with dpg.group(horizontal=True):
                dpg.add_text("Left:")
                dpg.add_combo(["default", "periodic", "mirror"],
                             default_value="default",
                             callback=lambda s, v: self.set_boundary_mode(0, v),
                             width=80, tag="left_boundary")

                dpg.add_text("Right:")
                dpg.add_combo(["default", "periodic", "mirror"],
                             default_value="default",
                             callback=lambda s, v: self.set_boundary_mode(1, v),
                             width=80, tag="right_boundary")

            with dpg.group(horizontal=True):
                dpg.add_text("Up:")
                dpg.add_combo(["default", "periodic", "mirror"],
                             default_value="default",
                             callback=lambda s, v: self.set_boundary_mode(2, v),
                             width=80, tag="up_boundary")

                dpg.add_text("Down:")
                dpg.add_combo(["default", "periodic", "mirror"],
                             default_value="default",
                             callback=lambda s, v: self.set_boundary_mode(3, v),
                             width=80, tag="down_boundary")

            # Boundary mode legend
            dpg.add_text("Legend:", color=[200, 200, 200])
            with dpg.group(horizontal=True):
                dpg.add_text("Gray=Default", color=[128, 128, 128])
                dpg.add_text("Green=Periodic", color=[0, 255, 0])
                dpg.add_text("Blue=Mirror", color=[0, 0, 255])

            dpg.add_separator()

            # Statistics
            dpg.add_text("Generation: 0", tag="generation_text")
            dpg.add_text("Alive Cells: 0", tag="alive_count")
            dpg.add_text("Cancer Cells: 0", tag="cancer_count")
            dpg.add_text("Cure Cells: 0", tag="cure_count")

            # Drawing canvas for the grid
            with dpg.drawlist(
                width=self.grid.cols * self.cell_size,
                height=self.grid.rows * self.cell_size,
                tag="grid_canvas"
            ):
                pass

        # Set main window as primary
        dpg.set_primary_window("main_window", True)

        # Add item-specific mouse handlers for the canvas only
        with dpg.item_handler_registry(tag="canvas_mouse_handler"):
            dpg.add_item_clicked_handler(callback=self.on_canvas_click)
            dpg.add_item_hover_handler(callback=self.on_canvas_hover)
        dpg.bind_item_handler_registry("grid_canvas", "canvas_mouse_handler")

        # Add global handlers only for drag operations
        with dpg.handler_registry():
            dpg.add_mouse_drag_handler(callback=self.on_mouse_drag)
            dpg.add_mouse_release_handler(callback=self.on_mouse_release)

        # Initial grid render
        self.render_grid()

    def render_grid(self):
        """Render the current state of the grid"""
        # Clear the canvas
        dpg.delete_item("grid_canvas", children_only=True)

        # Draw each cell
        for i in range(self.grid.rows):
            for j in range(self.grid.cols):
                cell = self.grid.get_cell(i, j)
                cell_type = type(cell)
                color = self.cell_colors.get(cell_type, [128, 128, 128, 255])

                # Calculate cell position
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                # Draw filled rectangle for the cell
                dpg.draw_rectangle(
                    (x1, y1), (x2, y2),
                    color=color,
                    fill=color,
                    parent="grid_canvas"
                )

        # Draw boundary mode indicators
        self.draw_boundary_indicators()

        # Update statistics
        self.update_statistics()

    def update_statistics(self):
        """Update the statistics display"""
        alive_count = 0
        cancer_count = 0
        cure_count = 0

        for row in self.grid.cells:
            for cell in row:
                if isinstance(cell, classes.AliveCell):
                    alive_count += 1
                elif isinstance(cell, classes.CancerCell):
                    cancer_count += 1
                elif isinstance(cell, classes.CureCell):
                    cure_count += 1

        dpg.set_value("alive_count", f"Alive Cells: {alive_count}")
        dpg.set_value("cancer_count", f"Cancer Cells: {cancer_count}")
        dpg.set_value("cure_count", f"Cure Cells: {cure_count}")

    def start_simulation(self):
        """Start the simulation"""
        if not self.running:
            self.running = True
            self.paused = False
            self.last_update_time = time.time()

    def pause_simulation(self):
        """Pause/unpause the simulation"""
        self.paused = not self.paused

    def stop_simulation(self):
        """Stop the simulation"""
        self.running = False
        self.paused = False

    def step_simulation(self):
        """Perform one step of the simulation"""
        self.game_runner.update()
        # Update grid reference in case it changed
        self.grid = self.game_runner.grid
        self.generation += 1
        dpg.set_value("generation_text", f"Generation: {self.generation}")
        self.render_grid()

    def clear_grid(self):
        """Clear all cells in the grid"""
        self.stop_simulation()
        for i in range(self.grid.rows):
            for j in range(self.grid.cols):
                self.grid.set_cell(classes.DeadCell(i, j, self.grid))
        self.generation = 0
        dpg.set_value("generation_text", f"Generation: {self.generation}")
        self.render_grid()

    def change_cell_type(self, _sender, value):
        """Change the selected cell type for painting"""
        self.selected_cell_type = value

    def update_speed(self, _sender, value):
        """Update the simulation speed"""
        self.update_interval = value

    def set_boundary_mode(self, boundary_index, mode):
        """Set boundary mode for a specific boundary"""
        self.boundary_modes[boundary_index] = mode
        # Update the grid's mode_list
        self.grid.mode_list = self.boundary_modes.copy()
        # Optional debug output (uncomment for troubleshooting)
        # print(f"Set boundary {['left', 'right', 'up', 'down'][boundary_index]} to {mode}")
        # print(f"Current boundary modes: {self.boundary_modes}")

    def draw_boundary_indicators(self):
        """Draw visual indicators for boundary modes around the grid"""
        grid_width = self.grid.cols * self.cell_size
        grid_height = self.grid.rows * self.cell_size

        # Define colors for different boundary modes
        mode_colors = {
            "default": [128, 128, 128, 255],  # Gray
            "periodic": [0, 255, 0, 255],     # Green
            "mirror": [0, 0, 255, 255]        # Blue
        }

        # Draw boundary indicators
        thickness = 4

        # Left boundary
        color = mode_colors.get(self.boundary_modes[0], [128, 128, 128, 255])
        dpg.draw_line(
            (0, 0), (0, grid_height),
            color=color, thickness=thickness,
            parent="grid_canvas"
        )

        # Right boundary
        color = mode_colors.get(self.boundary_modes[1], [128, 128, 128, 255])
        dpg.draw_line(
            (grid_width, 0), (grid_width, grid_height),
            color=color, thickness=thickness,
            parent="grid_canvas"
        )

        # Up boundary
        color = mode_colors.get(self.boundary_modes[2], [128, 128, 128, 255])
        dpg.draw_line(
            (0, 0), (grid_width, 0),
            color=color, thickness=thickness,
            parent="grid_canvas"
        )

        # Down boundary
        color = mode_colors.get(self.boundary_modes[3], [128, 128, 128, 255])
        dpg.draw_line(
            (0, grid_height), (grid_width, grid_height),
            color=color, thickness=thickness,
            parent="grid_canvas"
        )

    def paint_cell_at_position(self, mouse_pos):
        """Helper method to paint a cell at the given mouse position"""
        if self.running:
            return False  # Don't allow editing while simulation is running

        # Get the actual canvas rectangle (accounts for all GUI elements above it)
        canvas_rect_min = dpg.get_item_rect_min("grid_canvas")
        canvas_rect_max = dpg.get_item_rect_max("grid_canvas")

        # Calculate relative position within the canvas
        rel_x = mouse_pos[0] - canvas_rect_min[0]
        rel_y = mouse_pos[1] - canvas_rect_min[1]

        # Check if position is within canvas bounds
        canvas_width = canvas_rect_max[0] - canvas_rect_min[0]
        canvas_height = canvas_rect_max[1] - canvas_rect_min[1]

        if (0 <= rel_x < canvas_width and 0 <= rel_y < canvas_height):

            # Calculate grid coordinates
            grid_col = int(rel_x // self.cell_size)
            grid_row = int(rel_y // self.cell_size)+1

            # Ensure coordinates are within bounds
            if (0 <= grid_row < self.grid.rows and 0 <= grid_col < self.grid.cols):

                # Check if this is the same cell we just painted (avoid redundant painting)
                current_cell = (grid_row, grid_col)
                if current_cell == self.last_painted_cell:
                    return True  # Same cell, but still valid

                self.last_painted_cell = current_cell

                # Create the appropriate cell type
                if self.selected_cell_type == "DeadCell":
                    new_cell = classes.DeadCell(grid_row, grid_col, self.grid)
                elif self.selected_cell_type == "AliveCell":
                    new_cell = classes.AliveCell(grid_row, grid_col, self.grid)
                elif self.selected_cell_type == "CancerCell":
                    new_cell = classes.CancerCell(grid_row, grid_col, self.grid)
                elif self.selected_cell_type == "CureCell":
                    new_cell = classes.CureCell(grid_row, grid_col, self.grid)
                else:
                    return False

                # Set the cell in the grid
                self.grid.set_cell(new_cell)
                self.render_grid()
                return True

        return False

    def on_canvas_click(self, _sender, _app_data):
        """Handle clicks specifically on the canvas"""
        if self.running:
            return  # Don't allow editing while simulation is running

        mouse_pos = dpg.get_mouse_pos()
        self.is_dragging = True
        self.last_painted_cell = None  # Reset for new painting session
        self.paint_cell_at_position(mouse_pos)

    def on_canvas_hover(self, _sender, _app_data):
        """Handle hover events on canvas - used for drag painting"""
        if self.is_dragging and not self.running:
            mouse_pos = dpg.get_mouse_pos()
            self.paint_cell_at_position(mouse_pos)

    def on_mouse_drag(self, _sender, _app_data):
        """Handle mouse dragging for continuous cell painting"""
        if not self.is_dragging:
            return

        mouse_pos = dpg.get_mouse_pos()
        self.paint_cell_at_position(mouse_pos)

    def on_mouse_release(self, _sender, _app_data):
        """Handle mouse release to stop dragging"""
        self.is_dragging = False
        self.last_painted_cell = None

    def run(self):
        """Start the GUI and show the window"""
        try:
            dpg.setup_dearpygui()
            dpg.show_viewport()

            # Render initial state
            self.render_grid()

            # Start the DearPyGUI render loop with simulation updates
            while dpg.is_dearpygui_running():
                try:
                    # Handle simulation updates in the main thread
                    current_time = time.time()
                    if (self.running and not self.paused and
                        current_time - self.last_update_time >= self.update_interval):

                        self.game_runner.update()
                        # Update grid reference in case it changed
                        self.grid = self.game_runner.grid
                        self.generation += 1
                        dpg.set_value("generation_text", f"Generation: {self.generation}")
                        self.render_grid()
                        self.last_update_time = current_time

                    dpg.render_dearpygui_frame()
                except Exception as e:
                    print(f"Error in render loop: {e}")
                    break

        except Exception as e:
            print(f"Error in GUI setup: {e}")
        finally:
            # Cleanup
            self.stop_simulation()
            try:
                dpg.destroy_context()
            except:
                pass


def create_sample_grid():
    """Create a sample grid with some initial patterns"""
    grid = classes.Grid(30, 30)

    # Add some alive cells (classic glider pattern)
    grid.set_cell(classes.AliveCell(1, 2, grid))
    grid.set_cell(classes.AliveCell(2, 3, grid))
    grid.set_cell(classes.AliveCell(3, 1, grid))
    grid.set_cell(classes.AliveCell(3, 2, grid))
    grid.set_cell(classes.AliveCell(3, 3, grid))

    # Add some cancer cells
    grid.set_cell(classes.CancerCell(10, 10, grid))
    grid.set_cell(classes.CancerCell(15, 20, grid))

    # Add a cure cell
    grid.set_cell(classes.CureCell(20, 15, grid))

    return grid


if __name__ == "__main__":
    # Create a sample grid and game runner
    grid = create_sample_grid()
    runner = classes.GameRunner(grid)

    # Create and run the renderer
    renderer = ConwayRenderer(runner, cell_size=15, update_interval=0.2)
    renderer.run()