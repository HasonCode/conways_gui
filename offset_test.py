#!/usr/bin/env python3
"""
Test script to verify click offset accuracy
Creates a small grid with clear visual markers to test click precision
"""

import classes
from renderer import ConwayRenderer


def create_offset_test_grid():
    """Create a small test grid with markers at specific positions"""
    grid = classes.Grid(10, 10)
    
    # Place markers at corners and center to help with offset testing
    # Top-left corner (0,0)
    grid.set_cell(classes.AliveCell(0, 0, grid))
    
    # Top-right corner (0,9)
    grid.set_cell(classes.CancerCell(0, 9, grid))
    
    # Bottom-left corner (9,0)
    grid.set_cell(classes.CureCell(9, 0, grid))
    
    # Bottom-right corner (9,9)
    grid.set_cell(classes.AliveCell(9, 9, grid))
    
    # Center (5,5)
    grid.set_cell(classes.CancerCell(5, 5, grid))
    
    return grid


def main():
    """Test click offset accuracy"""
    print("Creating offset test grid...")
    grid = create_offset_test_grid()
    
    print("Initializing game runner...")
    runner = classes.GameRunner(grid)
    
    print("Starting offset test...")
    print("\nOffset Test Instructions:")
    print("The grid has markers at:")
    print("- (0,0) top-left: Green (AliveCell)")
    print("- (0,9) top-right: White (CancerCell)")
    print("- (9,0) bottom-left: Blue (CureCell)")
    print("- (9,9) bottom-right: Green (AliveCell)")
    print("- (5,5) center: White (CancerCell)")
    print("\nTry clicking on these markers and see if the debug output matches!")
    print("Also try clicking on empty cells and verify the coordinates.")
    
    # Use larger cells for easier testing
    renderer = ConwayRenderer(runner, cell_size=30, update_interval=1.0)
    renderer.run()


if __name__ == "__main__":
    main()
