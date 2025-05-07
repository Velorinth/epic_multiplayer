import pyglet
from pyglet.graphics import Batch
from pyglet.sprite import Sprite
from loader.content import yml_content

class MapRenderer:
    def __init__(self, window):
        self.window = window
        self.batch = Batch()
        self.tile_size = 32  
        self.map_data = None
        self.tiles = []
        
        # Load map data
        self.load_map()      
        
        # Load textures from all content files
        self.tile_textures = {}
        
        # Search through all loaded content for textures
        for content_type, content_data in yml_content.items():
            if isinstance(content_data, dict):
                # Check if this content type has texture definitions
                if 'tiles' in content_data:
                    tiles = content_data['tiles']
                    for tile_type, tile_data in tiles.items():
                        if 'texture' in tile_data:
                            texture_path = tile_data['texture']
                            try:
                                # Load texture from assets directory
                                texture = pyglet.image.load(f"assets/{texture_path}")
                                self.tile_textures[tile_type] = texture
                            except Exception as e:
                                print(f"Warning: Could not load texture for {tile_type}: {str(e)}")

    def load_map(self):
        """Load map data from content"""
        try:
            map_data = yml_content.get('map', {})
            if 'layout' in map_data:
                self.map_data = map_data['layout']
                self.create_map()
        except Exception as e:
            print(f"Error loading map: {str(e)}")

    def create_map(self):
        """Create the map using the loaded data"""
        if not self.map_data:
            return

        # Clear existing tiles
        self.tiles = []

        # Create sprites for each position in the map
        for y, row in enumerate(self.map_data['grid']):
            for x, tile_type in enumerate(row):
                if tile_type in self.tile_textures:
                    texture = self.tile_textures[tile_type]
                    tile = Sprite(
                        img=texture,
                        x=x * self.tile_size,
                        y=y * self.tile_size,
                        batch=self.batch
                    )
                    self.tiles.append(tile)

    def draw(self):
        """Draw the map"""
        self.batch.draw()

    def update(self, dt):
        """Update the map (currently empty)"""
        pass
