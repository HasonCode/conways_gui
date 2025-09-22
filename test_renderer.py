#!/usr/bin/env python3
"""
Test script for the Conway's Game of Life renderer
This script creates a simple test setup to verify both simulation updates and interactive editing work correctly.
"""

import classes
from renderer import ConwayRenderer


def create_test_grid():
    """Create a simple test grid with a few patterns"""
    grid = classes.Grid(20, 20)
    
    # Add a simple blinker pattern (oscillates between horizontal and vertical)
    grid.set_cell(classes.AliveCell(5, 5, grid))
    grid.set_cell(classes.AliveCell(5, 6, grid))
    grid.set_cell(classes.AliveCell(5, 7, grid))
    
    # Add a block pattern (stable)
    grid.set_cell(classes.AliveCell(10, 10, grid))
    grid.set_cell(classes.AliveCell(10, 11, grid))
    grid.set_cell(classes.AliveCell(11, 10, grid))
    grid.set_cell(classes.AliveCell(11, 11, grid))
    
    # Add a cancer cell to test extended functionality
    grid.set_cell(classes.CancerCell(15, 15, grid))
    
    return grid


def main():
    """Test the renderer with a simple grid"""
    print("Creating test grid...")
    grid = create_test_grid()
    
    print("Initializing game runner...")
    runner = classes.GameRunner(grid)
    
    print("Starting renderer...")
    print("\nTest Instructions:")
    print("1. Click 'Start' to begin simulation - you should see the blinker oscillate")
    print("2. Click 'Stop' to stop simulation")
    print("3. Select different cell types from the dropdown")
    print("4. Click on grid cells to paint them")
    print("5. DRAG across grid cells to paint multiple cells at once!")
    print("6. Try different BOUNDARY MODES (default/periodic/mirror) for each edge!")
    print("7. Watch the colored border lines show the boundary mode")
    print("8. Click 'Step' to advance one generation manually")
    print("9. Click 'Clear All' to clear the grid")
    print("10. Use the speed slider to adjust animation speed")
    
    # Create renderer with larger cells for easier clicking
    renderer = ConwayRenderer(runner, cell_size=20, update_interval=0.5)
    renderer.run()


if __name__ == "__main__":
    main()
