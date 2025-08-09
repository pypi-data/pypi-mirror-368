from typing import List, Literal
from ..core.component import Component


class Box(Component):
    def __init__(self, direction: Literal['horizontal', 'vertical'] = 'vertical',
                 spacing: int = 0, padding: int = 0,
                 x: int = 0, y: int = 0, width: int = 10, height: int = 10,
                 align: Literal['start', 'center', 'end', 'stretch'] = 'start',
                 justify: Literal['start', 'center', 'end', 'space-between', 'space-around'] = 'start'):
        super().__init__(x, y, width, height)
        self.direction = direction
        self.spacing = spacing
        self.padding = padding
        self.align = align
        self.justify = justify
        
    def add_child(self, child: Component):
        super().add_child(child)
        self._layout_children()
        
    def remove_child(self, child: Component):
        super().remove_child(child)
        self._layout_children()
        
    def resize(self, width: int, height: int):
        super().resize(width, height)
        self._layout_children()
        
    def _layout_children(self):
        if not self.children:
            return
            
        content_width = self.width - 2 * self.padding
        content_height = self.height - 2 * self.padding
        
        if self.direction == 'horizontal':
            self._layout_horizontal(content_width, content_height)
        else:
            self._layout_vertical(content_width, content_height)
            
    def _layout_horizontal(self, content_width: int, content_height: int):
        total_spacing = (len(self.children) - 1) * self.spacing
        available_width = content_width - total_spacing
        
        if self.align == 'stretch':
            child_height = content_height
        else:
            child_height = max(child.height for child in self.children)
            
        if self.justify == 'stretch':
            child_width = available_width // len(self.children)
        else:
            child_width = min(available_width // len(self.children), 
                            max(child.width for child in self.children))
            
        start_x = self.padding
        if self.justify == 'center':
            total_width = sum(child.width for child in self.children) + total_spacing
            start_x = self.padding + (content_width - total_width) // 2
        elif self.justify == 'end':
            total_width = sum(child.width for child in self.children) + total_spacing
            start_x = self.padding + content_width - total_width
            
        current_x = start_x
        for i, child in enumerate(self.children):
            if self.justify == 'space-between':
                if len(self.children) > 1:
                    current_x = self.padding + i * (content_width - child.width) // (len(self.children) - 1)
            elif self.justify == 'space-around':
                space = content_width // (len(self.children) + 1)
                current_x = self.padding + (i + 1) * space - child.width // 2
                
            child.x = current_x
            
            if self.align == 'center':
                child.y = self.padding + (content_height - child.height) // 2
            elif self.align == 'end':
                child.y = self.padding + content_height - child.height
            else:
                child.y = self.padding
                
            if self.align == 'stretch':
                child.height = child_height
            if self.justify == 'stretch':
                child.width = child_width
                
            current_x += child.width + self.spacing
            
    def _layout_vertical(self, content_width: int, content_height: int):
        total_spacing = (len(self.children) - 1) * self.spacing
        available_height = content_height - total_spacing
        
        if self.align == 'stretch':
            child_width = content_width
        else:
            child_width = max(child.width for child in self.children)
            
        if self.justify == 'stretch':
            child_height = available_height // len(self.children)
        else:
            child_height = min(available_height // len(self.children), 
                             max(child.height for child in self.children))
            
        start_y = self.padding
        if self.justify == 'center':
            total_height = sum(child.height for child in self.children) + total_spacing
            start_y = self.padding + (content_height - total_height) // 2
        elif self.justify == 'end':
            total_height = sum(child.height for child in self.children) + total_spacing
            start_y = self.padding + content_height - total_height
            
        current_y = start_y
        for i, child in enumerate(self.children):
            if self.justify == 'space-between':
                if len(self.children) > 1:
                    current_y = self.padding + i * (content_height - child.height) // (len(self.children) - 1)
            elif self.justify == 'space-around':
                space = content_height // (len(self.children) + 1)
                current_y = self.padding + (i + 1) * space - child.height // 2
                
            child.y = current_y
            
            if self.align == 'center':
                child.x = self.padding + (content_width - child.width) // 2
            elif self.align == 'end':
                child.x = self.padding + content_width - child.width
            else:
                child.x = self.padding
                
            if self.align == 'stretch':
                child.width = child_width
            if self.justify == 'stretch':
                child.height = child_height
                
            current_y += child.height + self.spacing
            
    def render(self, buffer: List[List[str]]):
        if not self.visible:
            return
        self.render_children(buffer)
