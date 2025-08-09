from typing import List, Callable, Optional, Union
from ..core.component import Component
from ..core.event import Event, KeyEvent
from ..utils.colors import Color
from ..utils.keys import Key


class MenuItem:
    def __init__(self, text: str, value: str = None, callback: Callable = None, 
                 separator: bool = False, enabled: bool = True):
        self.text = text
        self.value = value or text
        self.callback = callback
        self.separator = separator
        self.enabled = enabled


class Menu(Component):
    def __init__(self, items: List[Union[MenuItem, str]] = None,
                 x: int = 0, y: int = 0, width: int = 20, height: int = 10,
                 color: str = Color.WHITE, bg_color: str = Color.BLACK,
                 selected_color: str = Color.BLACK, selected_bg_color: str = Color.WHITE,
                 border: bool = True, title: str = None,
                 on_select: Callable = None):
        super().__init__(x, y, width, height)
        self.color = color
        self.bg_color = bg_color
        self.selected_color = selected_color
        self.selected_bg_color = selected_bg_color
        self.border = border
        self.title = title
        self.on_select = on_select
        self.focusable = True
        
        self.items: List[MenuItem] = []
        self.selected_index = 0
        self.scroll_offset = 0
        
        if items:
            for item in items:
                if isinstance(item, str):
                    self.add_item(MenuItem(item))
                else:
                    self.add_item(item)
                    
        self.on('key', self._handle_key)
        
    def add_item(self, item: MenuItem):
        self.items.append(item)
        if self.selected_index >= len(self.items):
            self.selected_index = len(self.items) - 1
            
    def remove_item(self, index: int):
        if 0 <= index < len(self.items):
            self.items.pop(index)
            if self.selected_index >= len(self.items):
                self.selected_index = max(0, len(self.items) - 1)
                
    def clear_items(self):
        self.items.clear()
        self.selected_index = 0
        self.scroll_offset = 0
        
    def _handle_key(self, event: KeyEvent):
        if not self.items:
            return
            
        key = event.key
        
        if key == Key.UP:
            self._move_selection(-1)
            event.stop_propagation()
        elif key == Key.DOWN:
            self._move_selection(1)
            event.stop_propagation()
        elif key == Key.HOME:
            self.selected_index = 0
            self._update_scroll()
            event.stop_propagation()
        elif key == Key.END:
            self.selected_index = len(self.items) - 1
            self._update_scroll()
            event.stop_propagation()
        elif key == Key.ENTER or key == Key.SPACE:
            self._select_current()
            event.stop_propagation()
            
    def _move_selection(self, direction: int):
        old_index = self.selected_index
        
        while True:
            self.selected_index = (self.selected_index + direction) % len(self.items)
            if self.selected_index == old_index:
                break
            if not self.items[self.selected_index].separator and self.items[self.selected_index].enabled:
                break
                
        self._update_scroll()
        
    def _update_scroll(self):
        visible_height = self.height - (2 if self.border else 0) - (1 if self.title else 0)
        
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + visible_height:
            self.scroll_offset = self.selected_index - visible_height + 1
            
    def _select_current(self):
        if 0 <= self.selected_index < len(self.items):
            item = self.items[self.selected_index]
            if item.enabled and not item.separator:
                if item.callback:
                    item.callback()
                if self.on_select:
                    self.on_select(item.value)
                self.emit(Event('select', item.value, target=self))
                
    def get_selected_item(self) -> Optional[MenuItem]:
        if 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None
        
    def render(self, buffer: List[List[str]]):
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        current_y = 0
        
        if self.border:
            for x in range(self.width):
                if abs_y + current_y < len(buffer) and abs_x + x < len(buffer[abs_y + current_y]):
                    char = '-' if 0 < x < self.width - 1 else '+'
                    buffer[abs_y + current_y][abs_x + x] = self.bg_color + self.color + char + Color.RESET
            current_y += 1
            
        if self.title:
            title_text = self.title[:self.width - (2 if self.border else 0)]
            title_text = title_text.center(self.width - (2 if self.border else 0))
            
            start_x = 1 if self.border else 0
            for i, char in enumerate(title_text):
                x_pos = abs_x + start_x + i
                y_pos = abs_y + current_y
                
                if y_pos < len(buffer) and x_pos < len(buffer[y_pos]):
                    styled_char = self.bg_color + Color.BOLD + self.color + char + Color.RESET
                    buffer[y_pos][x_pos] = styled_char
                    
            if self.border:
                buffer[abs_y + current_y][abs_x] = self.bg_color + self.color + '|' + Color.RESET
                buffer[abs_y + current_y][abs_x + self.width - 1] = self.bg_color + self.color + '|' + Color.RESET
                
            current_y += 1
            
        visible_height = self.height - current_y - (1 if self.border else 0)
        
        for i in range(visible_height):
            item_index = self.scroll_offset + i
            y_pos = abs_y + current_y + i
            
            if y_pos >= len(buffer):
                break
                
            if self.border:
                if abs_x < len(buffer[y_pos]):
                    buffer[y_pos][abs_x] = self.bg_color + self.color + '|' + Color.RESET
                if abs_x + self.width - 1 < len(buffer[y_pos]):
                    buffer[y_pos][abs_x + self.width - 1] = self.bg_color + self.color + '|' + Color.RESET
                    
            if item_index < len(self.items):
                item = self.items[item_index]
                is_selected = item_index == self.selected_index and self.focused
                
                item_color = self.selected_color if is_selected else self.color
                item_bg = self.selected_bg_color if is_selected else self.bg_color
                
                if not item.enabled:
                    item_color = Color.BRIGHT_BLACK
                    
                display_width = self.width - (2 if self.border else 0)
                
                if item.separator:
                    separator_char = '-'
                    display_text = separator_char * display_width
                else:
                    display_text = item.text[:display_width].ljust(display_width)
                    
                start_x = 1 if self.border else 0
                for j, char in enumerate(display_text):
                    x_pos = abs_x + start_x + j
                    
                    if x_pos < len(buffer[y_pos]):
                        styled_char = item_bg + item_color + char + Color.RESET
                        buffer[y_pos][x_pos] = styled_char
            else:
                start_x = 1 if self.border else 0
                display_width = self.width - (2 if self.border else 0)
                for j in range(display_width):
                    x_pos = abs_x + start_x + j
                    if x_pos < len(buffer[y_pos]):
                        buffer[y_pos][x_pos] = self.bg_color + ' ' + Color.RESET
                        
        if self.border:
            bottom_y = abs_y + self.height - 1
            if bottom_y < len(buffer):
                for x in range(self.width):
                    if abs_x + x < len(buffer[bottom_y]):
                        char = '-' if 0 < x < self.width - 1 else '+'
                        buffer[bottom_y][abs_x + x] = self.bg_color + self.color + char + Color.RESET
                        
        self.render_children(buffer)
