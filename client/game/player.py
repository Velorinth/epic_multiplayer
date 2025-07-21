import arcade
from render.renderer import active_sprites
from loader.content import yml_content, get_object_properties as get_content
class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.speed = 250  # pixels per second
        self.velocity_x = 0
        self.velocity_y = 0
        self.keys = {
            'W': False,
            'A': False,
            'S': False,
            'D': False
        }
        self._scheduled_interval = 0.05  # 50ms interval (20 times per second)
        self._time_since_last_call = 0.0  # Time accumulator
        self.collidable_x = []
        self.collidable_y = []
        self.collidable_objects = []  # Initialize empty list for collision detection

    def on_key_press_player(self, symbol, modifiers):
        """Handle key press events"""
        # Handle movement keys if not handled by inventory
        #print(f"Key pressed: {symbol}")
        if symbol == arcade.key.W:
            self.keys['W'] = True
        if symbol == arcade.key.A:
            self.keys['A'] = True
        if symbol == arcade.key.S:
            self.keys['S'] = True
        if symbol == arcade.key.D:
            self.keys['D'] = True
            
    def on_key_release_player(self, symbol, modifiers):
        """Handle key release events"""
        #print(f"Key released: {symbol}")
        if symbol == arcade.key.W:
            self.keys['W'] = False
        if symbol == arcade.key.A:
            self.keys['A'] = False
        if symbol == arcade.key.S:
            self.keys['S'] = False
        if symbol == arcade.key.D:
            self.keys['D'] = False

    def key_movement(self, dt):
        """Handle key press events"""
        vx = 0
        vy = 0
        
        if not any(self.keys.values()):
            return
            
        # Calculate movement based on keys pressed
        if self.keys['W']:
            vy += self.speed * dt
        if self.keys['A']:
            vx -= self.speed * dt
        if self.keys['S']:
            vy -= self.speed * dt
        if self.keys['D']:
            vx += self.speed * dt

        # Store original position
        original_x = self.x
        original_y = self.y
        
        # Player's collision box
        player_size = 1
        half_size = player_size / 2
        
        # Try X movement first
        if vx != 0:
            self.x += vx
            player_left = self.x - half_size
            player_right = self.x + half_size
            player_bottom = self.y - half_size
            player_top = self.y + half_size
            
            # Check for X-axis collisions
            x_collision = False
            for obj in self.collidable_objects:
                obj_left = obj['x']
                obj_right = obj['x'] + obj['width']
                obj_bottom = obj['y']
                obj_top = obj['y'] + obj['height']
                
                if (player_right > obj_left and 
                    player_left < obj_right and
                    player_top > obj_bottom and 
                    player_bottom < obj_top):
                    x_collision = True
                    break
            
            if x_collision:
                self.x = original_x
        
        # Store X position after X movement (which might have been reverted)
        x_after_move = self.x
        
        # Try Y movement
        if vy != 0:
            self.y += vy
            player_left = x_after_move - half_size
            player_right = x_after_move + half_size
            player_bottom = self.y - half_size
            player_top = self.y + half_size
            
            # Check for Y-axis collisions
            y_collision = False
            for obj in self.collidable_objects:
                obj_left = obj['x']
                obj_right = obj['x'] + obj['width']
                obj_bottom = obj['y']
                obj_top = obj['y'] + obj['height']
                
                if (player_right > obj_left and 
                    player_left < obj_right and
                    player_top > obj_bottom and 
                    player_bottom < obj_top):
                    y_collision = True
                    break
            
            if y_collision:
                self.y = original_y

        vx = 0
        vy = 0

    def get_position(self):
        return self.x, self.y
        
    def get_objects_in_radius(self, objects, radius_tiles=3, tile_size=48):
        """
        Get all objects within a specified radius (in tiles) of the player.
        
        Args:
            objects: List of game objects or dictionaries with x, y coordinates
            radius_tiles: Radius in tiles to check (default: 3)
            tile_size: Size of each tile in pixels (default: 48)
            
        Returns:
            List of objects that are within the specified radius of the player
        """
        radius_pixels = radius_tiles * tile_size
        player_x, player_y = self.x, self.y
        
        nearby_objects = []
        for obj in objects:
            # Get x, y from object (handles both object attributes and dictionary keys)
            try:
                if hasattr(obj, 'x') and hasattr(obj, 'y'):
                    # Object with x, y attributes
                    x, y = obj.x, obj.y
                elif isinstance(obj, dict) and 'x' in obj and 'y' in obj:
                    # Dictionary with x, y keys
                    x, y = obj['x'], obj['y']
                else:
                    continue  # Skip objects without coordinates
                
                # Calculate distance from player to object
                dx = x - player_x
                dy = y - player_y
                distance_squared = dx*dx + dy*dy
                
                # Check if within radius
                if distance_squared <= radius_pixels * radius_pixels:
                    nearby_objects.append(obj)
                    
            except (AttributeError, KeyError, TypeError) as e:
                print(f"Error processing object: {e}")
                continue
                
        return nearby_objects
        
    def on_update(self, delta_time: float):
        """
        Update the player. This is called every frame by the arcade window.
        
        Args:
            delta_time: Time since the last update in seconds
        """
        # Update the timer
        self._time_since_last_call += delta_time
        
        # Check if it's time to call the scheduled function
        if self._time_since_last_call >= self._scheduled_interval:
            self._time_since_last_call = 0.0
            self._on_scheduled_update()
    
    def _on_scheduled_update(self):
        """
        Override this method to add functionality that should run every 0.05 seconds.
        This is called approximately 20 times per second.
        """
        # Initialize last_collision_check_pos if it doesn't exist
        if not hasattr(self, 'last_collision_check_pos'):
            self.last_collision_check_pos = (self.x, self.y)
            
        if (abs(self.x - self.last_collision_check_pos[0]) > 24 or 
            abs(self.y - self.last_collision_check_pos[1]) > 24):
            
            self.collidable_objects = []  # Reset collidable objects list
            # Safely get tiles, handling case when yml_content is None
            all_tiles = []
            if yml_content is not None and hasattr(yml_content, 'get'):
                map_data = yml_content.get('map', {}) or {}
                layout = map_data.get('layout', {}) if isinstance(map_data, dict) else {}
                all_tiles = layout.get('tiles', []) if isinstance(layout, dict) else []
            
            # Only check tiles within 3 tiles radius of player
            player_tile_x = int(self.x // 48)
            player_tile_y = int(self.y // 48)
            radius_tiles = 3
            
            for tile in all_tiles:
                if not isinstance(tile, dict) or 'x' not in tile or 'y' not in tile:
                    continue
                    
                tile_x, tile_y = tile['x'], tile['y']
                # Skip tiles outside our radius
                if (abs(tile_x - player_tile_x) > radius_tiles or 
                    abs(tile_y - player_tile_y) > radius_tiles):
                    continue
                    
                if 'tile' in tile:  # Check if it's a valid tile object
                    tile_props = get_content(tile['tile'])
                    if tile_props and tile_props.get('wall', False):
                        # Store the collidable object with its position and size
                        self.collidable_objects.append({
                            'x': tile['x'] * 48,  # Convert grid to pixel coordinates
                            'y': tile['y'] * 48,
                            'width': 48,
                            'height': 48
                        })
            
            self.last_collision_check_pos = (self.x, self.y)
            print(f"Updated collidable objects: {len(self.collidable_objects)} walls in {radius_tiles}-tile radius")