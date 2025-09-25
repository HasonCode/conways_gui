# Conway's Game of Life - Advanced GUI

A comprehensive GUI implementation of Conway's Game of Life using customtkinter with extended features including multiple cell types, boundary conditions, and real-time statistics.

## Features

### 1. Interactive Canvas
- **Click and Drag**: Click on the canvas to place individual cells, or drag to paint multiple cells
- **Custom Cell Sprites**: Visual representation of different cell types with distinct colors and patterns
- **Grid Display**: Clear grid lines showing cell boundaries

### 2. Cell Types
- **Dead Cell** (🟥): Standard dead cells that can become alive with 3 neighbors
- **Alive Cell** (🟩): Standard living cells following Conway's rules
- **Cancer Cell** (⬜): Aggressive cells that spread to dead neighbors
- **Cure Cell** (🟦): Special cells that can eliminate cancer cells

### 3. Boundary Conditions
Configure how the grid edges behave:
- **Normal**: Cells outside the grid are considered dead
- **Periodic**: Grid wraps around (torus topology)
- **Mirror**: Edge cells are reflected back

Each edge (left, right, top, bottom) can be configured independently.

### 4. Simulation Controls
- **Start/Stop**: Begin or halt the simulation
- **Step**: Advance the simulation by one generation
- **Speed Slider**: Control simulation speed (10ms to 1000ms per iteration)
- **Clear**: Reset the grid to all dead cells

### 5. Cell Weight Controls
- **Cancer Weight**: Adjust cancer cell aggressiveness (0.0001 - 1.0)
- **Cure Weight**: Adjust cure cell healing strength (0.0001 - 1.0)
- **Real-time Updates**: Changes apply immediately to existing cells
- **Save/Load**: Weights are preserved in grid save files
- **Dynamic Behavior**: Higher weights create stronger effects during simulation

### 6. Grid Configuration
- **Size Slider**: Adjust grid dimensions (10x10 to 100x100)
- **Adaptive Scaling**: Cell size automatically adjusts to keep the interface manageable
- **Scrollable Canvas**: Large grids are contained in a scrollable area
- **Real-time Resize**: Grid updates immediately when size changes
- **Cell Size Display**: Shows current cell pixel size for reference

### 7. File Operations
- **Save Grid**: Export current grid state and settings to CSV format
- **Load Grid**: Import previously saved grid configurations
- **Save Graph**: Export line graph as high-quality PNG image (separate button)
- **Record GIF**: Capture simulation frames and export as animated GIF
- **Grid Focus**: CSV files contain grid state, settings, boundary conditions, and cell weights
- **Graph Export**: 300 DPI PNG with metadata, styling, and simulation parameters
- **GIF Animation**: Records up to 300 frames with frame counter and timing control
- **Settings Preservation**: Boundary conditions, speed, grid size, and cell weights are saved/loaded

### 8. Real-time Statistics
- **Pie Chart**: Shows current distribution of cell types
- **Line Graph**: Tracks cell population over time during simulation
- **Live Updates**: Charts update automatically during simulation

## Usage Instructions

### Running the GUI
```bash
python test_conway_gui.py
```

### Basic Operations
1. **Placing Cells**: 
   - Select a cell type from the dropdown menu
   - Click on the canvas to place individual cells
   - Drag across the canvas to paint multiple cells

2. **Starting Simulation**:
   - Click "Start" to begin automatic simulation
   - Use the speed slider to adjust iteration speed
   - Click "Stop" to halt simulation
   - Use "Step" for manual advancement

3. **Configuring Boundaries**:
   - Use the dropdown menus around the grid to set boundary conditions
   - Each edge can be set independently
   - Changes take effect immediately

4. **Saving/Loading**:
   - Click "Save Grid" to export current state
   - Click "Load Grid" to import a saved configuration
   - Files are saved in CSV format for easy editing

### Advanced Features

#### Cell Type Behaviors
- **Dead → Alive**: Exactly 3 alive neighbors
- **Alive → Dead**: Less than 2 or more than 3 alive neighbors
- **Cancer Spread**: 10% chance to infect dead neighbors
- **Cure Generation**: 50% chance when 5+ cancer neighbors present
- **Cancer Death**: Dies when touching cure cells or 7+ cancer neighbors

#### Boundary Mode Effects
- **Normal**: Standard Conway's rules with dead boundary
- **Periodic**: Creates seamless patterns that wrap around edges
- **Mirror**: Reflects patterns at boundaries, creating symmetrical effects

#### Performance Tips
- Larger grids (50x50+) may slow down on older hardware
- Reduce speed for better visualization of complex patterns
- Use smaller grids for faster iteration and testing

## File Format

### CSV Structure
```csv
Settings
grid_size,30
speed,100
boundary_modes,normal,normal,normal,normal

Grid
Dead,Dead,Alive,Dead,...
Dead,Alive,Alive,Alive,...
...
```

## Dependencies
- customtkinter
- matplotlib
- PIL (Pillow)
- numpy
- tkinter (built-in)

## Installation
```bash
pip install customtkinter matplotlib pillow numpy
```

## Examples

### Classic Patterns
Try loading these classic Conway's Game of Life patterns:
- **Glider**: Small moving pattern
- **Blinker**: Simple oscillator
- **Block**: Static pattern

### Extended Patterns
Experiment with cancer and cure cells:
- Place cancer cells to see aggressive spreading
- Add cure cells to create containment zones
- Mix all cell types for complex interactions

## Troubleshooting

### Common Issues
1. **GUI doesn't start**: Ensure all dependencies are installed
2. **Slow performance**: Reduce grid size or increase speed interval
3. **Charts not updating**: Check that matplotlib backend is properly configured
4. **File save/load errors**: Ensure write permissions in the directory

### Performance Optimization
- Use grid sizes under 50x50 for smooth real-time simulation
- Close other applications if experiencing lag
- Adjust speed slider to balance visualization and performance
