import arcade
import random
import os

from FireEngine.core.decorators import singleton
from FireEngine.core.decorators import register
from FireEngine.core.resources import resource_loading

@singleton
@register
class music():
    def __init__(self):

        # Audio Loading
        self.songs_folder_path = os.path.join(resource_loading.Assets, "Audio\\Music")
        self.songs = self.get_music_files()
        random.shuffle(self.songs)  # Shuffle the song list randomly
        self.current_song_index = 0
        self.current_player = None

    def play_next_song(self):
        """Play the next song in the shuffled list."""
        if self.current_player is None or not self.current_player.playing:
            if self.current_song_index < len(self.songs):
                song_path = self.songs[self.current_song_index]
                sound = arcade.load_sound(song_path, True)
                self.current_player = arcade.play_sound(sound, volume=0.2) # type: ignore
                self.current_song_index += 1
            else:
                self.songs = self.get_music_files()
                random.shuffle(self.songs)  # Shuffle the song list randomly
                self.current_song_index = 0
                self.current_player = None

    def get_music_files(self):
        """Get all music files from the specified folder."""
        music_files = []
        for file in os.listdir(self.songs_folder_path):
            if file.endswith(('.mp3', '.wav')):  # Filter by audio file types
                music_files.append(os.path.join(self.songs_folder_path, file))
        return music_files

    ###############
    #   Updates   #
    ###############

    def on_update(self, delta_time):
        self.play_next_song()

Music = music()