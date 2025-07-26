import arcade
from entity.entity import Entity
from render.renderer import entity_sprites, TILE_SIZE
from loader.content import get_object_properties as get_content
from networking.main import get_tile_map, entities

class Player:
    def __init__(self):
        self.entity = None
        self.x = 0
        self.y = 0
        self.speed = 250
        self.keys = {'W': False, 'A': False, 'S': False, 'D': False}
        
        # The wall list will be built once and stored
        self.wall_list = None

    def get_position(self):
        return self.x, self.y

    def try_link_entity(self) -> bool:
        """Attempts to find and link the player's entity."""
        if self.entity: return True
        
        for entity in entities.values():
            if entity.proto == 'player' and entity.sprite:
                self.entity = entity
                self.x = self.entity.x * TILE_SIZE
                self.y = self.entity.y * TILE_SIZE
                print("✅ Player entity linked successfully!")
                return True
        return False

    def build_static_wall_list(self):
        """Builds a static list of all wall sprites for efficient collision."""
        print("Building static wall list...")
        new_wall_list = arcade.SpriteList()
        
        # --- Add TILES with 'wall: true' ---
        all_tiles = get_tile_map().get('layout', {}).get('tiles', [])
        for tile in all_tiles:
            tile_props = get_content(tile.get('tile'))
            if tile_props and tile_props.get('wall', False):
                wall = arcade.SpriteSolidColor(int(TILE_SIZE), int(TILE_SIZE), arcade.color.RED)
                wall.position = (tile['x'] * TILE_SIZE + TILE_SIZE / 2, tile['y'] * TILE_SIZE + TILE_SIZE / 2)
                new_wall_list.append(wall)

        # --- Add ENTITIES with 'wall: true' ---
        if entities:
            for entity in entities.values():
                if entity.id == self.entity.id or not entity.sprite: continue
                
                entity_props = get_content(entity.proto) or {}
                if entity_props.get('wall', False):
                    new_wall_list.append(entity.sprite)
        
        self.wall_list = new_wall_list
        print(f"Wall list created with {len(self.wall_list)} objects.")

    def on_key_press_player(self, symbol, modifiers):
        if symbol == arcade.key.F7:
            from render.renderer import toggle_hitbox_drawing
            toggle_hitbox_drawing()
        
        if symbol == arcade.key.W: self.keys['W'] = True
        if symbol == arcade.key.A: self.keys['A'] = True
        if symbol == arcade.key.S: self.keys['S'] = True
        if symbol == arcade.key.D: self.keys['D'] = True

    def on_key_release_player(self, symbol, modifiers):
        if symbol == arcade.key.W: self.keys['W'] = False
        if symbol == arcade.key.A: self.keys['A'] = False
        if symbol == arcade.key.S: self.keys['S'] = False
        if symbol == arcade.key.D: self.keys['D'] = False
    
    def on_update(self, delta_time: float):
        """Main update loop."""
        if not self.try_link_entity():
            return
        
        # Build the wall list once after linking
        if self.wall_list is None:
            self.build_static_wall_list()

        # Process movement and collisions
        self.process_movement(delta_time)
        
    def process_movement(self, delta_time: float):
        """Calculates movement, handles collisions, and updates positions."""
        if not self.entity or not self.entity.sprite: return

        # --- Calculate Velocity ---
        vx = 0
        vy = 0
        if self.keys['W']: vy += self.speed
        if self.keys['S']: vy -= self.speed
        if self.keys['A']: vx -= self.speed
        if self.keys['D']: vx += self.speed

        if vx != 0 and vy != 0:
            vx *= 0.7071
            vy *= 0.7071
        
        # --- Apply movement and resolve collisions one axis at a time ---
        # Move X
        self.x += vx * delta_time
        self.entity.sprite.center_x = self.x

        collisions = arcade.check_for_collision_with_list(self.entity.sprite, self.wall_list)
        for wall in collisions:
            if vx > 0: self.entity.sprite.right = wall.left
            elif vx < 0: self.entity.sprite.left = wall.right
        self.x = self.entity.sprite.center_x # Re-sync after collision

        # Move Y
        self.y += vy * delta_time
        self.entity.sprite.center_y = self.y

        collisions = arcade.check_for_collision_with_list(self.entity.sprite, self.wall_list)
        for wall in collisions:
            if vy > 0: self.entity.sprite.top = wall.bottom
            elif vy < 0: self.entity.sprite.bottom = wall.top
        self.y = self.entity.sprite.center_y # Re-sync after collision

        # --- Sync final position with underlying entity data ---
        self.entity.x = self.x / TILE_SIZE
        self.entity.y = self.y / TILE_SIZE