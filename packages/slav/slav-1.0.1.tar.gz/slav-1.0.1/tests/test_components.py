import pytest
from slav.components.text import Text
from slav.components.button import Button
from slav.components.input import Input
from slav.components.checkbox import Checkbox
from slav.core.event import KeyEvent
from slav.utils.keys import Key
from slav.utils.colors import Color


class TestText:
    def test_text_creation(self):
        text = Text("Hello World", x=5, y=10, width=20)
        assert text.text == "Hello World"
        assert text.x == 5
        assert text.y == 10
        assert text.width == 20
        
    def test_text_rendering(self):
        text = Text("Test", x=0, y=0, width=10)
        buffer = [[' ' for _ in range(20)] for _ in range(5)]
        text.render(buffer)
        
        assert buffer[0][0] != ' '
        
    def test_text_wrapping(self):
        text = Text("This is a very long text that should wrap", 
                   x=0, y=0, width=10, wrap=True)
        text._update_lines()
        assert len(text._lines) > 1


class TestButton:
    def test_button_creation(self):
        button = Button("Click Me", x=0, y=0, width=15, height=3)
        assert button.text == "Click Me"
        assert button.focusable == True
        
    def test_button_click(self):
        clicked = False
        
        def on_click():
            nonlocal clicked
            clicked = True
            
        button = Button("Test", on_click=on_click)
        button.click()
        assert clicked == True
        
    def test_button_key_handling(self):
        button = Button("Test")
        button.focused = True
        
        event = KeyEvent(Key.ENTER)
        button._handle_key(event)
        assert event.bubbles == False


class TestInput:
    def test_input_creation(self):
        input_field = Input(placeholder="Enter text", width=20)
        assert input_field.placeholder == "Enter text"
        assert input_field.value == ""
        assert input_field.focusable == True
        
    def test_input_typing(self):
        input_field = Input()
        input_field.focused = True
        
        event = KeyEvent('a')
        input_field._handle_key(event)
        assert input_field.value == "a"
        assert input_field.cursor_pos == 1
        
    def test_input_backspace(self):
        input_field = Input()
        input_field.value = "hello"
        input_field.cursor_pos = 5
        
        event = KeyEvent(Key.BACKSPACE)
        input_field._handle_key(event)
        assert input_field.value == "hell"
        assert input_field.cursor_pos == 4
        
    def test_input_navigation(self):
        input_field = Input()
        input_field.value = "hello"
        input_field.cursor_pos = 5
        
        event = KeyEvent(Key.LEFT)
        input_field._handle_key(event)
        assert input_field.cursor_pos == 4
        
        event = KeyEvent(Key.RIGHT)
        input_field._handle_key(event)
        assert input_field.cursor_pos == 5
        
    def test_input_max_length(self):
        input_field = Input(max_length=5)
        input_field.value = "hello"
        input_field.cursor_pos = 5
        
        event = KeyEvent('x')
        input_field._handle_key(event)
        assert input_field.value == "hello"


class TestCheckbox:
    def test_checkbox_creation(self):
        checkbox = Checkbox("Test option")
        assert checkbox.label == "Test option"
        assert checkbox.checked == False
        assert checkbox.focusable == True
        
    def test_checkbox_toggle(self):
        checkbox = Checkbox("Test")
        assert checkbox.checked == False
        
        checkbox.toggle()
        assert checkbox.checked == True
        
        checkbox.toggle()
        assert checkbox.checked == False
        
    def test_checkbox_key_handling(self):
        checkbox = Checkbox("Test")
        checkbox.focused = True
        
        event = KeyEvent(Key.SPACE)
        checkbox._handle_key(event)
        assert checkbox.checked == True
        
    def test_checkbox_set_checked(self):
        checkbox = Checkbox("Test")
        
        checkbox.set_checked(True)
        assert checkbox.checked == True
        
        checkbox.set_checked(False)
        assert checkbox.checked == False
