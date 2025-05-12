import pyglet
import os
from loader.content import yml_content, load_content
from render.renderer import draw, draw_map, update_camera_position, draw_player
from render.camera import Camera
from game.player import Player

# Change working directory to project root
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create window and FPS display
window = pyglet.window.Window(
    width=800,
    height=600,
    vsync=False,
    resizable=True,
    caption="Epic Multiplayer!!11!!11!11",
    fullscreen=False,
    )
fps_display = pyglet.window.FPSDisplay(window)

player = Player()
camera = Camera()

@window.event
def on_draw():
    """Draw the window contents"""
    window.clear()
    draw()  # Call the draw function which uses batch.draw()
    fps_display.draw()

def update(dt):
    """Update function called at 170Hz"""
    player.update(dt)
    update_camera_position(player.get_position()[0], player.get_position()[1], player)


# Set the update rate to 170Hz (1/0.005882 = 170)
pyglet.clock.schedule_interval(update, 1.0/170.0)

def app_start():
    """Start the application"""
    content = load_content()
    if content is None:
        print("Failed to load content")
        return
    
    print("Content loaded successfully")
    print("Loaded content:", content)

    # Initialize the map (create sprites)
    draw_map()  # This creates all the sprites and adds them to the batch

    draw_player(player)

    @window.event
    def on_key_press(symbol, modifiers):
        player.on_key_press(symbol, modifiers)

    @window.event
    def on_key_release(symbol, modifiers):
        player.on_key_release(symbol, modifiers)

    # Start the application
    pyglet.app.run()

if __name__ == "__main__":
    app_start()