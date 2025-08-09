from typing import List, Callable, Optional
from ..core.component import Component
from ..core.event import Event, KeyEvent
from ..utils.colors import Color
from ..utils.keys import Key


class Checkbox(Component):
    def __init__(self, label: str = '', checked: bool = False,
                 x: int = 0, y: int = 0, width: int = None, height: int = 1,
                 color: str = Color.WHITE, bg_color: str = None,
                 focus_color: str = Color.YELLOW, checked_char: str = 'X',
                 unchecked_char: str = ' ', on_change: Callable = None):
        if width is None:
            width = len(label) + 4
        super().__init__(x, y, width, height)
        self.label = label
        self.checked = checked
        self.color = color
        self.bg_color = bg_color
        self.focus_color = focus_color
        self.checked_char = checked_char
        self.unchecked_char = unchecked_char
        self.on_change = on_change
        self.focusable = True
        
        self.on('key', self._handle_key)
        
    def _handle_key(self, event: KeyEvent):
        if event.key == Key.ENTER or event.key == Key.SPACE:
            self.toggle()
            event.stop_propagation()
            
    def toggle(self):
        self.checked = not self.checked
        if self.on_change:
            self.on_change(self.checked)
        self.emit(Event('change', self.checked, target=self))
        
    def set_checked(self, checked: bool):
        old_checked = self.checked
        self.checked = checked
        if old_checked != checked:
            if self.on_change:
                self.on_change(self.checked)
            self.emit(Event('change', self.checked, target=self))
            
    def render(self, buffer: List[List[str]]):
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        current_color = self.focus_color if self.focused else self.color
        
        checkbox_char = self.checked_char if self.checked else self.unchecked_char
        display_text = f'[{checkbox_char}] {self.label}'
        
        if len(display_text) > self.width:
            display_text = display_text[:self.width]
        else:
            display_text = display_text.ljust(self.width)
            
        for i, char in enumerate(display_text):
            x_pos = abs_x + i
            y_pos = abs_y
            
            if y_pos >= len(buffer) or x_pos >= len(buffer[y_pos]):
                continue
                
            styled_char = char
            if current_color != Color.WHITE:
                styled_char = current_color + styled_char + Color.RESET
            if self.bg_color:
                styled_char = self.bg_color + styled_char + Color.RESET
                
            if self.focused and i < 3:
                styled_char = Color.REVERSE + styled_char
                
            buffer[y_pos][x_pos] = styled_char
            
        self.render_children(buffer)
