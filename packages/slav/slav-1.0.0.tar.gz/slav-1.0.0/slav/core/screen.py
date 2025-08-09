import sys
import time
from typing import List, Optional, Tuple
from .component import Component
from .event import KeyEvent, MouseEvent
from ..utils.terminal import Terminal
from ..utils.keys import Key


class Screen:
    def __init__(self):
        self.terminal = Terminal()
        self.root_component: Optional[Component] = None
        self.focused_component: Optional[Component] = None
        self.running = False
        self.fps = 60
        self.last_render_time = 0
        
    def set_root(self, component: Component):
        self.root_component = component
        
    def set_focused(self, component: Component):
        if self.focused_component:
            self.focused_component.blur()
        self.focused_component = component
        if component:
            component.focus()
            
    def find_next_focusable(self, current: Component = None, reverse: bool = False) -> Optional[Component]:
        if not self.root_component:
            return None
            
        def collect_focusable(comp: Component, result: List[Component]):
            if comp.focusable and comp.visible:
                result.append(comp)
            for child in comp.children:
                collect_focusable(child, result)
                
        focusable = []
        collect_focusable(self.root_component, focusable)
        
        if not focusable:
            return None
            
        if current is None:
            return focusable[0] if not reverse else focusable[-1]
            
        try:
            current_index = focusable.index(current)
            if reverse:
                next_index = (current_index - 1) % len(focusable)
            else:
                next_index = (current_index + 1) % len(focusable)
            return focusable[next_index]
        except ValueError:
            return focusable[0] if not reverse else focusable[-1]
            
    def handle_key(self, key: str):
        if key == Key.TAB:
            next_component = self.find_next_focusable(self.focused_component)
            if next_component:
                self.set_focused(next_component)
            return
            
        if key == '\033[Z':
            next_component = self.find_next_focusable(self.focused_component, reverse=True)
            if next_component:
                self.set_focused(next_component)
            return
            
        event = KeyEvent(key, self.focused_component)
        if self.focused_component:
            self.focused_component.handle_event(event)
        elif self.root_component:
            self.root_component.handle_event(event)
            
    def render(self):
        if not self.root_component:
            return
            
        width, height = self.terminal.get_size()
        buffer = [[' ' for _ in range(width)] for _ in range(height)]
        
        self.root_component.render(buffer)
        
        self.terminal.move_cursor(0, 0)
        for y, row in enumerate(buffer):
            if y > 0:
                sys.stdout.write('\n')
            sys.stdout.write(''.join(row))
        self.terminal.flush()
        
    def run(self):
        self.running = True
        
        with self.terminal:
            if self.root_component:
                width, height = self.terminal.get_size()
                self.root_component.resize(width, height)
                
                first_focusable = self.find_next_focusable()
                if first_focusable:
                    self.set_focused(first_focusable)
                    
            while self.running:
                current_time = time.time()
                
                key = self.terminal.get_key()
                if key:
                    if key == '\x03' or key == Key.ESCAPE:
                        break
                    self.handle_key(key)
                    
                if current_time - self.last_render_time >= 1.0 / self.fps:
                    self.render()
                    self.last_render_time = current_time
                    
                time.sleep(0.01)
                
    def stop(self):
        self.running = False
