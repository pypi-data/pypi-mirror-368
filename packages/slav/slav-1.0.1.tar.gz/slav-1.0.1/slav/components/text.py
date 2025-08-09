from typing import List
from ..core.component import Component
from ..utils.colors import Color


class Text(Component):
    def __init__(self, text: str = '', x: int = 0, y: int = 0, 
                 width: int = None, height: int = 1, 
                 color: str = Color.WHITE, bg_color: str = None,
                 align: str = 'left', wrap: bool = False):
        if width is None:
            width = len(text)
        super().__init__(x, y, width, height)
        self.text = text
        self.color = color
        self.bg_color = bg_color
        self.align = align
        self.wrap = wrap
        self._lines = []
        self._update_lines()
        
    def set_text(self, text: str):
        self.text = text
        self._update_lines()
        
    def _update_lines(self):
        if self.wrap and self.width > 0:
            words = self.text.split()
            lines = []
            current_line = ''
            
            for word in words:
                if len(current_line + word) <= self.width:
                    if current_line:
                        current_line += ' '
                    current_line += word
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
                    
            if current_line:
                lines.append(current_line)
                
            self._lines = lines
        else:
            self._lines = [self.text]
            
        if self.wrap:
            self.height = max(1, len(self._lines))
            
    def render(self, buffer: List[List[str]]):
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        for i, line in enumerate(self._lines):
            if i >= self.height:
                break
                
            y_pos = abs_y + i
            if y_pos >= len(buffer):
                break
                
            display_text = line
            if len(display_text) > self.width:
                display_text = display_text[:self.width]
                
            if self.align == 'center':
                padding = (self.width - len(display_text)) // 2
                display_text = ' ' * padding + display_text
            elif self.align == 'right':
                padding = self.width - len(display_text)
                display_text = ' ' * padding + display_text
                
            display_text = display_text.ljust(self.width)
            
            for j, char in enumerate(display_text):
                x_pos = abs_x + j
                if x_pos >= len(buffer[y_pos]):
                    break
                    
                styled_char = char
                if self.color != Color.WHITE:
                    styled_char = self.color + styled_char + Color.RESET
                if self.bg_color:
                    styled_char = self.bg_color + styled_char + Color.RESET
                    
                buffer[y_pos][x_pos] = styled_char
                
        self.render_children(buffer)
