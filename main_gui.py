#!/usr/bin/env python3
"""
Modified main.py that uses the GUI renderer instead of console output
"""

import classes
from renderer import ConwayRenderer


def main():
    """Main function using the same setup as your original main.py but with GUI"""
    # Create the same grid setup as in your main.py
    grid = classes.Grid(30, 30)
    
    # Same initial pattern as your main.py
    grid.set_cell(classes.AliveCell(3, 3, grid))
    grid.set_cell(classes.AliveCell(3, 4, grid))
    grid.set_cell(classes.AliveCell(3, 5, grid))
    grid.set_cell(classes.AliveCell(4, 3, grid))
    grid.set_cell(classes.AliveCell(5, 4, grid))
    
    # Same cancer cells as your main.py
    grid.set_cell(classes.CancerCell(2, 20, grid))
    grid.set_cell(classes.CancerCell(20, 2, grid))
    
    # Create game runner
    runner = classes.GameRunner(grid)
    
    # Instead of runner.run(100), use the GUI renderer
    print("Starting Conway's Game of Life GUI...")
    print("Use the Start button to begin the simulation!")
    
    renderer = ConwayRenderer(runner, cell_size=15, update_interval=0.1)
    renderer.run()


if __name__ == "__main__":
    main()
