import arcade
import os

Assets = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "Game\\Assets")
Objects = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "Game\\Objects")
Code = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "Game\\Code")
Cache = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "Game\\Cache")

scenes = {}
scene_textures = {}
scene_objects = {}
scene_3d_objects = {}

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