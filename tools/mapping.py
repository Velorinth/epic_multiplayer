from dataclasses import dataclass
from typing import Set, Dict, Any
import yaml
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import sys

@dataclass(frozen=True)
class Tile:
    tile: str
    x: int
    y: int
    rot: int

class MapEditor:
    def __init__(self):
        self.tiles: Set[Tile] = set()
        self.tile_size = 32
        self.current_tile = None
        self.current_rotation = 0
        self.tile_images = {}
        self.load_tiles()

    def load_tiles(self):
        """Load tile definitions from YAML."""
        # Get the project root directory (one level up from tools)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tiles_path = os.path.join(project_root, 'assets/content/tiles.yml')
        
        print(f"Loading tiles from: {tiles_path}")  # Debug print
        with open(tiles_path, 'r') as f:
            tiles_data = yaml.safe_load(f)
        self.tile_types = tiles_data['tiles']

    def get_tile_image_path(self, tile_name):
        """Get the full path to a tile image."""
        # Get the project root directory (one level up from tools)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(project_root, f'assets/{self.tile_types[tile_name]["texture"]}')

    def add_tile(self, tile: str, x: int, y: int, rotation: int = 0):
        """Add a tile to the map."""
        if rotation not in [0, 90, 180, 270]:
            raise ValueError("Rotation must be 0, 90, 180, or 270 degrees")
        self.tiles.add(Tile(tile, x, y, rotation))

    def remove_tile(self, x: int, y: int):
        """Remove a tile from the map."""
        tiles_to_remove = {tile for tile in self.tiles if tile.x == x and tile.y == y}
        self.tiles -= tiles_to_remove

    def save_to_yaml(self, filename: str):
        """Save the map to a YAML file."""
        data = {
            'metadata': {'version': '1.0'},
            'layout': {
                'type': 'map',
                'tiles': list({
                    'tile': t.tile,
                    'x': t.x,
                    'y': t.y,
                    'rot': t.rot
                } for t in self.tiles)
            }
        }
        with open(filename, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

    def load_from_yaml(self, filename: str):
        """Load the map from a YAML file."""
        with open(filename, 'r') as f:
            data = yaml.safe_load(f)
            self.tiles = {
                Tile(
                    tile_dict['tile'],
                    tile_dict['x'],
                    tile_dict['y'],
                    tile_dict['rot']
                )
                for tile_dict in data['layout']['tiles']
            }

    def get_tile_at(self, x: int, y: int):
        """Get the tile at specific coordinates."""
        matching_tiles = [t for t in self.tiles if t.x == x and t.y == y]
        return matching_tiles[0] if matching_tiles else None

class MapEditorUI:
    def __init__(self):
        self.editor = MapEditor()
        self.window = tk.Tk()
        self.window.title("Map Editor")
        self.window.geometry("800x600")

        # Create main layout
        self.create_widgets()
        self.load_map()

    def create_widgets(self):
        # Create frames
        self.toolbar_frame = ttk.Frame(self.window)
        self.toolbar_frame.pack(side=tk.TOP, fill=tk.X)

        self.canvas_frame = ttk.Frame(self.window)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create toolbar buttons
        self.tile_buttons = {}
        for tile_name in self.editor.tile_types:
            btn = ttk.Button(
                self.toolbar_frame,
                text=tile_name,
                command=lambda t=tile_name: self.select_tile(t)
            )
            btn.pack(side=tk.LEFT)
            self.tile_buttons[tile_name] = btn

        # Create rotation buttons
        ttk.Button(self.toolbar_frame, text="↻", command=self.rotate_tile).pack(side=tk.LEFT)

        # Create canvas
        self.canvas = tk.Canvas(self.canvas_frame, bg="#333333")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.place_tile)
        self.canvas.bind("<Button-3>", self.remove_tile)

    def select_tile(self, tile_name):
        """Select a tile type."""
        self.editor.current_tile = tile_name
        self.editor.current_rotation = 0

    def rotate_tile(self):
        """Rotate the selected tile."""
        if self.editor.current_tile:
            self.editor.current_rotation = (self.editor.current_rotation + 90) % 360

    def place_tile(self, event):
        """Place a tile on the map."""
        if self.editor.current_tile:
            # Convert canvas coordinates to grid coordinates
            x = event.x // self.editor.tile_size
            y = event.y // self.editor.tile_size
            
            self.editor.add_tile(
                self.editor.current_tile,
                x,
                y,
                self.editor.current_rotation
            )
            self.draw_map()

    def remove_tile(self, event):
        """Remove a tile from the map."""
        # Convert canvas coordinates to grid coordinates
        x = event.x // self.editor.tile_size
        y = event.y // self.editor.tile_size
        
        self.editor.remove_tile(x, y)
        self.draw_map()

    def draw_map(self):
        """Draw the entire map."""
        self.canvas.delete("all")
        
        # Draw grid
        for x in range(0, self.canvas.winfo_width(), self.editor.tile_size):
            self.canvas.create_line(x, 0, x, self.canvas.winfo_height(), fill="#555555")
        for y in range(0, self.canvas.winfo_height(), self.editor.tile_size):
            self.canvas.create_line(0, y, self.canvas.winfo_width(), y, fill="#555555")

        # Draw tiles
        for tile in self.editor.tiles:
            # Load tile image if not already loaded
            if tile.tile not in self.editor.tile_images:
                img_path = self.editor.get_tile_image_path(tile.tile)
                print(f"Loading tile image: {img_path}")  # Debug print
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    img = img.resize((self.editor.tile_size, self.editor.tile_size))
                    self.editor.tile_images[tile.tile] = ImageTk.PhotoImage(img)
                else:
                    print(f"Warning: Tile image not found: {img_path}")  # Debug print

            if tile.tile in self.editor.tile_images:
                # Calculate screen coordinates
                screen_x = tile.x * self.editor.tile_size
                screen_y = tile.y * self.editor.tile_size

                # Create rotated image if needed
                if tile.rot != 0:
                    img = ImageTk.getimage(self.editor.tile_images[tile.tile])
                    img = img.rotate(tile.rot)
                    img = ImageTk.PhotoImage(img)
                else:
                    img = self.editor.tile_images[tile.tile]

                self.canvas.create_image(
                    screen_x, screen_y,
                    anchor=tk.NW,
                    image=img
                )
            else:
                # Draw a placeholder rectangle if image isn't loaded
                screen_x = tile.x * self.editor.tile_size
                screen_y = tile.y * self.editor.tile_size
                self.canvas.create_rectangle(
                    screen_x, screen_y,
                    screen_x + self.editor.tile_size,
                    screen_y + self.editor.tile_size,
                    fill="gray",
                    outline="black"
                )
                self.canvas.create_text(
                    screen_x + self.editor.tile_size//2,
                    screen_y + self.editor.tile_size//2,
                    text=tile.tile[0].upper(),  # Show first letter of tile type
                    fill="white"
                )

    def place_tile(self, event):
        """Place a tile on the map."""
        if self.editor.current_tile:
            # Convert canvas coordinates to grid coordinates
            x = event.x // self.editor.tile_size
            y = event.y // self.editor.tile_size
            
            # Add the tile
            self.editor.add_tile(
                self.editor.current_tile,
                x,
                y,
                self.editor.current_rotation
            )
            
            # Redraw the map
            self.draw_map()

    def load_map(self):
        """Load the map from file."""
        try:
            self.editor.load_from_yaml('assets/content/map.yml')
            self.draw_map()
        except FileNotFoundError:
            pass

    def save_map(self):
        """Save the map to file."""
        self.editor.save_to_yaml('assets/content/map.yml')

    def run(self):
        """Start the UI application."""
        self.window.mainloop()

if __name__ == "__main__":
    editor_ui = MapEditorUI()
    editor_ui.run()