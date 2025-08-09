#!/usr/bin/env python3

from ..core.screen import Screen
from ..components.text import Text
from ..components.button import Button
from ..layout.box import Box
from ..utils.colors import Color


def main():
    screen = Screen()
    
    root = Box(direction='vertical', padding=10, spacing=2, width=80, height=24)
    
    title = Text(
        text="Hello, Slav!",
        color=Color.BOLD + Color.CYAN,
        align='center',
        width=60,
        height=1
    )
    root.add_child(title)
    
    subtitle = Text(
        text="This is a simple example of the Slav terminal UI library.",
        color=Color.WHITE,
        align='center',
        width=60,
        height=1
    )
    root.add_child(subtitle)
    
    button = Button(
        text="Exit",
        width=12,
        height=3,
        on_click=lambda: screen.stop()
    )
    root.add_child(button)
    
    screen.set_root(root)
    screen.run()


if __name__ == "__main__":
    main()
