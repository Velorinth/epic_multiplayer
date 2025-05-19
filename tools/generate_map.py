import yaml

def generate_map():
    # Initialize the map structure
    map_data = {
        'metadata': {'version': '1.0'},
        'layout': {
            'type': 'map',
            'tiles': []
        }
    }

    # Grid dimensions
    width = 30
    height = 15

    # Define the grid
    grid = [
        ['sand'] * width,  # Row 0
        ['sand', 'dirt', 'dirt', 'dirt', 'sand', 'sand', 'dirt', 'dirt', 'dirt', 'sand',
         'sand', 'dirt', 'dirt', 'dirt', 'sand', 'sand', 'dirt', 'dirt', 'dirt', 'sand',
         'sand', 'dirt', 'dirt', 'dirt', 'sand', 'sand', 'sand', 'sand', 'sand', 'sand'],
        ['sand', 'dirt', 'dirt', 'dirt', 'sand', 'sand', 'dirt', 'dirt', 'dirt', 'sand',
         'sand', 'dirt', 'dirt', 'dirt', 'sand', 'sand', 'dirt', 'dirt', 'dirt', 'sand',
         'sand', 'dirt', 'dirt', 'dirt', 'sand', 'sand', 'sand', 'sand', 'sand', 'sand'],
        ['sand', 'dirt', 'dirt', 'dirt', 'sand', 'sand', 'dirt', 'dirt', 'dirt', 'sand',
         'sand', 'dirt', 'dirt', 'dirt', 'sand', 'sand', 'dirt', 'dirt', 'dirt', 'sand',
         'sand', 'dirt', 'dirt', 'dirt', 'sand', 'sand', 'sand', 'sand', 'sand', 'sand'],
        ['sand'] * width,  # Row 4
        ['sand'] * width,  # Row 5
        ['grass'] * 20 + ['sand'] * 10,  # Row 6
        ['grass'] * 20 + ['sand', 'water', 'sand', 'water', 'sand', 'sand', 'water', 'sand', 'sand', 'sand'],  # Row 7
        ['grass'] * 20 + ['sand'] * 10,  # Row 8
        ['grass'] * 20 + ['sand', 'water', 'sand', 'water', 'sand', 'sand', 'sand', 'sand', 'sand', 'sand'],  # Row 9
        ['grass'] * 20 + ['sand'] * 10,  # Row 10
        ['grass'] * 20 + ['sand'] * 10,  # Row 11
        ['grass'] * 20 + ['sand'] * 10,  # Row 12
        ['sand', 'grass'] * 19 + ['sand'],  # Row 13
        ['dirt', 'water'] + ['grass'] * 28  # Row 14
    ]

    # Convert grid to tile format
    for y, row in enumerate(grid):
        for x, tile_type in enumerate(row):
            map_data['layout']['tiles'].append({
                'tile': tile_type,
                'x': x,
                'y': y,
                'rot': 100
            })

    # Save to YAML file
    with open('assets/content/map.yml', 'w') as f:
        yaml.dump(map_data, f, default_flow_style=False)

if __name__ == "__main__":
    generate_map()
