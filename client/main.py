import arcade
from arcade.camera import Camera2D
import os
import time
import threading

from networking.main import start_client, entities
from loader.content import load_content, get_object_properties
from render.renderer import draw, draw_map, initialize_renderer, active_sprites
from game.player import Player
from game.inventory import Inventory
from game.music import MusicPlayer
from entity.entity import Entity, update_entities

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class GameWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, vsync=True, resizable=True)
        self.set_location(400, 200)
        
        load_content()
        arcade.set_background_color(arcade.color.BLACK)
        self.mouse_x = 0
        self.mouse_y = 0
        self.camera = Camera2D()
        self.gui_camera = Camera2D()
        
        self.player = Player()
        
        self.inventory = Inventory()
        self.music_player = MusicPlayer()

        self.network_thread = threading.Thread(
            target=start_client, args=(self.player,), daemon=True
        )
        self.network_thread.start()

        # Test Entity for offline development
        if not any(e.proto == 'player' for e in entities.values()):
            ent = Entity(id=1, proto="player", x=0, y=0)
            entities[ent.id] = ent
        item1 = Entity(id=2, proto="cheese", x=10, y=0)
        entities[item1.id] = item1
        self.inventory.add_item(item1)
        item1 = Entity(id=3, proto="cheese", x=10, y=2)
        entities[item1.id] = item1
        self.inventory.add_item(item1)
        item1 = Entity(id=4, proto="dirt", x=10, y=0)
        entities[item1.id] = item1
        self.inventory.add_item(item1)
        item1 = Entity(id=5, proto="dirt", x=10, y=2)
        entities[item1.id] = item1
        self.inventory.add_item(item1)
        self.music_player.load_song()
        self.music_player.play()
        print(entities)

    def on_draw(self):
        self.clear()
        
        self.camera.use()
        draw_map(self)
        draw()
        
        self.gui_camera.use()
        self.inventory.draw(self.width, self.height, self.mouse_x, self.mouse_y)

    def on_update(self, delta_time: float):
        initialize_renderer()
        
        self.player.on_update(delta_time)
        
        update_entities()

        # Only move the camera if the player is fully linked and ready.
        if self.player.entity:
            player_x, player_y = self.player.get_position()
            
            # This is the correct, backwards-compatible camera logic.
            self.camera.position = (
                player_x,
                player_y,
            )

    def on_resize(self, width: int, height: int):
        self.camera.viewport_width = width
        self.camera.viewport_height = height
        self.gui_camera.viewport_width = width
        self.gui_camera.viewport_height = height

    def on_key_press(self, symbol, modifiers):
        self.player.on_key_press_player(symbol, modifiers)
        self.inventory.on_key_press_inventory(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        self.player.on_key_release_player(symbol, modifiers)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        self.inventory.on_mouse_press(x, y, button, modifiers)
        print(entities)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        """Called when the user moves the mouse."""
        self.mouse_x = x
        self.mouse_y = y
        self.inventory.on_mouse_motion(x, y, dx, dy)

if __name__ == "__main__":
    window = GameWindow(800, 600, "Epic Multiplayer")
    arcade.run()