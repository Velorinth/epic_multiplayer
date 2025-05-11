import pyglet
import os
from pyglet.graphics import Batch
from pyglet.sprite import Sprite
from loader.content import yml_content
from loader.content import get_object_properties as get_content

loaded_textures = {}

batch = Batch()

def draw_map():
    """Draw the map tiles"""
    tile_size = 32
    map = yml_content['map']
    
    for tile in map['layout']['tiles']:
        tile_name = tile['tile']
        tile_props = get_content(tile_name)
        if tile_props["texture"] not in loaded_textures:
            loaded_textures[tile_props["texture"]] = pyglet.image.load(f"assets/textures/{tile_props['texture']}")
        texture = loaded_textures[tile_props["texture"]]
        sprite = Sprite(texture, 
                        x=tile['x'] * tile_size, 
                        y=tile['y'] * tile_size,
                        batch=batch)
        
        # Calculate scaling factors to make the sprite exactly tile_size x tile_size
        sprite.scale_x = tile_size / texture.width
        sprite.scale_y = tile_size / texture.height
        
        tile['sprite'] = sprite


def draw():
    """Draw all sprites in the batch"""
    batch.draw()