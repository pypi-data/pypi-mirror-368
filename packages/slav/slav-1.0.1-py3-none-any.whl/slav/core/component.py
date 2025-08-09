from typing import Optional, List, Tuple, Any
from abc import ABC, abstractmethod
from .event import EventEmitter, Event


class Component(EventEmitter, ABC):
    def __init__(self, x: int = 0, y: int = 0, width: int = 10, height: int = 1):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.focusable = False
        self.focused = False
        self.parent: Optional['Component'] = None
        self.children: List['Component'] = []
        self.z_index = 0
        
    def add_child(self, child: 'Component'):
        child.parent = self
        self.children.append(child)
        
    def remove_child(self, child: 'Component'):
        if child in self.children:
            child.parent = None
            self.children.remove(child)
            
    def get_absolute_position(self) -> Tuple[int, int]:
        if self.parent:
            px, py = self.parent.get_absolute_position()
            return (px + self.x, py + self.y)
        return (self.x, self.y)
        
    def contains_point(self, x: int, y: int) -> bool:
        abs_x, abs_y = self.get_absolute_position()
        return (abs_x <= x < abs_x + self.width and 
                abs_y <= y < abs_y + self.height)
                
    def get_component_at(self, x: int, y: int) -> Optional['Component']:
        if not self.visible or not self.contains_point(x, y):
            return None
            
        for child in reversed(self.children):
            result = child.get_component_at(x, y)
            if result:
                return result
                
        return self
        
    def focus(self):
        if self.focusable:
            self.focused = True
            from .event import FocusEvent
            self.emit(FocusEvent(target=self, gained=True))
            
    def blur(self):
        if self.focused:
            self.focused = False
            from .event import FocusEvent
            self.emit(FocusEvent(target=self, gained=False))
            
    def move(self, x: int, y: int):
        self.x = x
        self.y = y
        
    def resize(self, width: int, height: int):
        self.width = width
        self.height = height
        
    def show(self):
        self.visible = True
        
    def hide(self):
        self.visible = False
        
    def handle_event(self, event: Event):
        if not self.visible:
            return
            
        self.emit(event)
        
        if event.bubbles and self.parent:
            self.parent.handle_event(event)
            
    @abstractmethod
    def render(self, buffer: List[List[str]]):
        pass
        
    def render_children(self, buffer: List[List[str]]):
        sorted_children = sorted(self.children, key=lambda c: c.z_index)
        for child in sorted_children:
            if child.visible:
                child.render(buffer)
