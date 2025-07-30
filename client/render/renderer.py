import arcade
import os
import time
from typing import Dict, List, Tuple, Set, Optional
from loader.content import get_object_properties as get_content
from dataclasses import dataclass
from networking.main import get_tile_map, entities

_debug_draw_hitboxes = False

# Constants
TILE_SIZE = 48
VIEWPORT_PADDING = 2  # Slightly increased padding to reduce updates when moving
TEXTURE_SCALE = TILE_SIZE / 64  # Assuming 32x32 textures by default

# Performance tracking
_last_update_time = 0
_update_interval = 0.1  # Update viewport every 100ms

# Game state
loaded_textures: Dict[str, arcade.Texture] = {}
active_sprites: arcade.SpriteList = arcade.SpriteList(use_spatial_hash=True)
tile_sprites: Dict[Tuple[int, int], arcade.Sprite] = {}
entity_sprites: Dict[str, arcade.Sprite] = {} # New: For storing entity sprites
player_sprite: Optional[arcade.Sprite] = None
unique_textures = set()
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
    unique_textures.add("ui/trans1.png")
    unique_textures.add("ui/trans1024.png")
    
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

    # Get all unique entity textures
    if entities:
        for entity in entities.values():
            try:
                entity_props = get_content(entity.proto)
                if entity_props and 'texture' in entity_props:
                    unique_textures.add(entity_props["texture"])
            except (KeyError, TypeError):
                continue

    # Get player texture (can be redundant if player is in entities, but safe)
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
        print(tile_map)
        raise RuntimeError("Map data not available for initialization")
    
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

def init_entities() -> None:
    """Initialize sprites for ALL entities, including the player."""
    global entity_sprites
    entity_sprites.clear()
    
    if not entities: return

    for entity_id, entity in entities.items():
        # Only process entities that should be drawn
        if entity.draw:
            try:
                props = get_content(entity.proto)
                if not props or 'texture' not in props: continue
                
                texture_name = props["texture"]
                if texture_name not in loaded_textures: continue
                
                texture = loaded_textures[texture_name]
                sprite = arcade.Sprite(texture, hit_box_algorithm="Detailed")

                if entity.proto == 'player':
                    sprite.width = TILE_SIZE - 4
                    sprite.height = TILE_SIZE - 4
                else:
                    sprite.scale = TILE_SIZE / max(texture.width, texture.height)

                sprite.position = ((entity.x * TILE_SIZE) + (TILE_SIZE / 2), (entity.y * TILE_SIZE) + (TILE_SIZE / 2))
                sprite.angle = entity.rot
                
                entity_sprites[entity_id] = sprite
                entity.sprite = sprite
            except (KeyError, TypeError) as e:
                print(f"Warning: Error initializing sprite for entity '{entity_id}': {e}")

def update_entity_sprites() -> None:
    """Update positions and rotations of all drawn entities."""
    if not entities:
        return
        
    for entity_id, entity in entities.items():
        # Only process entities that should be drawn
        if entity.proto != 'player' and entity.draw and entity_id in entity_sprites:
            sprite = entity_sprites[entity_id]
            sprite.position = ((entity.x * TILE_SIZE) + (TILE_SIZE / 2), (entity.y * TILE_SIZE) + (TILE_SIZE / 2))
            sprite.angle = entity.rot
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
    """Update which tiles and entities are visible based on the current viewport."""
    global active_sprites, _visible_tiles, _last_camera_pos
    
    update_entity_sprites()

    if not should_update_viewport(viewport):
        return
    
    current_camera_pos = (viewport.left, viewport.bottom)
    _last_camera_pos = current_camera_pos
    
    min_x_tile = int((viewport.left - TILE_SIZE * VIEWPORT_PADDING) // TILE_SIZE)
    max_x_tile = int((viewport.right + TILE_SIZE * VIEWPORT_PADDING) // TILE_SIZE) + 1
    min_y_tile = int((viewport.bottom - TILE_SIZE * VIEWPORT_PADDING) // TILE_SIZE)
    max_y_tile = int((viewport.top + TILE_SIZE * VIEWPORT_PADDING) // TILE_SIZE) + 1
    
    visible_sprites = []
    
    if tile_sprites:
        for y in range(min_y_tile, max_y_tile + 1):
            for x in range(min_x_tile, max_x_tile + 1):
                sprite = tile_sprites.get((x, y))
                if sprite:
                    visible_sprites.append(sprite)

    # Add visible entities to the list, checking the 'draw' flag
    # Note: This loop is changed to iterate over 'entities' to access the flag.
    if entities:
        min_x_px = viewport.left - TILE_SIZE
        max_x_px = viewport.right + TILE_SIZE
        min_y_px = viewport.bottom - TILE_SIZE
        max_y_px = viewport.top + TILE_SIZE
        
        for entity in entities.values():
            if entity.draw and entity.sprite:
                sprite = entity.sprite
                if (min_x_px < sprite.center_x < max_x_px and
                    min_y_px < sprite.center_y < max_y_px):
                    visible_sprites.append(sprite)
    
    active_sprites.clear()
    active_sprites.extend(visible_sprites)

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

def toggle_hitbox_drawing():
    """Flips the debug flag for drawing hitboxes."""
    global _debug_draw_hitboxes
    _debug_draw_hitboxes = not _debug_draw_hitboxes
    print(f"Hitbox drawing {'ENABLED' if _debug_draw_hitboxes else 'DISABLED'}")

def draw() -> None:
    """Draw all active sprites."""
    global _debug_text
    
    # Draw all sprites in one batch
    if active_sprites:
        active_sprites.draw(
            filter=None, 
            pixelated=True
        )
        
        # --- THIS IS THE FIX ---
        # If the debug flag is on, draw the hitboxes separately.
        if _debug_draw_hitboxes:
            active_sprites.draw_hit_boxes(color=arcade.color.BLUE, line_thickness=2)
    
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
            
            # --- THIS IS THE FIX ---
            # Use the "Detailed" algorithm to create a hitbox that fits the visible pixels, ignoring transparency.
            player.sprite = arcade.Sprite(texture, hit_box_algorithm="Detailed")
            
            player.sprite.scale = TILE_SIZE / max(texture.width, texture.height)
            player_sprite = player.sprite
        
        # This part remains the same
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
        init_entities() # Initialize entity sprites
        _initialized = True