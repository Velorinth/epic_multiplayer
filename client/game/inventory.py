import arcade
from arcade.types import Rect
from loader.content import yml_content
from loader.content import get_object_properties as get_content

class Inventory:
    def __init__(self):
        self.items = []
        self.items_text = {}
        self.draw_x = 0
        self.draw_y = 0
        self.font_size = 12
        self.text_color = arcade.color.WHITE
        self.is_open = False
        
        # Create a reusable shape list
        self.shape_list = arcade.shape_list.ShapeElementList()
        
    def add_item(self, item):
        """Add an item to the inventory"""
        if item not in self.items:
            self.items.append(item)
            # Create text object for new item
            self.items_text[item] = arcade.Text(
                get_content(item)['name'],
                0,  # Will be updated in update_inventory
                0,  # Will be updated in update_inventory
                self.text_color,
                self.font_size
            )
            self.updated = True
    
    def remove_item(self, item):
        """Remove an item from the inventory"""
        if item in self.items:
            self.items.remove(item)
            del self.items_text[item]
            self.updated = True

    def on_key_press_inventory(self, symbol, modifiers):
        """Handle key press events"""
        if symbol == arcade.key.TAB:
            self.is_open = not self.is_open
            self.updated = True

    def update_inventory(self, screen_width, screen_height):
        """Update and draw the inventory"""
        if not self.is_open:
            return
            
        # Clear existing shapes
        self.shape_list.clear()
        
        # Update item positions
        self.draw_y = screen_height/2
        for item in self.items:
            # Draw item background
            item_bg = arcade.shape_list.create_rectangle_filled(
                screen_width/2,
                self.draw_y,
                100,
                20,
                (50, 50, 50, 128)
            )
            self.shape_list.append(item_bg)
            
            # Update text position
            text = self.items_text[item]
            text.position = (screen_width/2 - 50, self.draw_y - 5)
            self.draw_y += 20
        
        # Draw all shapes in a single batch
        self.shape_list.draw()
        
        # Draw all text objects
        for text in self.items_text.values():
            text.draw()