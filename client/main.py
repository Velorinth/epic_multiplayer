from arcade import Window
import arcade
from arcade.camera import Camera2D
from arcade.types import Rect
import os
from loader.content import yml_content, load_content
from render.renderer import draw, draw_map, update_camera_position, draw_player
from game.player import Player

# Change working directory to project root
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create window and set up Arcade
class GameWindow(arcade.Window):
    def __init__(self, width, height, title):
        content = load_content()
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)
        
        # Set up the camera
        viewport = Rect(
            left=0,
            right=width,
            bottom=0,
            top=height,
            width=width,
            height=height,
            x=0,
            y=0
        )
        self.camera = Camera2D(viewport=viewport)
        self.gui_camera = Camera2D(viewport=viewport)
        
        # Initialize game
        self.setup()
        
    def setup(self):
        """Set up the game and initialize the variables."""
        # Create player
        self.player = Player()
        
        # Initialize the map (create sprites)
        draw_map()
        draw_player(self.player)



    def on_draw(self):
        """Draw the window contents"""
        self.clear()
        
        # Draw the game using the game camera
        self.camera.use()
        draw()
        
        # Draw the GUI using the GUI camera
        self.gui_camera.use()

    def on_update(self, delta_time):
        """Update function"""
        self.player.key_movement(dt=delta_time)
        # Update camera position
        player_pos = self.player.get_position()
        self.camera.position = player_pos
        update_camera_position(player_pos[0], player_pos[1], self.player)
        


    def on_key_press(self, symbol, modifiers):
        self.player.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        self.player.on_key_release(symbol, modifiers)

if __name__ == "__main__":
    window = GameWindow(800, 600, "Epic Multiplayer!!11!!11!11")
    window.set_update_rate(1.0/170.0)
    arcade.run()