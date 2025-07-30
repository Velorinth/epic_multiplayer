import arcade
from entity.entity import Entity
from render.renderer import TILE_SIZE
from loader.content import get_object_properties as get_content
from networking.main import get_tile_map, entities

class Player:
    def __init__(self):
        self.entity = None
        # self.x and self.y are now read-only mirrors of the sprite's position
        self.x = 0
        self.y = 0
        self.speed = 250
        self.keys = {'W': False, 'A': False, 'S': False, 'D': False}
        self.wall_list = arcade.SpriteList()

    def get_position(self):
        return self.x, self.y

    def try_link_entity(self) -> bool:
        """Finds the player's entity once the renderer has created its sprite."""
        if self.entity: return True
        
        for entity in entities.values():
            if entity.proto == 'player' and entity.sprite:
                self.entity = entity
                print("✅ Player entity linked!")
                return True
        return False

    def build_static_wall_list(self):
        print("Player: Building static wall list...")
        self.wall_list = arcade.SpriteList()
        
        all_tiles = get_tile_map().get('layout', {}).get('tiles', [])
        for tile in all_tiles:
            tile_props = get_content(tile.get('tile'))
            if tile_props and tile_props.get('wall', False):
                wall = arcade.SpriteSolidColor(int(TILE_SIZE), int(TILE_SIZE), arcade.color.RED)
                wall.position = (tile['x'] * TILE_SIZE + TILE_SIZE / 2, tile['y'] * TILE_SIZE + TILE_SIZE / 2)
                self.wall_list.append(wall)

        if entities:
            for entity in entities.values():
                if entity.id == self.entity.id or not entity.sprite: continue
                entity_props = get_content(entity.proto) or {}
                if entity_props.get('wall', False):
                    self.wall_list.append(entity.sprite)
        
        print(f"Player: Wall list created with {len(self.wall_list)} objects.")

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
        if not self.try_link_entity(): return
        
        if not self.wall_list:
            self.build_static_wall_list()

        self.process_movement(delta_time)

        # After all physics, update the read-only coordinates
        self.x = self.entity.sprite.center_x
        self.y = self.entity.sprite.center_y
    def process_movement(self, delta_time: float):
        if not self.entity or not self.entity.sprite: return
        vx = 0; vy = 0 
        if self.keys['W']: vy += self.speed
        if self.keys['S']: vy -= self.speed
        if self.keys['A']: vx -= self.speed
        if self.keys['D']: vx += self.speed
        if vx != 0 and vy != 0:
            vx *= 0.7071; vy *= 0.7071
        
        # Move the sprite directly
        self.entity.sprite.center_x += vx * delta_time
        for wall in arcade.check_for_collision_with_list(self.entity.sprite, self.wall_list):
            if vx > 0: self.entity.sprite.right = wall.left
            elif vx < 0: self.entity.sprite.left = wall.right

        self.entity.sprite.center_y += vy * delta_time
        for wall in arcade.check_for_collision_with_list(self.entity.sprite, self.wall_list):
            if vy > 0: self.entity.sprite.top = wall.bottom
            elif vy < 0: self.entity.sprite.bottom = wall.top

        # Sync the entity's grid coordinates from the sprite's final position
        self.entity.x = self.entity.sprite.center_x / TILE_SIZE
        self.entity.y = self.entity.sprite.center_y / TILE_SIZE