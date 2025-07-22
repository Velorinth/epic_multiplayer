import arcade
import os
import time
from typing import Dict, List, Tuple, Set, Optional
from loader.content import get_object_properties as get_content
from dataclasses import dataclass
from networking.main import get_tile_map

# Constants
TILE_SIZE = 48
VIEWPORT_PADDING = 2  # Slightly increased padding to reduce updates when moving
TEXTURE_SCALE = TILE_SIZE / 32  # Assuming 32x32 textures by default

# Performance tracking
_last_update_time = 0
_update_interval = 0.1  # Update viewport every 100ms

# Game state
loaded_textures: Dict[str, arcade.Texture] = {}
active_sprites: arcade.SpriteList = arcade.SpriteList(use_spatial_hash=True)
tile_sprites: Dict[Tuple[int, int], arcade.Sprite] = {}
player_sprite: Optional[arcade.Sprite] = None
_initialized = False
_last_viewport = None  # Cache the last viewport to avoid unnecessary updates
_visible_tiles = set()  # Track currently visible tiles
_last_camera_pos = (0, 0)  # Track last camera position

@dataclass
class Viewport:
    left: float
    right: float
    bottom: float
    top: float
    width: float
    height: float

    @classmethod
    def from_camera(cls, camera_pos: Tuple[float, float], width: int, height: int) -> 'Viewport':
        """Create a viewport from camera position and window dimensions."""
        half_width = width / 2
        half_height = height / 2
        return cls(
            left=camera_pos[0] - half_width,
            right=camera_pos[0] + half_width,
            bottom=camera_pos[1] - half_height,
            top=camera_pos[1] + half_height,
            width=width,
            height=height
        )

def preload_textures() -> None:
    """Preload all textures used in the game."""
    unique_textures = set()
    
    # Get all unique tile textures if map is available
    tile_map = get_tile_map()
    if 'layout' in tile_map and 'tiles' in tile_map['layout']:
        for tile in tile_map['layout']['tiles']:
            try:
                tile_props = get_content(tile['tile'])
                if tile_props and 'texture' in tile_props:
                    unique_textures.add(tile_props["texture"])
            except (KeyError, TypeError):
                continue
    else:
        print('skill issue')
    # Get player texture
    try:
        player_props = get_content('player')
        if player_props and 'texture' in player_props:
            unique_textures.add(player_props["texture"])
    except (KeyError, TypeError):
        pass
    
    # Load all textures
    for texture_name in unique_textures:
        if texture_name and texture_name not in loaded_textures:
            try:
                loaded_textures[texture_name] = arcade.load_texture(f"assets/textures/{texture_name}")
            except (FileNotFoundError, arcade.resources.resource.ResourceError):
                print(f"Warning: Could not load texture: {texture_name}")

def init_map() -> None:
    """Initialize the map and create all tile sprites."""
    global tile_sprites
    
    tile_sprites.clear()
    
    tile_map = get_tile_map()

    # Check if map data is available
    if 'layout' not in tile_map or 'tiles' not in tile_map['layout']:
        print("Warning: Map data not available for initialization")
        raise "nah"
    
    map_data = tile_map
    
    for tile in map_data['layout']['tiles']:
        try:
            tile_name = tile.get('tile')
            if not tile_name:
                continue
                
            tile_props = get_content(tile_name)
            if not tile_props or 'texture' not in tile_props:
                continue
                
            texture_name = tile_props["texture"]
            if texture_name not in loaded_textures:
                continue
                
            texture = loaded_textures[texture_name]
            
            # Create sprite
            sprite = arcade.Sprite(texture)
            sprite.scale = TILE_SIZE / max(texture.width, texture.height)
            sprite.position = (round(tile['x'] * TILE_SIZE), round(tile['y'] * TILE_SIZE))
            
            # Store sprite with its grid position as key
            tile_sprites[(tile['x'], tile['y'])] = sprite
            
        except (KeyError, TypeError) as e:
            print(f"Warning: Error processing tile at ({tile.get('x')}, {tile.get('y')}): {e}")
            continue

def should_update_viewport(viewport: 'Viewport') -> bool:
    """Check if we should update the viewport based on movement."""
    global _last_update_time, _last_viewport
    
    current_time = time.time()
    if current_time - _last_update_time < _update_interval and _last_viewport:
        # Check if viewport has moved significantly
        dx = abs(viewport.left - _last_viewport.left)
        dy = abs(viewport.bottom - _last_viewport.bottom)
        if dx < TILE_SIZE and dy < TILE_SIZE:
            return False
    
    _last_update_time = current_time
    _last_viewport = viewport
    return True

def update_visible_tiles(viewport: 'Viewport') -> None:
    """Update which tiles are visible based on the current viewport."""
    global active_sprites, _visible_tiles, _last_camera_pos
    
    # Only update if necessary
    if not should_update_viewport(viewport):
        return
    
    # Update camera position
    current_camera_pos = (viewport.left, viewport.bottom)
    camera_moved = (_last_camera_pos[0] != current_camera_pos[0] or 
                   _last_camera_pos[1] != current_camera_pos[1])
    _last_camera_pos = current_camera_pos
    
    # Calculate visible tile range with padding
    min_x = int((viewport.left - TILE_SIZE * VIEWPORT_PADDING) // TILE_SIZE)
    max_x = int((viewport.right + TILE_SIZE * VIEWPORT_PADDING) // TILE_SIZE) + 1
    min_y = int((viewport.bottom - TILE_SIZE * VIEWPORT_PADDING) // TILE_SIZE)
    max_y = int((viewport.top + TILE_SIZE * VIEWPORT_PADDING) // TILE_SIZE) + 1
    
    # Only update if viewport has moved significantly or first run
    if not camera_moved and _visible_tiles:
        return
    
    # Clear previous visible tiles
    _visible_tiles.clear()
    
    # Add visible tiles to the active sprites
    if tile_sprites:
        # Pre-allocate list for visible sprites
        visible_sprites = []
        
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                try:
                    pos = (x, y)
                    sprite = tile_sprites.get(pos)
                    if sprite:
                        visible_sprites.append(sprite)
                        _visible_tiles.add(pos)
                except (KeyError, TypeError):
                    continue
        
        # Update sprite list in one go
        active_sprites.clear()
        active_sprites.extend(visible_sprites)
    
    # Always add player last (on top)
    if player_sprite:
        active_sprites.append(player_sprite)
    
    # Spatial hash is automatically updated when sprites are added/removed
    # No need to manually update it

def draw_map(window) -> None:
    """Update and draw the visible portion of the map."""
    
    # Only update viewport if window size changed or first run
    if not hasattr(draw_map, '_last_size') or draw_map._last_size != (window.width, window.height):
        draw_map._last_size = (window.width, window.height)
        viewport = Viewport.from_camera(
            (window.camera.position[0], window.camera.position[1]),
            window.width,
            window.height
        )
        update_visible_tiles(viewport)
    else:
        # Reuse existing viewport if only camera position changed
        viewport = Viewport.from_camera(
            (window.camera.position[0], window.camera.position[1]),
            window.width,
            window.height
        )
        update_visible_tiles(viewport)

def update_camera_position(camera_x: float, camera_y: float, player) -> None:
    """Update camera and sprite positions."""
    try:
        if hasattr(player, 'sprite') and player.sprite is not None:
            # Update player sprite position
            player.sprite.position = (player.x, player.y)
            
            # Update global player sprite reference
            global player_sprite
            player_sprite = player.sprite
    except Exception as e:
        print(f"Error updating camera position: {e}")

# Cache the text object for better performance
_debug_text = None

def draw() -> None:
    """Draw all active sprites."""
    global _debug_text
    
    # Draw all sprites in one batch
    if active_sprites:
        # Use draw_hit_boxes=False for better performance if hitboxes aren't needed
        active_sprites.draw(filter=None, pixelated=True)
    
    # Only update debug text periodically
    current_time = time.time()
    if not hasattr(draw, '_last_debug_update') or current_time - draw._last_debug_update > 0.5:
        draw._last_debug_update = current_time
        if not _debug_text:
            _debug_text = arcade.Text(
                f"Sprites: {len(active_sprites)}",
                10, 10,
                arcade.color.WHITE, 12
            )
        else:
            _debug_text.text = f"Sprites: {len(active_sprites)}"
    
    if _debug_text:
        _debug_text.draw()
def draw_player(player) -> None:
    """Initialize or update the player sprite."""
    global player_sprite
    
    try:
        if not hasattr(player, 'sprite') or player.sprite is None:
            tile_props = get_content('player')
            if not tile_props or 'texture' not in tile_props:
                print("Warning: Could not get player texture properties")
                return
                
            texture_name = tile_props["texture"]
            if texture_name not in loaded_textures:
                print(f"Warning: Player texture '{texture_name}' not loaded")
                return
                
            texture = loaded_textures[texture_name]
            player.sprite = arcade.Sprite(texture)
            player.sprite.scale = TILE_SIZE / max(texture.width, texture.height)
            player_sprite = player.sprite
        
        if hasattr(player, 'sprite') and player.sprite is not None:
            player.sprite.position = (player.x, player.y)
    except Exception as e:
        print(f"Error initializing/updating player sprite: {e}")

# Initialize the renderer
_initialized = False

def initialize_renderer() -> None:
    """Initialize the renderer. Must be called after content is loaded."""
    global _initialized
    if not _initialized:
        preload_textures()
        init_map()
        _initialized = True