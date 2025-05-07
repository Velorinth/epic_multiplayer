import pyglet
import yaml
from loader.content import yml_content, load_content

window = pyglet.window.Window(width=800, height=600, caption="Epic multiplayer")

def app_start():
    load_content()
    pyglet.app.run()

@window.event
def on_draw():
    window.clear()
    print(yml_content)

app_start()