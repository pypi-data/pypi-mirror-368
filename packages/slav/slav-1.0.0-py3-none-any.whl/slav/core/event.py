from typing import Any, Callable, Dict, List
from dataclasses import dataclass


@dataclass
class Event:
    type: str
    data: Any = None
    target: Any = None
    bubbles: bool = True
    cancelled: bool = False
    
    def stop_propagation(self):
        self.bubbles = False
        
    def cancel(self):
        self.cancelled = True


class EventEmitter:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        
    def on(self, event_type: str, callback: Callable):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
        
    def off(self, event_type: str, callback: Callable):
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(callback)
            except ValueError:
                pass
                
    def emit(self, event: Event):
        if event.type in self._listeners:
            for callback in self._listeners[event.type]:
                if event.cancelled:
                    break
                callback(event)
                if not event.bubbles:
                    break


class KeyEvent(Event):
    def __init__(self, key: str, target=None):
        super().__init__('key', key, target)
        self.key = key


class MouseEvent(Event):
    def __init__(self, x: int, y: int, button: str, target=None):
        super().__init__('mouse', {'x': x, 'y': y, 'button': button}, target)
        self.x = x
        self.y = y
        self.button = button


class FocusEvent(Event):
    def __init__(self, target=None, gained: bool = True):
        super().__init__('focus', gained, target)
        self.gained = gained
