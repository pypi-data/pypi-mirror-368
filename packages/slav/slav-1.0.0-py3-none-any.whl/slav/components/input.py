from typing import List, Callable, Optional
from ..core.component import Component
from ..core.event import Event, KeyEvent
from ..utils.colors import Color
from ..utils.keys import Key


class Input(Component):
    def __init__(self, placeholder: str = '', x: int = 0, y: int = 0,
                 width: int = 20, height: int = 1,
                 color: str = Color.WHITE, bg_color: str = Color.BLACK,
                 focus_color: str = Color.BRIGHT_WHITE, focus_bg_color: str = Color.BRIGHT_BLACK,
                 border: bool = True, password: bool = False,
                 max_length: int = None, on_change: Callable = None,
                 on_submit: Callable = None):
        super().__init__(x, y, width, height)
        self.placeholder = placeholder
        self.color = color
        self.bg_color = bg_color
        self.focus_color = focus_color
        self.focus_bg_color = focus_bg_color
        self.border = border
        self.password = password
        self.max_length = max_length
        self.on_change = on_change
        self.on_submit = on_submit
        self.focusable = True
        
        self.value = ''
        self.cursor_pos = 0
        self.scroll_offset = 0
        
        self.on('key', self._handle_key)
        
    def _handle_key(self, event: KeyEvent):
        key = event.key
        
        if key == Key.ENTER:
            if self.on_submit:
                self.on_submit(self.value)
            self.emit(Event('submit', self.value, target=self))
            event.stop_propagation()
            
        elif key == Key.BACKSPACE:
            if self.cursor_pos > 0:
                self.value = self.value[:self.cursor_pos-1] + self.value[self.cursor_pos:]
                self.cursor_pos -= 1
                self._trigger_change()
            event.stop_propagation()
            
        elif key == Key.DELETE:
            if self.cursor_pos < len(self.value):
                self.value = self.value[:self.cursor_pos] + self.value[self.cursor_pos+1:]
                self._trigger_change()
            event.stop_propagation()
            
        elif key == Key.LEFT:
            if self.cursor_pos > 0:
                self.cursor_pos -= 1
            event.stop_propagation()
            
        elif key == Key.RIGHT:
            if self.cursor_pos < len(self.value):
                self.cursor_pos += 1
            event.stop_propagation()
            
        elif key == Key.HOME:
            self.cursor_pos = 0
            event.stop_propagation()
            
        elif key == Key.END:
            self.cursor_pos = len(self.value)
            event.stop_propagation()
            
        elif Key.is_printable(key):
            if self.max_length is None or len(self.value) < self.max_length:
                self.value = self.value[:self.cursor_pos] + key + self.value[self.cursor_pos:]
                self.cursor_pos += 1
                self._trigger_change()
            event.stop_propagation()
            
        self._update_scroll()
        
    def _trigger_change(self):
        if self.on_change:
            self.on_change(self.value)
        self.emit(Event('change', self.value, target=self))
        
    def _update_scroll(self):
        visible_width = self.width - (2 if self.border else 0)
        if self.cursor_pos < self.scroll_offset:
            self.scroll_offset = self.cursor_pos
        elif self.cursor_pos >= self.scroll_offset + visible_width:
            self.scroll_offset = self.cursor_pos - visible_width + 1
            
    def set_value(self, value: str):
        self.value = value
        self.cursor_pos = len(value)
        self._update_scroll()
        
    def clear(self):
        self.value = ''
        self.cursor_pos = 0
        self.scroll_offset = 0
        
    def render(self, buffer: List[List[str]]):
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        current_color = self.focus_color if self.focused else self.color
        current_bg = self.focus_bg_color if self.focused else self.bg_color
        
        display_text = self.value
        if self.password:
            display_text = '*' * len(self.value)
            
        if not display_text and not self.focused:
            display_text = self.placeholder
            current_color = Color.BRIGHT_BLACK
            
        visible_width = self.width - (2 if self.border else 0)
        visible_text = display_text[self.scroll_offset:self.scroll_offset + visible_width]
        visible_text = visible_text.ljust(visible_width)
        
        for y in range(self.height):
            for x in range(self.width):
                y_pos = abs_y + y
                x_pos = abs_x + x
                
                if y_pos >= len(buffer) or x_pos >= len(buffer[y_pos]):
                    continue
                    
                char = ' '
                char_color = current_color
                char_bg = current_bg
                
                if self.border:
                    if y == 0 or y == self.height - 1:
                        if x == 0 or x == self.width - 1:
                            char = '+'
                        else:
                            char = '-'
                    elif x == 0 or x == self.width - 1:
                        char = '|'
                    elif x > 0 and x < self.width - 1:
                        text_x = x - 1
                        if text_x < len(visible_text):
                            char = visible_text[text_x]
                else:
                    if x < len(visible_text):
                        char = visible_text[x]
                        
                styled_char = char_bg + char_color + char + Color.RESET
                
                if self.focused and not self.border:
                    cursor_x = self.cursor_pos - self.scroll_offset
                    if x == cursor_x:
                        styled_char = Color.REVERSE + styled_char
                elif self.focused and self.border:
                    cursor_x = self.cursor_pos - self.scroll_offset + 1
                    if x == cursor_x and y == 0:
                        styled_char = Color.REVERSE + styled_char
                        
                buffer[y_pos][x_pos] = styled_char
                
        self.render_children(buffer)
