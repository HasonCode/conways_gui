# Conway's Game of Life GUI Renderer

This implementation provides a graphical user interface for Conway's Game of Life using DearPyGUI, supporting both classic Conway rules and extended cell types (Cancer and Cure cells).

## Features

### Visual Rendering
- **Real-time grid visualization** with color-coded cell types
- **Smooth animation** with adjustable speed
- **Statistics display** showing cell counts and generation number

### Cell Types & Colors
- **Dead Cells** (Dark Gray): Empty cells that can become alive
- **Alive Cells** (Green): Standard Conway's Game of Life cells
- **Cancer Cells** (White): Special cells that can spread to neighbors
- **Cure Cells** (Blue): Special cells that can eliminate cancer cells

### Interactive Controls
- **Start**: Begin automatic simulation
- **Pause**: Pause/unpause the running simulation
- **Stop**: Stop the simulation completely
- **Step**: Advance exactly one generation manually
- **Clear All**: Clear the entire grid to start fresh
- **Speed Slider**: Adjust animation speed (0.01 - 2.0 seconds per frame)

### Interactive Cell Editing
- **Cell Type Dropdown**: Select which type of cell to paint (DeadCell, AliveCell, CancerCell, CureCell)
- **Grid Clicking**: Click on any grid cell when simulation is stopped to paint it with the selected cell type
- **Grid Dragging**: Click and drag across multiple cells to paint them quickly in one motion
- **Real-time Updates**: Changes are immediately visible and affect the next simulation step
- **Smart Painting**: Avoids redundant painting of the same cell during a single drag operation

### Boundary Mode Controls
- **Individual Edge Control**: Set boundary behavior for each edge independently (Left, Right, Up, Down)
- **Three Boundary Types**:
  - **Default**: Standard Conway's rules - cells outside the grid are considered dead
  - **Periodic**: Grid wraps around - cells on opposite edges are neighbors (torus topology)
  - **Mirror**: Edge cells are mirrored - boundary acts like a reflective surface
- **Visual Indicators**: Colored border lines show the current boundary mode for each edge:
  - Gray = Default boundary
  - Green = Periodic boundary
  - Blue = Mirror boundary
- **Real-time Changes**: Boundary modes can be changed during simulation and take effect immediately

## Usage

### Basic Usage
```python
import classes
from renderer import ConwayRenderer

# Create your grid and game runner
grid = classes.Grid(30, 30)
# ... add cells to your grid ...
runner = classes.GameRunner(grid)

# Create and run the GUI renderer
renderer = ConwayRenderer(runner, cell_size=15, update_interval=0.1)
renderer.run()
```

### Running the Examples

1. **Demo with various patterns**:
   ```bash
   python gui_demo.py
   ```

2. **Your original main.py setup with GUI**:
   ```bash
   python main_gui.py
   ```

3. **Basic renderer test**:
   ```bash
   python renderer.py
   ```

4. **Simple test with instructions**:
   ```bash
   python test_renderer.py
   ```

### Constructor Parameters

```python
ConwayRenderer(game_runner, cell_size=10, update_interval=0.1)
```

- `game_runner`: Your `GameRunner` instance containing the grid
- `cell_size`: Size of each cell in pixels (default: 10)
- `update_interval`: Time between updates in seconds (default: 0.1)

## Implementation Details

### Architecture
- **Main Thread**: Handles GUI rendering and user interaction
- **Simulation Thread**: Runs the Conway's Game of Life logic
- **Thread-Safe Updates**: Statistics and grid state are updated safely

### Grid Rendering
The renderer loops through each cell in the grid and:
1. Determines the cell type using `isinstance()`
2. Maps the cell type to a color using the `cell_colors` dictionary
3. Draws a filled rectangle for each cell using DearPyGUI's drawing API

### Performance
- Optimized for grids up to 50x50 cells
- Uses efficient rectangle drawing for cell visualization
- Separate thread for simulation prevents GUI freezing

## Dependencies

- `dearpygui`: Modern GUI framework for Python
- Your existing `classes.py` module with Conway's implementation

Install dependencies:
```bash
pip install dearpygui
```

## Customization

### Adding New Cell Types
1. Add your new cell class to `classes.py`
2. Add a color mapping in `ConwayRenderer.cell_colors`
3. Update statistics tracking in `update_statistics()` if needed

### Changing Colors
Modify the `cell_colors` dictionary in the `ConwayRenderer` constructor:
```python
self.cell_colors = {
    classes.DeadCell: [R, G, B, A],      # RGBA values 0-255
    classes.AliveCell: [R, G, B, A],
    # ... etc
}
```

### Window Size
The window size is automatically calculated based on:
- Grid dimensions (`grid.rows` × `grid.cols`)
- Cell size (`cell_size` parameter)
- Extra space for controls (200px width, 100px height)

## Troubleshooting

### Common Issues
1. **GUI doesn't appear**: Make sure DearPyGUI is installed correctly
2. **Simulation runs too fast/slow**: Adjust the speed slider or `update_interval`
3. **Grid appears cut off**: Increase `cell_size` or check grid dimensions

### Performance Tips
- For large grids (>50x50), consider reducing `cell_size`
- Increase `update_interval` for slower machines
- Use the Step button for detailed analysis of specific generations
