import random
import time
import os
class Location:
    def __init__(self, i:int, j:int):
        self.i = i
        self.j = j
    
    @property
    def i(self):
        return self._i
    
    @i.setter
    def i(self, value):
        self._i = value

    @i.getter
    def i(self):
        return self._i

    @property
    def j(self):
        return self._j
    
    @j.setter
    def j(self, value):
        self._j = value

    @j.getter
    def j(self):
        return self._j
    
    def set_location(self, i, j):
        self.i = i
        self.j = j

    

class ImplCell:
    def __init__(self, location, grid):
        self.location = location
        self.grid = grid
    
    @property
    def location(self):
        return self._location
    
    @location.setter
    def location(self, value):
        self._location = value

    @location.getter
    def location(self):
        return self._location

    @property
    def grid(self):
        return self._grid
    
    @grid.setter
    def grid(self, value):
        self._grid = value
    
    @grid.getter
    def grid(self):
        return self._grid

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
        if cancer_neighbors>=1:
            if random.random()<cancer_chance: 
                return CancerCell(self.location.i, self.location.j, self.grid)
        if cancer_neighbors>=5:
            if random.random()<curechance:
                return CureCell(self.location.i, self.location.j, self.grid)

        return DeadCell(self.location.i, self.location.j, self.grid)
    
    def __str__(self):
        return "🟥"

class AliveCell(ImplCell):
    def __init__(self, row, col, grid):
        super().__init__(Location(row, col), grid)    

    def process(self):
        neighbors = self.grid.count_neighbors(self.location.i, self.location.j)
        cancer_neighbor = self.grid.count_neighbors(self.location.i, self.location.j, CancerCell)
        if neighbors in [2,3]:
            return AliveCell(self.location.i, self.location.j, self.grid)
        return DeadCell(self.location.i, self.location.j, self.grid)

    def clone(self, grid):
        return AliveCell(self.location.i, self.location.j, grid)

    def __str__(self):
        return "🟩"
    
class CancerCell(ImplCell):
    def __init__(self, row, col, grid, weighting):
        self.cancer_weighting = weighting
        super().__init__(Location(row, col), grid) 
    
    def process(self):
        cells = self.grid.cells
        loc = self.location
        cure_neighbors = self.grid.count_neighbors(loc.i, loc.j, CureCell)
        cancer_neighbors = self.grid.count_neighbors(loc.i, loc.j, CancerCell)
        if cure_neighbors>=1 or cancer_neighbors>=7:
            return DeadCell(loc.i, loc.j, self.grid)
        return CancerCell(loc.i, loc.j, self.grid)
    
    def clone(self, grid):
        return CancerCell(self.location.i, self.location.j, grid)
    def __str__(self):
        return "⬜"
    

class CureCell(ImplCell):
    def __init__(self, row, col, grid, weighting = 0.1):
        self.cure_weighting = weighting
        super().__init__(Location(row, col), grid) 
    
    def process(self):
        cells = self.grid.cells
        loc = self.location
        neighbors = self.grid.count_neighbors(loc.i, loc.j, CureCell)
        dead_neighbors = self.grid.count_neighbors(loc.i, loc.j, DeadCell)
        if dead_neighbors >= 6:
            return DeadCell(loc.i, loc.j, self.grid)
        if neighbors>=3:
            return DeadCell(loc.i, loc.j, self.grid)
        return CureCell(loc.i, loc.j, self.grid)
    
    def __str__(self):
        return "🟦"
        
    def clone(self, grid):
        return CureCell(self.location.i, self.location.j, grid)

        
        


class Grid:
    def __init__(self, rows, cols, mode_list = ["","","",""]):
        self.rows = rows
        self.cols = cols
        self.mode_list = mode_list
        self.cells = [[DeadCell(j,i,self) for i in range(cols)] for j in range(rows)]
    
    def set_cell(self, cell):
        self.cells[cell.location.i][cell.location.j] = cell
    
    def set_left(self, mode):
        self.mode_list[0] = mode

    def set_right(self, mode):
        self.mode_list[2] = mode

    def set_up(self, mode):
        self.mode_list[2] = mode

    def set_down(self, mode):
        self.mode_list[3] = mode


    def clone(self):
        new_grid = Grid(self.rows, self.cols, self.mode_list)
        for i in range(len(self.cells)):
            for j in range(len(self.cells[-1])):
                new_grid.cells[i][j] = self.cells[i][j]
        return new_grid
                

    def get_cell(self, row, col):
        return self.cells[row][col]

    def check_left(self, col, mode = "default"):
        if mode == "periodic":
            return col%len(self.cells[0])
        elif mode == "mirror" and col < 0:
            return 0
        elif col < 0:
            return None
        return col
    
    def check_right(self, col, mode = "default"):
        if mode == "periodic":
            return col%len(self.cells[0])
        elif mode == "mirror" and col > len(self.cells[0]) - 1:
            return len(self.cells[0]) - 1
        elif col > len(self.cells[0]) - 1:
            return None
        return col

    def row_processor(self, row, i, mode_list):
        if i < row:
            return self.check_up(i, mode_list[2])
        elif i > row:
            return self.check_down(i, mode_list[3])
        else:
            return i


    def check_up(self, row, mode = "default"):
        if mode == "periodic":
            return row%len(self.cells)
        elif mode == "mirror" and row < 0:
            return 0
        elif row < 0:
            return None
        return row
    
    def check_down(self, row, mode = "default"):
        if mode == "periodic":
            return row%len(self.cells)
        elif mode == "mirror" and row > len(self.cells) - 1:
            return len(self.cells) - 1
        elif row > len(self.cells) - 1:
            return None
        return row

    def col_processor(self, col, j, mode_list):
        if j < col:
            return self.check_left(j, mode_list[0])
        elif j > col:
            return self.check_right(j, mode_list[1])
        else:
            return j

    def count_neighbors(self, row, col, cell_type = AliveCell, mode_list = ["","","",""]):
        count_cells = 0
        for i in range(row-1, row+2):
            row_val = self.row_processor(row, i, mode_list)
            for j in range(col-1, col+2):
                col_val = self.col_processor(col, j, mode_list)
                if row_val != None and col_val != None:
                    if isinstance(self.cells[row_val][col_val], cell_type):
                        count_cells += 1
        if (isinstance(self.cells[row][col], AliveCell)):
            count_cells -= 1
        return count_cells


class GameRunner:
    def __init__(self, grid):
        self.grid = grid
    
    def update(self):
        temp_grid = self.grid.clone()
        for row in self.grid.cells:
            for cell in row:
                next = cell.process()
                next.grid = temp_grid
                temp_grid.set_cell(next)
        self.grid = temp_grid

    def print_grid(self):
        for row in self.grid.cells:
            row_str = ""
            for cell in row:
                row_str += cell.__str__()
            print(row_str)
    
    def run(self, iterations = 1):
        self.print_grid()
        for i in range(iterations):
            time.sleep(0.1)
            os.system("cls")
            self.update()
            self.print_grid()