import pyglet
from loader.content import yml_content, load_content
from camera.window import main_window
from camera.map import MapRenderer

map_renderer = None

def app_start():
    load_content()
    global map_renderer
    map_renderer = MapRenderer(main_window)
    
    # Add the draw event to main_window
    @main_window.event
    def on_draw():
        main_window.clear()
        if map_renderer:
            map_renderer.draw()
    pyglet.app.run()

app_start()