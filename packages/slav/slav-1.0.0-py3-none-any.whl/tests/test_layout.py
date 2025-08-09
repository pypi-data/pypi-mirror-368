import pytest
from slav.layout.box import Box
from slav.layout.grid import Grid
from slav.components.text import Text
from slav.components.button import Button


class TestBox:
    def test_box_creation(self):
        box = Box(direction='horizontal', spacing=2, padding=1)
        assert box.direction == 'horizontal'
        assert box.spacing == 2
        assert box.padding == 1
        
    def test_box_add_child(self):
        box = Box(width=100, height=50)
        text = Text("Test", width=10, height=1)
        
        box.add_child(text)
        assert text in box.children
        assert text.parent == box
        
    def test_box_vertical_layout(self):
        box = Box(direction='vertical', width=20, height=20, padding=2, spacing=1)
        
        text1 = Text("Text 1", width=10, height=2)
        text2 = Text("Text 2", width=10, height=2)
        
        box.add_child(text1)
        box.add_child(text2)
        
        assert text1.x == 2
        assert text1.y == 2
        assert text2.x == 2
        assert text2.y == 5
        
    def test_box_horizontal_layout(self):
        box = Box(direction='horizontal', width=20, height=20, padding=2, spacing=1)
        
        text1 = Text("Text 1", width=5, height=2)
        text2 = Text("Text 2", width=5, height=2)
        
        box.add_child(text1)
        box.add_child(text2)
        
        assert text1.x == 2
        assert text1.y == 2
        assert text2.x == 8
        assert text2.y == 2


class TestGrid:
    def test_grid_creation(self):
        grid = Grid(rows=3, cols=3, width=30, height=30)
        assert grid.rows == 3
        assert grid.cols == 3
        assert len(grid.grid) == 3
        assert len(grid.grid[0]) == 3
        
    def test_grid_add_child(self):
        grid = Grid(rows=2, cols=2, width=20, height=20, padding=1, gap=1)
        text = Text("Test", width=5, height=2)
        
        grid.add_child_at(text, 0, 0)
        assert text in grid.children
        assert text.parent == grid
        assert grid.grid[0][0] == text
        
    def test_grid_layout(self):
        grid = Grid(rows=2, cols=2, width=20, height=20, padding=2, gap=2)
        
        text1 = Text("Text 1")
        text2 = Text("Text 2") 
        text3 = Text("Text 3")
        text4 = Text("Text 4")
        
        grid.add_child_at(text1, 0, 0)
        grid.add_child_at(text2, 0, 1)
        grid.add_child_at(text3, 1, 0)
        grid.add_child_at(text4, 1, 1)
        
        assert text1.x == 2
        assert text1.y == 2
        assert text2.x == 12
        assert text2.y == 2
        assert text3.x == 2
        assert text3.y == 12
        assert text4.x == 12
        assert text4.y == 12
        
    def test_grid_spanning(self):
        grid = Grid(rows=3, cols=3, width=30, height=30, padding=0, gap=0)
        
        text = Text("Spanning text")
        grid.add_child_at(text, 0, 0, row_span=2, col_span=2)
        
        assert grid.grid[0][0] == text
        assert grid.grid[0][1] == text
        assert grid.grid[1][0] == text
        assert grid.grid[1][1] == text
        
        assert text.width == 20
        assert text.height == 20
