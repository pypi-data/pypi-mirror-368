import pytest
from slav.core.component import Component
from slav.core.event import Event, EventEmitter, KeyEvent
from slav.core.screen import Screen
from slav.components.text import Text


class MockComponent(Component):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.render_called = False
        
    def render(self, buffer):
        self.render_called = True


class TestComponent:
    def test_component_creation(self):
        comp = MockComponent(x=10, y=20, width=30, height=40)
        assert comp.x == 10
        assert comp.y == 20
        assert comp.width == 30
        assert comp.height == 40
        assert comp.visible == True
        assert comp.focused == False
        
    def test_component_hierarchy(self):
        parent = MockComponent()
        child = MockComponent()
        
        parent.add_child(child)
        assert child in parent.children
        assert child.parent == parent
        
        parent.remove_child(child)
        assert child not in parent.children
        assert child.parent is None
        
    def test_component_absolute_position(self):
        parent = MockComponent(x=10, y=10)
        child = MockComponent(x=5, y=5)
        
        parent.add_child(child)
        abs_x, abs_y = child.get_absolute_position()
        assert abs_x == 15
        assert abs_y == 15
        
    def test_component_contains_point(self):
        comp = MockComponent(x=10, y=10, width=20, height=15)
        
        assert comp.contains_point(15, 15) == True
        assert comp.contains_point(29, 24) == True
        assert comp.contains_point(5, 5) == False
        assert comp.contains_point(35, 30) == False
        
    def test_component_focus(self):
        comp = MockComponent()
        comp.focusable = True
        
        assert comp.focused == False
        comp.focus()
        assert comp.focused == True
        
        comp.blur()
        assert comp.focused == False


class TestEventEmitter:
    def test_event_emission(self):
        emitter = EventEmitter()
        
        called = False
        def callback(event):
            nonlocal called
            called = True
            
        emitter.on('test', callback)
        event = Event('test')
        emitter.emit(event)
        
        assert called == True
        
    def test_event_removal(self):
        emitter = EventEmitter()
        
        called = False
        def callback(event):
            nonlocal called
            called = True
            
        emitter.on('test', callback)
        emitter.off('test', callback)
        
        event = Event('test')
        emitter.emit(event)
        
        assert called == False
        
    def test_event_stopping(self):
        emitter = EventEmitter()
        
        call_count = 0
        def callback1(event):
            nonlocal call_count
            call_count += 1
            event.stop_propagation()
            
        def callback2(event):
            nonlocal call_count
            call_count += 1
            
        emitter.on('test', callback1)
        emitter.on('test', callback2)
        
        event = Event('test')
        emitter.emit(event)
        
        assert call_count == 1


class TestScreen:
    def test_screen_creation(self):
        screen = Screen()
        assert screen.root_component is None
        assert screen.focused_component is None
        assert screen.running == False
        
    def test_screen_set_root(self):
        screen = Screen()
        root = Text("Root")
        
        screen.set_root(root)
        assert screen.root_component == root
        
    def test_screen_focus_management(self):
        screen = Screen()
        comp1 = MockComponent()
        comp1.focusable = True
        comp2 = MockComponent()
        comp2.focusable = True
        
        screen.set_focused(comp1)
        assert screen.focused_component == comp1
        assert comp1.focused == True
        
        screen.set_focused(comp2)
        assert screen.focused_component == comp2
        assert comp1.focused == False
        assert comp2.focused == True
