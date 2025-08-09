from typing import List as ListType, Callable, Optional, Any
from ..core.component import Component
from ..core.event import Event, KeyEvent
from ..utils.colors import Color
from ..utils.keys import Key


class List(Component):
    def __init__(self, items: ListType[Any] = None,
                 x: int = 0, y: int = 0, width: int = 20, height: int = 10,
                 color: str = Color.WHITE, bg_color: str = Color.BLACK,
                 selected_color: str = Color.BLACK, selected_bg_color: str = Color.WHITE,
                 border: bool = True, title: str = None,
                 item_formatter: Callable[[Any], str] = None,
                 on_select: Callable = None, multi_select: bool = False):
        super().__init__(x, y, width, height)
        self.color = color
        self.bg_color = bg_color
        self.selected_color = selected_color
        self.selected_bg_color = selected_bg_color
        self.border = border
        self.title = title
        self.item_formatter = item_formatter or str
        self.on_select = on_select
        self.multi_select = multi_select
        self.focusable = True
        
        self.items: ListType[Any] = items or []
        self.selected_index = 0
        self.selected_indices = set()
        self.scroll_offset = 0
        
        self.on('key', self._handle_key)
        
    def add_item(self, item: Any):
        self.items.append(item)
        
    def remove_item(self, index: int):
        if 0 <= index < len(self.items):
            item = self.items.pop(index)
            if index in self.selected_indices:
                self.selected_indices.remove(index)
            self.selected_indices = {i - 1 if i > index else i for i in self.selected_indices}
            if self.selected_index >= len(self.items):
                self.selected_index = max(0, len(self.items) - 1)
            return item
        return None
        
    def clear_items(self):
        self.items.clear()
        self.selected_index = 0
        self.selected_indices.clear()
        self.scroll_offset = 0
        
    def get_selected_items(self) -> ListType[Any]:
        if self.multi_select:
            return [self.items[i] for i in self.selected_indices if 0 <= i < len(self.items)]
        else:
            if 0 <= self.selected_index < len(self.items):
                return [self.items[self.selected_index]]
            return []
            
    def get_selected_item(self) -> Optional[Any]:
        items = self.get_selected_items()
        return items[0] if items else None
        
    def _handle_key(self, event: KeyEvent):
        if not self.items:
            return
            
        key = event.key
        
        if key == Key.UP:
            self.selected_index = max(0, self.selected_index - 1)
            self._update_scroll()
            event.stop_propagation()
        elif key == Key.DOWN:
            self.selected_index = min(len(self.items) - 1, self.selected_index + 1)
            self._update_scroll()
            event.stop_propagation()
        elif key == Key.HOME:
            self.selected_index = 0
            self._update_scroll()
            event.stop_propagation()
        elif key == Key.END:
            self.selected_index = len(self.items) - 1
            self._update_scroll()
            event.stop_propagation()
        elif key == Key.ENTER:
            self._select_current()
            event.stop_propagation()
        elif key == Key.SPACE and self.multi_select:
            self._toggle_selection()
            event.stop_propagation()
            
    def _update_scroll(self):
        visible_height = self.height - (2 if self.border else 0) - (1 if self.title else 0)
        
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + visible_height:
            self.scroll_offset = self.selected_index - visible_height + 1
            
    def _select_current(self):
        if 0 <= self.selected_index < len(self.items):
            item = self.items[self.selected_index]
            if self.on_select:
                self.on_select(item)
            self.emit(Event('select', item, target=self))
            
    def _toggle_selection(self):
        if self.selected_index in self.selected_indices:
            self.selected_indices.remove(self.selected_index)
        else:
            self.selected_indices.add(self.selected_index)
            
    def render(self, buffer: ListType[ListType[str]]):
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
                is_multi_selected = item_index in self.selected_indices
                
                item_color = self.selected_color if is_selected else self.color
                item_bg = self.selected_bg_color if is_selected else self.bg_color
                
                display_width = self.width - (2 if self.border else 0)
                prefix = ""
                
                if self.multi_select:
                    prefix = "[X] " if is_multi_selected else "[ ] "
                    display_width -= len(prefix)
                    
                item_text = self.item_formatter(item)
                display_text = (prefix + item_text)[:display_width + len(prefix)]
                display_text = display_text.ljust(display_width + len(prefix))
                
                start_x = 1 if self.border else 0
                for j, char in enumerate(display_text):
                    x_pos = abs_x + start_x + j
                    
                    if x_pos < len(buffer[y_pos]):
                        styled_char = item_bg + item_color + char + Color.RESET
                        if is_multi_selected and not is_selected:
                            styled_char = Color.DIM + styled_char
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
