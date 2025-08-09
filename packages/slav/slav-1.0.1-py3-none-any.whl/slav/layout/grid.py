from typing import List, Tuple, Optional
from ..core.component import Component


class Grid(Component):
    def __init__(self, rows: int, cols: int, x: int = 0, y: int = 0,
                 width: int = 10, height: int = 10,
                 gap: int = 1, padding: int = 0):
        super().__init__(x, y, width, height)
        self.rows = rows
        self.cols = cols
        self.gap = gap
        self.padding = padding
        self.grid: List[List[Optional[Component]]] = [[None for _ in range(cols)] for _ in range(rows)]
        
    def add_child_at(self, child: Component, row: int, col: int, 
                     row_span: int = 1, col_span: int = 1):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            child.parent = self
            child._grid_row = row
            child._grid_col = col
            child._grid_row_span = row_span
            child._grid_col_span = col_span
            
            for r in range(row, min(row + row_span, self.rows)):
                for c in range(col, min(col + col_span, self.cols)):
                    self.grid[r][c] = child
                    
            if child not in self.children:
                self.children.append(child)
                
            self._layout_children()
            
    def remove_child_at(self, row: int, col: int):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            child = self.grid[row][col]
            if child:
                for r in range(self.rows):
                    for c in range(self.cols):
                        if self.grid[r][c] == child:
                            self.grid[r][c] = None
                            
                if child in self.children:
                    child.parent = None
                    self.children.remove(child)
                    
                self._layout_children()
                
    def resize(self, width: int, height: int):
        super().resize(width, height)
        self._layout_children()
        
    def _layout_children(self):
        content_width = self.width - 2 * self.padding
        content_height = self.height - 2 * self.padding
        
        total_gap_width = (self.cols - 1) * self.gap
        total_gap_height = (self.rows - 1) * self.gap
        
        cell_width = (content_width - total_gap_width) // self.cols
        cell_height = (content_height - total_gap_height) // self.rows
        
        positioned_children = set()
        
        for child in self.children:
            if child in positioned_children:
                continue
                
            row = getattr(child, '_grid_row', 0)
            col = getattr(child, '_grid_col', 0)
            row_span = getattr(child, '_grid_row_span', 1)
            col_span = getattr(child, '_grid_col_span', 1)
            
            x = self.padding + col * (cell_width + self.gap)
            y = self.padding + row * (cell_height + self.gap)
            
            width = cell_width * col_span + self.gap * (col_span - 1)
            height = cell_height * row_span + self.gap * (row_span - 1)
            
            child.x = x
            child.y = y
            child.width = width
            child.height = height
            
            positioned_children.add(child)
            
    def render(self, buffer: List[List[str]]):
        if not self.visible:
            return
        self.render_children(buffer)
