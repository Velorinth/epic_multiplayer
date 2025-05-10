import pyglet
from loader.content import yml_content, load_content
from render.renderer import batch, initialize_map, draw_map

window = pyglet.window.Window(width=800, height=600)

@window.event
def on_draw():
    window.clear()
    batch.draw()

def app_start():
    if not load_content():
        print("Failed to load content")
        return
    print("Content loaded successfully")
    pyglet.app.run()

if __name__ == "__main__":
    app_start()