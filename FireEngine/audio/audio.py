from FireEngine.core.decorators import singleton
from FireEngine.core.decorators import register

# Old music code
# https://discord.com/channels/@me/625148109747650565/1322081064755396609

@singleton
@register
class music():
    def __init__(self):
        import random
        import os
        from FireEngine.core.resources import resource_loading

        # Audio Loading
        self.songs_folder_path = os.path.join(resource_loading.Assets, "Audio\Music")
        self.songs = self.get_music_files()
        random.shuffle(self.songs)  # Shuffle the song list randomly
        self.current_song_index = 0
        self.current_player = None

    def play_next_song(self):
        """Play the next song in the shuffled list."""
        import random
        import arcade

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
        import os

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

###############################################
# Spatial Audio 
###############################################

# Try to get spaital audio system working later
@singleton
@register
class AudioManager:
    def __init__(self):
        from FireEngine.player import player        
        import openal
        import math
        import time

        openal.oalInit()
        openal.alDistanceModel(openal.AL_LINEAR_DISTANCE_CLAMPED)
        self.listener = openal.oalGetListener()
        self.listener.position = (player.Player.player_x, 0, player.Player.player_y)
        self.listener.velocity = (0, 0, 0)
        self.listener.orientation = (math.cos(player.Player.player_angle), 0, -math.sin(player.Player.player_angle), 0, 1, 0)
        self.audio_sources = [] # Keep track of all audio sources

        self.audio_sources.append(AudioSource("C:\\Users\\bjsea\\Documents\\Projects\\FireEngine\\Game\\Assets\\Audio\\Music\\doom.wav", 0, 0))

    def on_update(self, delta_time):
        from FireEngine.player import player
        import math

        #self.listener.position = (player.Player.player_x, player.Player.player_y, 0)
        #self.listener.velocity = (0, 0, 0)
        #self.listener.orientation = (math.cos(player.Player.player_angle), 0, -math.sin(player.Player.player_angle), 0, 1, 0)

    def cleanup(self):
        """Release OpenAL resources and stop all sounds."""
        import openal

        # Stop all active audio sources
        for source in self.audio_sources:
            source.stop()  # Signal each thread to stop
        
        # Wait for all threads to finish
        for source in self.audio_sources:
            source.thread.join()  # Ensure threads have exited
        
        # Release OpenAL resources
        openal.oalQuit()

class AudioSource:
    def __init__(self, file_path, x, y):
        import threading
        
        self.stop_event = threading.Event()
        self.lock = threading.Lock()

        if self.is_mono(file_path):
            self.thread = threading.Thread(target=self.play_audio, args=(file_path, x, y,))
            self.thread.start()

    def is_mono(self, file_path):
        """Check if the audio file is mono."""
        from pydub import AudioSegment

        audio = AudioSegment.from_file(file_path)
        return audio.channels == 1

    def convert_to_mono(self, file_path):
        """Convert a stereo audio file to mono."""
        from pydub import AudioSegment
        from FireEngine.core.resources import resource_loading
        import os
        from pathlib import Path
        
        audio = AudioSegment.from_file(file_path)
        if audio.channels > 1:
            print(f"Converting {file_path} to mono...")
            mono_audio = audio.set_channels(1)  # Convert to mono
            mono_audio.export(os.path.join(resource_loading.Cache, f"{Path(file_path).stem}_mono"), format="wav")  # Save as WAV
            return resource_loading.Cache
        return file_path  # Return original path if already mono

    def stop(self):
        self.stop_event.set()

    def play_audio(self, file_path, x, y):
        import openal
        import time

        with self.lock:
            # Load and play the audio file
            audio = openal.oalOpen(file_path)
            audio.position = (x, 0, y)
            audio.max_distance = 3
            audio.gain = 1.0
            audio.velocity = (0, 0, 0)
            audio.reference_distance = 0.5
            audio.max_distance = 10

            audio.play()
            
            # Wait until playback finishes or stop signal is set
            while audio.get_state() == openal.AL_PLAYING and not self.stop_event.is_set():
                time.sleep(0.1)
            
            # Stop playback if still playing
            if audio.get_state() == openal.AL_PLAYING:
                audio.stop()

#audiomanager = AudioManager()
#Music = music()