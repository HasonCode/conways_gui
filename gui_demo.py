#!/usr/bin/env python3
"""
Conway's Game of Life GUI Demo
This script demonstrates how to use the DearPyGUI renderer with your existing Conway's implementation.
"""

import classes
from renderer import ConwayRenderer


def create_demo_grid():
    """Create a demo grid with various patterns and cell types"""
    grid = classes.Grid(40, 40)
    
    # Classic Conway patterns
    
    # Glider pattern (top-left)
    grid.set_cell(classes.AliveCell(1, 2, grid))
    grid.set_cell(classes.AliveCell(2, 3, grid))
    grid.set_cell(classes.AliveCell(3, 1, grid))
    grid.set_cell(classes.AliveCell(3, 2, grid))
    grid.set_cell(classes.AliveCell(3, 3, grid))
    
    # Blinker pattern (oscillator)
    grid.set_cell(classes.AliveCell(10, 10, grid))
    grid.set_cell(classes.AliveCell(10, 11, grid))
    grid.set_cell(classes.AliveCell(10, 12, grid))
    
    # Block pattern (still life)
    grid.set_cell(classes.AliveCell(15, 15, grid))
    grid.set_cell(classes.AliveCell(15, 16, grid))
    grid.set_cell(classes.AliveCell(16, 15, grid))
    grid.set_cell(classes.AliveCell(16, 16, grid))
    
    # Extended Conway features (your custom cell types)
    
    # Cancer cells scattered around
    grid.set_cell(classes.CancerCell(5, 20, grid))
    grid.set_cell(classes.CancerCell(25, 10, grid))
    grid.set_cell(classes.CancerCell(30, 30, grid))
    
    # Cure cells to counteract cancer
    grid.set_cell(classes.CureCell(20, 25, grid))
    grid.set_cell(classes.CureCell(35, 5, grid))
    
    # Random alive cells for more interesting dynamics
    import random
    random.seed(42)  # For reproducible results
    for _ in range(20):
        row = random.randint(0, 39)
        col = random.randint(0, 39)
        if isinstance(grid.get_cell(row, col), classes.DeadCell):
            grid.set_cell(classes.AliveCell(row, col, grid))
    
    return grid


def main():
    """Main function to run the Conway's Game of Life GUI"""
    print("Creating Conway's Game of Life grid...")
    grid = create_demo_grid()
    
    print("Initializing game runner...")
    runner = classes.GameRunner(grid)
    
    print("Starting GUI renderer...")
    print("\nControls:")
    print("- Start: Begin automatic simulation")
    print("- Pause: Pause/unpause the simulation")
    print("- Stop: Stop the simulation")
    print("- Step: Advance one generation manually")
    print("- Clear All: Clear the entire grid")
    print("- Speed slider: Adjust simulation speed")
    print("\nInteractive Editing:")
    print("- Select cell type from dropdown")
    print("- Click on grid cells when simulation is stopped to paint")
    print("- DRAG across multiple cells to paint them quickly!")
    print("- Try different patterns and see how they evolve!")
    print("\nCell Types:")
    print("- Dark Gray: Dead cells")
    print("- Green: Alive cells (standard Conway)")
    print("- White: Cancer cells (spread to neighbors)")
    print("- Blue: Cure cells (eliminate cancer)")
    
    # Create and run the renderer
    # cell_size=12 makes cells a bit larger for better visibility
    # update_interval=0.15 gives a nice animation speed
    renderer = ConwayRenderer(runner, cell_size=12, update_interval=0.15)
    renderer.run()


if __name__ == "__main__":
    main()
