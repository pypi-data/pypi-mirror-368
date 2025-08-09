from typing import List, Callable, Optional
from ..core.component import Component
from ..core.event import Event, KeyEvent
from ..utils.colors import Color
from ..utils.keys import Key


class Button(Component):
    def __init__(self, text: str = 'Button', x: int = 0, y: int = 0,
                 width: int = None, height: int = 3,
                 color: str = Color.WHITE, bg_color: str = Color.BLUE,
                 focus_color: str = Color.YELLOW, focus_bg_color: str = Color.BRIGHT_BLUE,
                 border: bool = True, on_click: Callable = None):
        if width is None:
            width = len(text) + 4
        super().__init__(x, y, width, height)
        self.text = text
        self.color = color
        self.bg_color = bg_color
        self.focus_color = focus_color
        self.focus_bg_color = focus_bg_color
        self.border = border
        self.on_click = on_click
        self.focusable = True
        self.pressed = False
        
        self.on('key', self._handle_key)
        
    def _handle_key(self, event: KeyEvent):
        if event.key == Key.ENTER or event.key == Key.SPACE:
            self.click()
            event.stop_propagation()
            
    def click(self):
        self.pressed = True
        if self.on_click:
            self.on_click()
        self.emit(Event('click', target=self))
        
    def render(self, buffer: List[List[str]]):
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        current_color = self.focus_color if self.focused else self.color
        current_bg = self.focus_bg_color if self.focused else self.bg_color
        
        for y in range(self.height):
            for x in range(self.width):
                y_pos = abs_y + y
                x_pos = abs_x + x
                
                if y_pos >= len(buffer) or x_pos >= len(buffer[y_pos]):
                    continue
                    
                char = ' '
                
                if self.border:
                    if y == 0 or y == self.height - 1:
                        if x == 0 or x == self.width - 1:
                            char = '+'
                        else:
                            char = '-'
                    elif x == 0 or x == self.width - 1:
                        char = '|'
                        
                if y == self.height // 2 and not self.border:
                    text_start = (self.width - len(self.text)) // 2
                    if text_start <= x < text_start + len(self.text):
                        char = self.text[x - text_start]
                elif y == self.height // 2 and self.border and self.height >= 3:
                    text_start = (self.width - len(self.text)) // 2
                    if text_start <= x < text_start + len(self.text) and x > 0 and x < self.width - 1:
                        char = self.text[x - text_start]
                        
                styled_char = current_bg + current_color + char + Color.RESET
                if self.pressed and char != ' ':
                    styled_char = Color.REVERSE + styled_char
                    
                buffer[y_pos][x_pos] = styled_char
                
        self.pressed = False
        self.render_children(buffer)
