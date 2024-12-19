import arcade
import os
from FireEngine.core.decorators import singleton

Assets = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "Assets")

# Resource loading
def load_animation(folder_path, return_paths=False):
    """Load all animation frames from the specified folder."""
    frames = []
    paths = []
    for file in sorted(os.listdir(folder_path)):  # Sort ensures frames are in order
        if file.endswith(".png"):  # Only load PNG files
            full_path = os.path.join(folder_path, file)
            frames.append(arcade.load_texture(full_path))
            paths.append(full_path)
    if return_paths:
        return frames, paths
    else:
        return frames
    
def load_folder_sounds(folder_path):
    """Load all gore/scream sounds from the specified folder."""
    folder_contents = []
    for file in os.listdir(folder_path):
        if file.endswith(('.wav', '.mp3')):  # Filter for valid audio files
            full_path = os.path.join(folder_path, file)
            folder_contents.append(arcade.load_sound(full_path))
    return folder_contents

def delete_all_files_in_directory(directory_path):
    try:
        # List all files in the directory
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            # Check if it's a file before deleting
            if os.path.isfile(file_path):
                os.remove(file_path)
    except Exception as e:
        return

# Doesn't have register tag because it will run before the sprite texture loading otherwise
@singleton
class resource_loading:
    def __init__(self):
        pass

    ########################
    #   Update functions   #
    ########################

    def on_start(self):
        import main
        # Clear out texture Cache
        delete_all_files_in_directory(os.path.join(Assets, "Cache"))