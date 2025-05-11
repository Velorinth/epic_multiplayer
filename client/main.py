import pyglet
import os
from loader.content import yml_content, load_content
from render.renderer import draw, draw_map

# Change working directory to project root
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create window and FPS display
window = pyglet.window.Window(width=800, height=600)
fps_display = pyglet.window.FPSDisplay(window)

@window.event
def on_draw():
    """Draw the window contents"""
    window.clear()
    draw()  # Call the draw function which uses batch.draw()
    fps_display.draw()

def update(dt):
    """Update function called at 170Hz"""
    draw_map()
    draw()
    pass  # You can add any update logic here if needed

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
    
    # Start the application
    pyglet.app.run()

if __name__ == "__main__":
    app_start()