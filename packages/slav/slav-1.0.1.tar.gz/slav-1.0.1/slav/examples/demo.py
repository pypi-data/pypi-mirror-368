#!/usr/bin/env python3

import time
from ..core.screen import Screen
from ..components.text import Text
from ..components.button import Button
from ..components.input import Input
from ..components.checkbox import Checkbox
from ..components.menu import Menu, MenuItem
from ..components.list import List
from ..components.progress import ProgressBar
from ..components.dialog import Dialog, show_message_dialog
from ..layout.box import Box
from ..layout.grid import Grid
from ..utils.colors import Color


def create_basic_demo():
    screen = Screen()
    
    root = Box(direction='vertical', padding=2, spacing=1, width=80, height=24)
    
    title = Text(
        text="Slav Terminal UI Demo",
        color=Color.BOLD + Color.CYAN,
        align='center',
        width=76,
        height=1
    )
    root.add_child(title)
    
    subtitle = Text(
        text="A modern terminal-based UI toolkit",
        color=Color.BRIGHT_WHITE,
        align='center',
        width=76,
        height=1
    )
    root.add_child(subtitle)
    
    content_box = Box(direction='horizontal', spacing=2, width=76, height=18)
    
    left_panel = Box(direction='vertical', spacing=1, width=25, height=18)
    
    input_field = Input(
        placeholder="Enter your name...",
        width=23,
        height=1,
        border=True
    )
    left_panel.add_child(input_field)
    
    checkbox1 = Checkbox(
        label="Enable notifications",
        width=23,
        height=1
    )
    left_panel.add_child(checkbox1)
    
    checkbox2 = Checkbox(
        label="Dark mode",
        checked=True,
        width=23,
        height=1
    )
    left_panel.add_child(checkbox2)
    
    progress = ProgressBar(
        value=65,
        width=23,
        height=3,
        border=True,
        show_percentage=True
    )
    left_panel.add_child(progress)
    
    button = Button(
        text="Click Me!",
        width=15,
        height=3,
        on_click=lambda: show_dialog(screen)
    )
    left_panel.add_child(button)
    
    content_box.add_child(left_panel)
    
    middle_panel = Box(direction='vertical', spacing=1, width=25, height=18)
    
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
        width=23,
        height=10,
        border=True
    )
    middle_panel.add_child(menu)
    
    content_box.add_child(middle_panel)
    
    right_panel = Box(direction='vertical', spacing=1, width=24, height=18)
    
    list_items = ["Apple", "Banana", "Cherry", "Date", "Elderberry", "Fig", "Grape"]
    
    item_list = List(
        items=list_items,
        title="Fruits",
        width=22,
        height=12,
        border=True,
        multi_select=True
    )
    right_panel.add_child(item_list)
    
    status_text = Text(
        text="Use Tab to navigate, Enter to select, Esc to exit",
        color=Color.BRIGHT_BLACK,
        width=22,
        height=2,
        wrap=True
    )
    right_panel.add_child(status_text)
    
    content_box.add_child(right_panel)
    root.add_child(content_box)
    
    screen.set_root(root)
    return screen


def show_dialog(screen):
    dialog = Dialog(
        title="Hello Dialog",
        message="This is a modal dialog example.\nYou can use dialogs for confirmations,\ninput, or displaying information.",
        width=50,
        height=12,
        buttons=["OK", "Cancel"],
        on_result=lambda result: handle_dialog_result(result)
    )
    dialog.center_on_screen(80, 24)
    screen.root_component.add_child(dialog)


def handle_dialog_result(result):
    print(f"Dialog result: {result}")


def create_grid_demo():
    screen = Screen()
    
    root = Grid(rows=3, cols=3, width=80, height=24, gap=1, padding=2)
    
    title = Text(
        text="Grid Layout Demo",
        color=Color.BOLD + Color.YELLOW,
        align='center'
    )
    root.add_child_at(title, 0, 0, 1, 3)
    
    for i in range(6):
        row = (i // 2) + 1
        col = i % 2
        
        button = Button(
            text=f"Button {i+1}",
            color=Color.WHITE,
            bg_color=[Color.RED, Color.GREEN, Color.BLUE, Color.MAGENTA, Color.CYAN, Color.YELLOW][i]
        )
        root.add_child_at(button, row, col)
    
    info_text = Text(
        text="This demonstrates grid layout with buttons in a 2x3 arrangement",
        color=Color.BRIGHT_WHITE,
        align='center',
        wrap=True
    )
    root.add_child_at(info_text, 2, 2)
    
    screen.set_root(root)
    return screen


def create_progress_demo():
    screen = Screen()
    
    root = Box(direction='vertical', padding=5, spacing=2, width=80, height=24)
    
    title = Text(
        text="Progress Bar Demo",
        color=Color.BOLD + Color.GREEN,
        align='center',
        width=70,
        height=1
    )
    root.add_child(title)
    
    progress_bars = []
    for i in range(4):
        progress = ProgressBar(
            value=i * 25,
            width=60,
            height=3,
            border=True,
            show_percentage=True,
            fill_color=[Color.RED, Color.YELLOW, Color.BLUE, Color.GREEN][i]
        )
        progress_bars.append(progress)
        root.add_child(progress)
    
    def animate_progress():
        for i, progress in enumerate(progress_bars):
            progress.value = (progress.value + (i + 1) * 2) % 101
    
    screen.set_root(root)
    return screen, animate_progress


def main():
    print("Slav Terminal UI Demo")
    print("1. Basic Components Demo")
    print("2. Grid Layout Demo") 
    print("3. Progress Bar Demo")
    
    choice = input("Select demo (1-3): ").strip()
    
    if choice == "1":
        screen = create_basic_demo()
        screen.run()
    elif choice == "2":
        screen = create_grid_demo()
        screen.run()
    elif choice == "3":
        screen, animate_func = create_progress_demo()
        
        import threading
        def animation_loop():
            while screen.running:
                animate_func()
                time.sleep(0.1)
        
        animation_thread = threading.Thread(target=animation_loop)
        animation_thread.daemon = True
        animation_thread.start()
        
        screen.run()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
