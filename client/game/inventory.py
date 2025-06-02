import arcade
# from arcade.types import Rect # Not explicitly used, can be removed if Rect is not needed elsewhere
# from loader.content import yml_content # Assuming this is used by get_content
from loader.content import get_object_properties as get_content

class Inventory:
    # --- Constants for easy appearance tuning ---
    ITEM_RECT_WIDTH = 150  # Increased width for potentially longer names
    ITEM_RECT_HEIGHT = 25
    ITEM_VERTICAL_SPACING = 30  # Center-to-center Y distance between items (includes margin)
    ITEM_BG_COLOR = (50, 50, 50, 180) # Slightly more opaque
    TEXT_COLOR = arcade.color.WHITE
    FONT_SIZE = 12
    # Offset for text from the bottom-left corner of its background rectangle
    TEXT_X_OFFSET_IN_RECT = 5 
    TEXT_Y_OFFSET_IN_RECT = (ITEM_RECT_HEIGHT - FONT_SIZE) / 2 # Vertically center text in rect

    def __init__(self):
        self.items = []  # List of item keys/identifiers
        self.items_text = {}  # Maps item key to its arcade.Text object
        
        self.is_open = False
        
        self.shape_list = arcade.shape_list.ShapeElementList()
        
        # --- State for performance optimization and click detection ---
        self._needs_visual_rebuild = True # Flag to trigger regeneration of visual elements
        self._last_screen_width = 0
        self._last_screen_height = 0
        self._clickable_areas = []  # Stores (left, bottom, width, height, item_original_index)

    def add_item(self, item_key):
        """Add an item to the inventory by its key."""
        if item_key not in self.items:
            self.items.append(item_key)
            # Create text object for new item. Position will be set during visual rebuild.
            item_name = "Unknown Item" # Default name
            try:
                content = get_content(item_key)
                if content and 'name' in content:
                    item_name = content['name']
                else:
                    print(f"Warning: No name found for item key '{item_key}' in content.")
            except Exception as e:
                print(f"Error fetching content for item '{item_key}': {e}")

            self.items_text[item_key] = arcade.Text(
                item_name,
                0,  # Placeholder, actual position set in _rebuild_visuals
                0,  # Placeholder
                self.TEXT_COLOR,
                self.FONT_SIZE
            )
            self._needs_visual_rebuild = True # Mark that visuals need updating
    
    def remove_item(self, item_key):
        """Remove an item from the inventory by its key."""
        if item_key in self.items:
            self.items.remove(item_key)
            if item_key in self.items_text:
                del self.items_text[item_key]
            self._needs_visual_rebuild = True # Mark that visuals need updating
        else:
            print(f"Item '{item_key}' not found in inventory for removal.")

    def on_key_press_inventory(self, symbol, modifiers):
        """Handle key press events relevant to the inventory (e.g., toggling)."""
        if symbol == arcade.key.TAB:
            self.is_open = not self.is_open
            if self.is_open:
                # When opening, always flag for a rebuild in case screen size changed
                # or to ensure it's drawn correctly for the first time.
                self._needs_visual_rebuild = True 

    def _rebuild_visuals(self, screen_width, screen_height):
        """
        Private method. Recreates background shapes, updates text positions, 
        and stores clickable areas. Called only when necessary.
        """
        self.shape_list.clear()
        self._clickable_areas.clear()

        if not self.items:
            self._needs_visual_rebuild = False
            self._last_screen_width = screen_width
            self._last_screen_height = screen_height
            return

        center_x = screen_width / 2
        num_items = len(self.items)

        # Calculate the Y coordinate for the center of the *first* (bottom-most) item
        # to center the entire list vertically.
        # Total height spanned by item centers: (num_items - 1) * ITEM_VERTICAL_SPACING
        total_list_centers_span = (num_items - 1) * self.ITEM_VERTICAL_SPACING
        first_item_center_y = (screen_height / 2) - (total_list_centers_span / 2)

        current_item_center_y = first_item_center_y

        for idx, item_key in enumerate(self.items):
            # Create item background shape
            item_bg = arcade.shape_list.create_rectangle_filled(
                center_x,
                current_item_center_y,
                self.ITEM_RECT_WIDTH,
                self.ITEM_RECT_HEIGHT,
                self.ITEM_BG_COLOR
            )
            self.shape_list.append(item_bg)
            
            # Calculate rectangle's bottom-left for positioning text and click area
            rect_left = center_x - self.ITEM_RECT_WIDTH / 2
            rect_bottom = current_item_center_y - self.ITEM_RECT_HEIGHT / 2

            # Store clickable area: (left, bottom, width, height, original_item_index)
            self._clickable_areas.append(
                (rect_left, rect_bottom, self.ITEM_RECT_WIDTH, self.ITEM_RECT_HEIGHT, idx)
            )
            
            # Update text object's position
            if item_key in self.items_text:
                text_obj = self.items_text[item_key]
                text_obj.position = (
                    rect_left + self.TEXT_X_OFFSET_IN_RECT,
                    rect_bottom + self.TEXT_Y_OFFSET_IN_RECT
                )
                # Ensure text properties if they might change or for consistency
                text_obj.color = self.TEXT_COLOR
                text_obj.font_size = self.FONT_SIZE
            else:
                # This should ideally not happen if add_item and remove_item are used correctly
                print(f"Warning: Text object for item key '{item_key}' not found during visual rebuild.")

            current_item_center_y += self.ITEM_VERTICAL_SPACING # Move to next item slot (upwards)
        
        self._needs_visual_rebuild = False
        self._last_screen_width = screen_width
        self._last_screen_height = screen_height

    def draw_inventory(self, screen_width, screen_height):
        """Draw the inventory if it's open. Rebuilds visuals if needed."""
        if not self.is_open:
            return
            
        # Check if a visual rebuild is necessary
        if (self._needs_visual_rebuild or 
            self._last_screen_width != screen_width or
            self._last_screen_height != screen_height):
            self._rebuild_visuals(screen_width, screen_height)
        
        # Draw all background shapes (batched)
        self.shape_list.draw()
        
        # Draw all text objects. Iterating self.items ensures draw order matches logical order.
        for item_key in self.items:
            if item_key in self.items_text:
                self.items_text[item_key].draw()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """
        Handles mouse clicks for inventory items. Call this from your game's main
        on_mouse_press method when the inventory might be active.
        
        Returns:
            int: The index of the clicked item in the self.items list.
            None: If no item was clicked, inventory is closed, or not a left click.
        """
        if not self.is_open or button != arcade.MOUSE_BUTTON_LEFT:
            return None # Inventory not open or not a left click

        for r_x, r_y, r_width, r_height, item_original_idx in self._clickable_areas:
            # Check if point (x,y) is within the rectangle defined by (r_x, r_y, r_width, r_height)
            if (r_x <= x <= r_x + r_width) and (r_y <= y <= r_y + r_height):
                clicked_item_key = self.items[item_original_idx]
                item_name = "N/A"
                if clicked_item_key in self.items_text:
                    item_name = self.items_text[clicked_item_key].text

                print(f"Clicked inventory item at index: {item_original_idx}, Key: '{clicked_item_key}', Name: '{item_name}'")
                
                # --- Example: Placeholder for using/interacting with the item ---
                # self.use_item(item_original_idx) 
                # self.is_open = False # Optionally close inventory after click
                # self._needs_visual_rebuild = True # If closing, may want to mark for rebuild
                
                return item_original_idx # Return the index of the clicked item

        return None # Click was not on any inventory item