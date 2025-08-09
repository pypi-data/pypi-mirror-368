from typing import List, Optional
from ..core.component import Component
from ..utils.colors import Color


class ProgressBar(Component):
    def __init__(self, value: float = 0.0, min_value: float = 0.0, max_value: float = 100.0,
                 x: int = 0, y: int = 0, width: int = 20, height: int = 1,
                 color: str = Color.WHITE, bg_color: str = Color.BLACK,
                 fill_color: str = Color.GREEN, fill_bg_color: str = Color.BRIGHT_GREEN,
                 border: bool = True, show_percentage: bool = True,
                 fill_char: str = '█', empty_char: str = '░'):
        super().__init__(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.color = color
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.fill_bg_color = fill_bg_color
        self.border = border
        self.show_percentage = show_percentage
        self.fill_char = fill_char
        self.empty_char = empty_char
        self._value = value
        
    @property
    def value(self) -> float:
        return self._value
        
    @value.setter
    def value(self, val: float):
        self._value = max(self.min_value, min(self.max_value, val))
        
    def get_percentage(self) -> float:
        if self.max_value == self.min_value:
            return 0.0
        return ((self.value - self.min_value) / (self.max_value - self.min_value)) * 100
        
    def set_percentage(self, percentage: float):
        self.value = self.min_value + (percentage / 100) * (self.max_value - self.min_value)
        
    def render(self, buffer: List[List[str]]):
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        for y in range(self.height):
            y_pos = abs_y + y
            if y_pos >= len(buffer):
                continue
                
            if self.border and (y == 0 or y == self.height - 1):
                for x in range(self.width):
                    x_pos = abs_x + x
                    if x_pos >= len(buffer[y_pos]):
                        continue
                        
                    if x == 0 or x == self.width - 1:
                        char = '+'
                    else:
                        char = '-'
                        
                    buffer[y_pos][x_pos] = self.bg_color + self.color + char + Color.RESET
                    
            elif self.border and (y > 0 and y < self.height - 1):
                for x in range(self.width):
                    x_pos = abs_x + x
                    if x_pos >= len(buffer[y_pos]):
                        continue
                        
                    if x == 0 or x == self.width - 1:
                        char = '|'
                        buffer[y_pos][x_pos] = self.bg_color + self.color + char + Color.RESET
                    else:
                        self._render_progress_content(buffer, y_pos, x_pos, x - 1, self.width - 2)
                        
            else:
                for x in range(self.width):
                    x_pos = abs_x + x
                    if x_pos >= len(buffer[y_pos]):
                        continue
                        
                    self._render_progress_content(buffer, y_pos, x_pos, x, self.width)
                    
        self.render_children(buffer)
        
    def _render_progress_content(self, buffer: List[List[str]], y_pos: int, x_pos: int, 
                               relative_x: int, content_width: int):
        percentage = self.get_percentage()
        fill_width = int((percentage / 100) * content_width)
        
        char = ' '
        char_color = self.color
        char_bg = self.bg_color
        
        if relative_x < fill_width:
            char = self.fill_char
            char_color = self.fill_color
            char_bg = self.fill_bg_color
        else:
            char = self.empty_char
            
        if self.show_percentage and self.height >= 3:
            percentage_text = f"{percentage:.1f}%"
            text_start = (content_width - len(percentage_text)) // 2
            text_y = self.height // 2
            
            if (y_pos - self.get_absolute_position()[1]) == text_y:
                if text_start <= relative_x < text_start + len(percentage_text):
                    char = percentage_text[relative_x - text_start]
                    char_color = self.color if relative_x < fill_width else self.color
                    char_bg = self.fill_bg_color if relative_x < fill_width else self.bg_color
                    
        buffer[y_pos][x_pos] = char_bg + char_color + char + Color.RESET
