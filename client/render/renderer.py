import pyglet
from pyglet.graphics import Batch
from pyglet.sprite import Sprite
from loader.content import yml_content

batch = Batch()

def initialize_map():
    tile_size = 32
    map = yml_content['map']

def draw_map():
    for i in map['layout']['grid']:
        texture = pyglet.image.load(f"assets/tiles/{i['tile']}.png")
        Sprite(texture, x=i['x'] * tile_size, y=i['y'] * tile_size, batch=batch)