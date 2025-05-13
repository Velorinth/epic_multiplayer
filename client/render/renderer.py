import arcade
import os
from loader.content import yml_content
from loader.content import get_object_properties as get_content

loaded_textures = {}

sprite_list = arcade.SpriteList()

def draw_map():
    """Draw the map tiles"""
    tile_size = 32
    map = yml_content['map']
    
    for tile in map['layout']['tiles']:
        tile_name = tile['tile']
        tile_props = get_content(tile_name)
        if tile_props["texture"] not in loaded_textures:
            loaded_textures[tile_props["texture"]] = arcade.load_texture(f"assets/textures/{tile_props['texture']}")
        texture = loaded_textures[tile_props["texture"]]
        
        # Create sprite
        sprite = arcade.Sprite(texture,
                              center_x=tile['x'] * tile_size,
                              center_y=tile['y'] * tile_size)
        
        # Calculate scaling factors to make the sprite exactly tile_size x tile_size
        sprite.scale = tile_size / max(texture.width, texture.height)
        
        # Set initial position
        sprite.position = (tile['x'] * tile_size, tile['y'] * tile_size)
        
        tile['sprite'] = sprite
        sprite_list.append(sprite)

# Store original positions when the map is loaded
original_positions = {}

def update_camera_position(camera_x, camera_y, player):
    """Update all sprite positions based on camera position"""
    # Update map sprites
    for sprite in sprite_list:
        # If we don't have the original position stored, store it
        if id(sprite) not in original_positions:
            original_positions[id(sprite)] = (sprite.center_x, sprite.center_y)
        
        # Calculate position relative to camera
        original_x, original_y = original_positions[id(sprite)]
        sprite.center_x = original_x - camera_x
        sprite.center_y = original_y - camera_y
    
    # Update player sprite if it exists
    if hasattr(player, 'sprite'):
        player.sprite.center_x = player.x
        player.sprite.center_y = player.y

def draw_player(player):
    """Draw the player"""
    tile_name = 'player'
    tile_props = get_content(tile_name)
    if tile_props["texture"] not in loaded_textures:
        loaded_textures[tile_props["texture"]] = arcade.load_texture(f"assets/textures/{tile_props['texture']}")
    texture = loaded_textures[tile_props["texture"]]
    sprite = arcade.Sprite(texture,
                          center_x=player.x,
                          center_y=player.y)
    
    player.sprite = sprite
    sprite_list.append(sprite)

def draw():
    """Draw all sprites in the sprite list"""
    sprite_list.draw()
    
    # Draw debug info
    arcade.draw_text(f"Sprites: {len(sprite_list)}", 10, 10, arcade.color.WHITE, 12)