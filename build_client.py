import PyInstaller.__main__
import os

# Get the absolute path to the assets directory
assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')

PyInstaller.__main__.run([
    '--name=epic_multiplayer',
    '--onefile',
    '--windowed',
    '--hidden-import=render.renderer',
    '--hidden-import=loader.content',
    '--hidden-import=arcade',
    '--hidden-import=arcade.resources',
    '--hidden-import=arcade.tilemap',
    '--add-data=assets/content;assets/content',
    '--add-data=assets/sound;assets/sound',
    '--add-data=assets/textures;assets/textures',
    'client/main.py'
])
