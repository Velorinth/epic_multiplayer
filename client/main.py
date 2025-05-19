from arcade import Window
import arcade
from arcade.camera import Camera2D
from arcade.types import Rect
import os
from loader.content import yml_content, load_content
from render.renderer import draw, draw_map, update_camera_position, draw_player
from game.player import Player
from game.inventory import Inventory
from game.music import MusicPlayer
import time
# Change working directory to project root
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

fps_limit = 999099999

# Create window and set up Arcade
class GameWindow(arcade.Window):
    def __init__(self, width, height, title):
        self.fps_limit = fps_limit
        super().__init__(width, height, title, update_rate=1/self.fps_limit, draw_rate=1/self.fps_limit, vsync=False, resizable=True)
        self.frame_times = []
        self.last_time = time.time()
        self.prnt_cntr = 0
        content = load_content()
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
        self.inventory = Inventory()

        self.inventory.add_item("dirt")
        self.inventory.add_item("sand")
        self.inventory.add_item("water")
        self.inventory.add_item("player")
        self.music_player = MusicPlayer()
        self.music_player.load_song()
        self.music_player.play()
        
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
        
        self.gui_camera.use()
        self.inventory.update_inventory(self.width, self.height)

        # frame rate
        current_time = time.time()
        self.frame_times.append(current_time)
        self.frame_times = [t for t in self.frame_times if current_time - t <= 1.0]
        fps = len(self.frame_times)
        if self.prnt_cntr <= fps/2:
            self.prnt_cntr += 1
            return
        else:
            self.prnt_cntr = 0
            print(f"pos: {self.player.get_position()}")
            print(f"FPS: {fps:.2f}")
    def on_update(self, delta_time):
        """Update function"""
        self.player.key_movement(dt=delta_time)
        # Update camera position
        player_pos = self.player.get_position()
        self.camera.position = player_pos
        update_camera_position(player_pos[0], player_pos[1], self.player)
        


    def on_key_press(self, symbol, modifiers):
        self.player.on_key_press_player(symbol, modifiers)
        self.inventory.on_key_press_inventory(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        self.player.on_key_release_player(symbol, modifiers)

if __name__ == "__main__":
    window = GameWindow(800, 600, "Epic Multiplayer!!11!!11!11")
    window.set_update_rate(1.0/fps_limit)
    arcade.run()