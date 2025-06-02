import random
import yaml

def generate_large_map(width=100, height=100, output_file="assets/content/large_map.yml"):
    """
    Generate a large map with various terrain types.
    
    Args:
        width: Width of the map in tiles
        height: Height of the map in tiles
        output_file: Path to save the map file
    """
    # Define terrain types and their probability weights
    terrain_types = {
        'sand': 30,    # 30% chance
        'grass': 40,   # 40% chance
        'water': 20,   # 20% chance
        'dirt': 10     # 10% chance
    }
    
    # Create weighted choices list
    choices = []
    for terrain, weight in terrain_types.items():
        choices.extend([terrain] * weight)
    
    # Create map layout
    map_data = {
        'layout': {
            'name': f'Large Map {width}x{height}',
            'tiles': []
        }
    }
    
    # Generate map tiles
    for y in range(height):
        for x in range(width):
            # Add some variation to terrain
            if y < height // 3:  # More water at the bottom
                terrain = random.choices(['water', 'sand'], weights=[50, 50])[0]
            elif y > height * 2 // 3:  # More grass at the top
                terrain = random.choices(['grass', 'dirt'], weights=[70, 30])[0]
            else:  # Middle section
                terrain = random.choice(choices)
            
            # Create tile entry
            tile = {
                'rot': 0,
                'tile': terrain,
                'x': x,
                'y': y
            }
            map_data['layout']['tiles'].append(tile)
    
    # Add some variation by creating rivers and paths
    for _ in range(5):  # Create 5 rivers/paths
        start_x = random.randint(0, width-1)
        start_y = random.randint(0, height-1)
        length = random.randint(10, 20)
        direction = random.choice(['horizontal', 'vertical'])
        
        for i in range(length):
            if direction == 'horizontal':
                x = (start_x + i) % width
                y = start_y
            else:
                x = start_x
                y = (start_y + i) % height
            
            # Change the tile to water or sand
            for tile in map_data['layout']['tiles']:
                if tile['x'] == x and tile['y'] == y:
                    tile['tile'] = random.choice(['water', 'sand'])
                    break
    
    # Save to YAML file
    with open(output_file, 'w') as f:
        yaml.dump(map_data, f, default_flow_style=False)
    
    print(f"Generated map {width}x{height} saved to {output_file}")

if __name__ == "__main__":
    generate_large_map(100, 100, "assets/content/map.yml")
