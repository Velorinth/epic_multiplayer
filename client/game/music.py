import arcade
from pathlib import Path
from loader.content import get_object_properties as get_content

class MusicPlayer:
    def __init__(self):
        self.current_song = None
        self.player = None
        self.is_playing = False
        self.volume = 0.5  # Default volume (0.0 to 1.0)
        self.looping = True  # Default to looping
        
    def load_song(self):
        """Load a music file"""
        # Get the full path to the music file
        music_path = Path(__file__).parent.parent.parent / "assets" / get_content("background_music_1")['file']
        print(f"Loading music from: {music_path}")
        
        try:
            self.current_song = arcade.load_sound(str(music_path))
            print(f"Loaded sound: {self.current_song}")
            self.is_playing = False  # Reset playing state
        except Exception as e:
            print(f"Error loading music: {e}")
            self.current_song = None
            self.is_playing = False

    def play(self):
        """Start playing the current song"""
        if self.current_song and not self.is_playing:
            print(f"Playing music with volume: {self.volume}")
            self.player = arcade.play_sound(self.current_song, volume=self.volume, loop=self.looping)
            self.is_playing = True

    def toggle_play_pause(self):
        """Toggle between play and pause"""
        if self.player:
            if self.is_playing:
                arcade.stop_sound(self.player)
                self.is_playing = False
            else:
                self.player = arcade.play_sound(self.current_song, volume=self.volume, looping=self.looping)
                self.is_playing = True

    def set_volume(self, volume: float):
        """Set the volume (0.0 to 1.0)"""
        if 0.0 <= volume <= 1.0:
            self.volume = volume
            if self.player:
                arcade.set_volume(self.player, self.volume)

    def stop(self):
        """Stop playing the music"""
        if self.player:
            arcade.stop_sound(self.player)
            self.player = None
            self.is_playing = False