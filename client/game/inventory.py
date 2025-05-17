import arcade
from arcade.types import Rect
from loader.content import yml_content
from loader.content import get_object_properties as get_content

# Draw a semi-transparent black square
def draw_semi_transparent_square(x, y, width, height, alpha=128):  # alpha 0-255
    arcade.draw_rect_filled(
        Rect(
            left=x,
            right=x+width,
            bottom=y,
            top=y+height,
            width=width,
            height=height,
            x=x,
            y=y
        ),
        (50, 50, 50, alpha)  # RGBA tuple: (red, green, blue, alpha)
    )


class Inventory:
    def __init__(self):
        self.items = []
        self.draw_x = 0
        self.draw_y = 0
        self.font_size = 12
        self.text_color = arcade.color.WHITE
        self.updated = True    
    def add_item(self, item):
        self.updated = True
        self.items.append(item)
    
    def remove_item(self, item):
        self.updated = True
        self.items.remove(item)
    
    def update_inventory(self, screen_width, screen_height):
        self.draw_y = screen_height/2
        for item in self.items:
            draw_semi_transparent_square(screen_width/2, self.draw_y, 100, 20)   
            arcade.draw_text(
                get_content(item)['name'],
                screen_width/2-50,
                self.draw_y-5,
                self.text_color,
                self.font_size,
                align="left"
            )
            
            self.draw_y += 20