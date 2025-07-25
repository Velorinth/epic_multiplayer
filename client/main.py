#main script

#import libraries
from arcade import Window
import arcade
from arcade.camera import Camera2D
from arcade.types import Rect
import os
import time
import threading

#import game content
from networking.main import start_client, isConnectedToServer, entities
from loader.content import yml_content, load_content, get_object_properties
from render.renderer import draw, draw_map, update_camera_position, draw_player, active_sprites
from game.player import Player
from game.inventory import Inventory
from game.music import MusicPlayer
from entity.entity import Entity

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
        
        # Create player instance
        self.player = Player()  # Assuming Player class exists and is properly imported
        
        # Start network client in a separate thread
        self.network_thread = threading.Thread(
            target=start_client,
            args=(self.player,),  # Pass the player instance
            daemon=True  # This ensures the thread will close when the main program exits
        )
        self.network_thread.start()
        
        self.inventory.add_item("dirt")
        self.inventory.add_item("sand")
        self.inventory.add_item("water")
        self.inventory.add_item("player")
        self.music_player = MusicPlayer()
        self.music_player.load_song()
        self.music_player.play()
        self.dt = 0
        
        #time.sleep(2)
        ent = Entity(id=67786767, params=get_object_properties("cheese"))
        print(ent)
        entities[ent.id] = ent
        # Initialize the renderer after content is loaded
        from render.renderer import initialize_renderer
        initialize_renderer()
        
        # Initialize gamep
        self.setup()
        
    def setup(self):
        """Set up the game and initialize the variables."""
        # Initialize the map (create sprites)
        draw_player(self.player)

    def on_draw(self):
        """Draw the window contents"""
        self.clear()
        
        # Draw the game using the game camera
        self.camera.use()
        draw_map(self)
        draw()
        
        self.gui_camera.use()
        self.inventory.draw_inventory(self.width, self.height)

        self.player.on_update(self.dt)

        # Update FPS counter
        current_time = time.time()
        self.frame_times.append(current_time)
        
        # Only update debug info every 30 frames to reduce console spam
        if len(self.frame_times) % 30 == 0:
            # Calculate FPS based on last second of frames
            self.frame_times = [t for t in self.frame_times if current_time - t <= 1.0]
            fps = len(self.frame_times)
            
            # Get player position
            pos = self.player.get_position()
            
            # Print debug info in a single line
            '''
            print(f"Sprites: {len(active_sprites):<5} | "
                  f"Pos: ({pos[0]:.1f}, {pos[1]:.1f}) | "
                  f"FPS: {fps:3.0f}", end='\r')
            '''
            # Clear frame times occasionally to prevent memory growth
            if len(self.frame_times) > 120:  # Keep max 2 seconds of frame times
                self.frame_times = self.frame_times[-60:]  # Keep only last second
    def on_update(self, delta_time):
        """Update function"""
        self.dt = delta_time
        self.player.key_movement(dt=self.dt)
        # Update camera position
        player_pos = self.player.get_position()
        self.camera.position = player_pos
        update_camera_position(player_pos[0], player_pos[1], self.player)
        


    def on_key_press(self, symbol, modifiers):
        self.player.on_key_press_player(symbol, modifiers)
        self.inventory.on_key_press_inventory(symbol, modifiers)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """
        Called when the user presses a mouse button.
        
        Args:
            x: x position of mouse
            y: y position of mouse
            button: what button was hit
            modifiers: shift, ctrl, etc
        """
        # Pass the event to the inventory system
        self.inventory.on_mouse_press(x, y, button, modifiers)

    def on_key_release(self, symbol, modifiers):
        self.player.on_key_release_player(symbol, modifiers)

if __name__ == "__main__":
    window = GameWindow(800, 600, "Epic Multiplayer!!11!!11!11")
    window.set_update_rate(1.0/fps_limit)
    arcade.run()