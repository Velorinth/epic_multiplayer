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
        self.updated = True
        
        # Create a reusable shape list
        self.shape_list = arcade.shape_list.ShapeElementList()
        
        # Create a single text object for all inventory items
        self.all_text = arcade.Text(
            "",
            0,
            0,
            self.text_color,
            self.font_size
        )
        
    def add_item(self, item):
        """Add an item to the inventory"""
        if item not in self.items:
            self.items.append(item)
            self.updated = True
    
    def remove_item(self, item):
        """Remove an item from the inventory"""
        if item in self.items:
            self.items.remove(item)
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
            
        # Only update if inventory state changed
        if not self.updated:
            return
            
        # Clear existing shapes
        self.shape_list.clear()
        
        # Build the text string
        text_str = ""
        self.draw_y = screen_height/2
        
        # Update item positions and build text
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
            
            # Add text to string
            text_str += get_content(item)['name'] + "\n"
            self.draw_y += 20
        
        # Update text object
        self.all_text.text = text_str
        self.all_text.position = (screen_width/2 - 50, screen_height/2 - (20 * len(self.items)) + 10)
        
        # Draw all shapes in a single batch
        self.shape_list.draw()
        
        # Draw text in a single call
        self.all_text.draw()