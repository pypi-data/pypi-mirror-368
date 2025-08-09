# Slav - Terminal UI Toolkit

A modern, lightweight terminal-based UI toolkit for building interactive interfaces directly in the terminal. Slav provides a clean, intuitive API for creating professional terminal applications without external window dependencies.

## Features

- **Rich Component Library**: Buttons, inputs, checkboxes, menus, lists, progress bars, and dialogs
- **Flexible Layout System**: Box and grid layouts with automatic positioning and sizing
- **Event-Driven Architecture**: Comprehensive keyboard navigation and event handling
- **Cross-Platform**: Works on Windows, macOS, and Linux terminal emulators
- **Modern Design**: Clean, professional appearance with customizable colors and styles
- **Lightweight**: No external dependencies, pure Python implementation

## Installation

```bash
pip install slav
```

## Quick Start

```python
from slav import Screen, Box, Text, Button, Color

def main():
    screen = Screen()
    
    # Create a vertical layout container
    root = Box(direction='vertical', padding=5, spacing=2, width=80, height=24)
    
    # Add a title
    title = Text(
        text="Hello, Slav!",
        color=Color.BOLD + Color.CYAN,
        align='center',
        width=70
    )
    root.add_child(title)
    
    # Add a button
    button = Button(
        text="Click Me!",
        width=15,
        height=3,
        on_click=lambda: screen.stop()
    )
    root.add_child(button)
    
    # Run the application
    screen.set_root(root)
    screen.run()

if __name__ == "__main__":
    main()
```

## Components

### Text

Display formatted text with alignment, colors, and word wrapping.

```python
from slav import Text, Color

text = Text(
    text="Hello World",
    x=10, y=5,
    width=20,
    color=Color.GREEN,
    align='center',
    wrap=True
)
```

### Button

Interactive buttons with click events and keyboard navigation.

```python
from slav import Button

button = Button(
    text="Submit",
    width=12,
    height=3,
    on_click=lambda: print("Button clicked!"),
    color=Color.WHITE,
    bg_color=Color.BLUE
)
```

### Input

Text input fields with placeholder text, validation, and event handling.

```python
from slav import Input

input_field = Input(
    placeholder="Enter your name...",
    width=25,
    border=True,
    max_length=50,
    on_change=lambda value: print(f"Input: {value}"),
    on_submit=lambda value: process_input(value)
)
```

### Checkbox

Toggle controls with labels and change events.

```python
from slav import Checkbox

checkbox = Checkbox(
    label="Enable notifications",
    checked=True,
    on_change=lambda checked: print(f"Checked: {checked}")
)
```

### Menu

Vertical menu with items, keyboard navigation, and selection events.

```python
from slav import Menu, MenuItem

menu_items = [
    MenuItem("New File", "new"),
    MenuItem("Open File", "open"),
    MenuItem("Save File", "save"),
    MenuItem("", separator=True),
    MenuItem("Exit", "exit")
]

menu = Menu(
    items=menu_items,
    title="File Menu",
    width=20,
    height=10,
    on_select=lambda value: handle_menu_selection(value)
)
```

### List

Scrollable lists with single or multiple selection support.

```python
from slav import List

items = ["Apple", "Banana", "Cherry", "Date"]

item_list = List(
    items=items,
    title="Fruits",
    width=20,
    height=8,
    multi_select=True,
    on_select=lambda item: print(f"Selected: {item}")
)
```

### ProgressBar

Visual progress indicators with customizable appearance.

```python
from slav import ProgressBar

progress = ProgressBar(
    value=65,
    min_value=0,
    max_value=100,
    width=30,
    height=3,
    show_percentage=True,
    fill_color=Color.GREEN
)
```

### Dialog

Modal dialog boxes for user interaction and information display.

```python
from slav import Dialog

dialog = Dialog(
    title="Confirmation",
    message="Are you sure you want to delete this file?",
    width=40,
    height=10,
    buttons=["Yes", "No"],
    on_result=lambda result: handle_dialog_result(result)
)
```

## Layout Management

### Box Layout

Flexible container for arranging components horizontally or vertically.

```python
from slav import Box

# Vertical layout
vbox = Box(
    direction='vertical',
    spacing=2,
    padding=5,
    align='center',
    justify='space-between'
)

# Horizontal layout  
hbox = Box(
    direction='horizontal',
    spacing=3,
    padding=2,
    align='stretch'
)
```

### Grid Layout

Structured grid system for precise component positioning.

```python
from slav import Grid

grid = Grid(
    rows=3,
    cols=3,
    width=60,
    height=40,
    gap=2,
    padding=3
)

# Add components to specific grid positions
grid.add_child_at(title, row=0, col=0, row_span=1, col_span=3)
grid.add_child_at(button1, row=1, col=0)
grid.add_child_at(button2, row=1, col=1)
```

## Event Handling

Slav provides a comprehensive event system for handling user interactions.

```python
from slav import Screen, KeyEvent

def handle_key_event(event):
    if event.key == 'q':
        screen.stop()
    elif event.key == Key.F1:
        show_help()

# Component-level event handling
button.on('click', lambda event: handle_button_click())
input_field.on('change', lambda event: validate_input(event.data))

# Global event handling
screen.on('key', handle_key_event)
```

## Keyboard Navigation

- **Tab**: Move focus to next component
- **Shift+Tab**: Move focus to previous component  
- **Enter**: Activate focused component
- **Arrow Keys**: Navigate within components (lists, menus)
- **Escape**: Close dialogs or exit application
- **Space**: Toggle checkboxes, activate buttons

## Colors and Styling

```python
from slav import Color

# Basic colors
Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW
Color.CYAN, Color.MAGENTA, Color.WHITE, Color.BLACK

# Bright variants
Color.BRIGHT_RED, Color.BRIGHT_GREEN, Color.BRIGHT_BLUE

# Background colors
Color.BG_RED, Color.BG_GREEN, Color.BG_BLUE

# Text styling
Color.BOLD, Color.ITALIC, Color.UNDERLINE

# RGB colors
custom_color = Color.rgb(255, 128, 64)
custom_bg = Color.bg_rgb(32, 32, 32)
```

## Examples

Run the included demo to see all components in action:

```bash
python -m slav.examples.demo
```

Or create a simple application:

```bash
python -m slav.examples.simple
```

## Platform Support

Slav works across different platforms with specific optimizations:

- **Linux/macOS**: Full feature support with optimal performance
- **Windows**: Compatible with Command Prompt, PowerShell, and Windows Terminal
- **Terminal Emulators**: Tested with common emulators including iTerm2, GNOME Terminal, and Konsole

## API Reference

### Core Classes

- `Screen`: Main application screen and event loop
- `Component`: Base class for all UI components
- `Box`: Flexible layout container
- `Grid`: Structured grid layout container

### Event System

- `Event`: Base event class
- `KeyEvent`: Keyboard input events
- `FocusEvent`: Component focus events

### Utility Classes

- `Color`: Color and styling constants
- `Key`: Keyboard key constants
- `Terminal`: Low-level terminal control

## Development

To set up for development:

```bash
git clone https://github.com/slavdev/slav.git
cd slav
pip install -e .
pip install pytest pytest-cov
pytest tests/
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please read the contributing guidelines and submit pull requests for any improvements.

## Changelog

### 1.0.0
- Initial release
- Core component library
- Layout management system
- Event handling and keyboard navigation
- Cross-platform terminal support
