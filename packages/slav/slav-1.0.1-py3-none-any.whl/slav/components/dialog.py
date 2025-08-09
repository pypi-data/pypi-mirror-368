from typing import List, Callable, Optional, Dict, Any
from ..core.component import Component
from ..core.event import Event, KeyEvent
from ..utils.colors import Color
from ..utils.keys import Key
from .button import Button
from .text import Text


class Dialog(Component):
    def __init__(self, title: str = "Dialog", message: str = "",
                 x: int = 0, y: int = 0, width: int = 40, height: int = 10,
                 color: str = Color.WHITE, bg_color: str = Color.BLACK,
                 border_color: str = Color.BRIGHT_WHITE,
                 buttons: List[str] = None, modal: bool = True,
                 on_result: Callable[[str], None] = None):
        super().__init__(x, y, width, height)
        self.title = title
        self.message = message
        self.color = color
        self.bg_color = bg_color
        self.border_color = border_color
        self.modal = modal
        self.on_result = on_result
        self.focusable = True
        self.z_index = 1000
        
        self.buttons = buttons or ["OK"]
        self.selected_button = 0
        self.result = None
        
        self._create_ui()
        self.on('key', self._handle_key)
        
    def _create_ui(self):
        self.children.clear()
        
        title_component = Text(
            text=self.title,
            x=2, y=1,
            width=self.width - 4,
            color=Color.BOLD + self.color,
            align='center'
        )
        self.add_child(title_component)
        
        message_lines = self.message.split('\n')
        for i, line in enumerate(message_lines[:self.height - 6]):
            message_component = Text(
                text=line,
                x=2, y=3 + i,
                width=self.width - 4,
                color=self.color,
                wrap=True
            )
            self.add_child(message_component)
            
        button_width = max(8, (self.width - 4) // len(self.buttons) - 2)
        button_y = self.height - 3
        total_button_width = len(self.buttons) * button_width + (len(self.buttons) - 1) * 2
        start_x = (self.width - total_button_width) // 2
        
        for i, button_text in enumerate(self.buttons):
            button_x = start_x + i * (button_width + 2)
            button = Button(
                text=button_text,
                x=button_x, y=button_y,
                width=button_width, height=1,
                border=False,
                on_click=lambda btn_text=button_text: self._button_clicked(btn_text)
            )
            button.focusable = True
            self.add_child(button)
            
    def _handle_key(self, event: KeyEvent):
        key = event.key
        
        if key == Key.LEFT:
            self.selected_button = (self.selected_button - 1) % len(self.buttons)
            self._update_button_focus()
            event.stop_propagation()
        elif key == Key.RIGHT:
            self.selected_button = (self.selected_button + 1) % len(self.buttons)
            self._update_button_focus()
            event.stop_propagation()
        elif key == Key.ENTER:
            self._button_clicked(self.buttons[self.selected_button])
            event.stop_propagation()
        elif key == Key.ESCAPE:
            self._button_clicked("Cancel" if "Cancel" in self.buttons else self.buttons[-1])
            event.stop_propagation()
            
    def _update_button_focus(self):
        button_index = 0
        for child in self.children:
            if isinstance(child, Button):
                child.focused = (button_index == self.selected_button)
                button_index += 1
                
    def _button_clicked(self, button_text: str):
        self.result = button_text
        if self.on_result:
            self.on_result(button_text)
        self.emit(Event('result', button_text, target=self))
        
    def show(self):
        super().show()
        self._update_button_focus()
        
    def center_on_screen(self, screen_width: int, screen_height: int):
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        
    def render(self, buffer: List[List[str]]):
        if not self.visible:
            return
            
        abs_x, abs_y = self.get_absolute_position()
        
        if self.modal:
            for y in range(len(buffer)):
                for x in range(len(buffer[y])):
                    if buffer[y][x] != ' ':
                        buffer[y][x] = Color.DIM + buffer[y][x] + Color.RESET
                        
        for y in range(self.height):
            for x in range(self.width):
                y_pos = abs_y + y
                x_pos = abs_x + x
                
                if y_pos >= len(buffer) or x_pos >= len(buffer[y_pos]):
                    continue
                    
                char = ' '
                char_color = self.color
                char_bg = self.bg_color
                
                if y == 0 or y == self.height - 1:
                    if x == 0 or x == self.width - 1:
                        char = '+'
                        char_color = self.border_color
                    else:
                        char = '-'
                        char_color = self.border_color
                elif x == 0 or x == self.width - 1:
                    char = '|'
                    char_color = self.border_color
                    
                buffer[y_pos][x_pos] = char_bg + char_color + char + Color.RESET
                
        self.render_children(buffer)


def show_message_dialog(title: str, message: str, buttons: List[str] = None) -> Dialog:
    buttons = buttons or ["OK"]
    dialog = Dialog(title=title, message=message, buttons=buttons)
    dialog.center_on_screen(80, 24)
    return dialog


def show_confirm_dialog(title: str, message: str) -> Dialog:
    return show_message_dialog(title, message, ["Yes", "No"])


def show_error_dialog(message: str) -> Dialog:
    return show_message_dialog("Error", message, ["OK"])
