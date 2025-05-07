import pyglet
from pyglet.window import Window

main_window = pyglet.window.Window(
    width=800,
    height=600,
    caption="Epic multiplayer", 
    vsync=False
)

@main_window.event
def on_draw():
    main_window.clear()