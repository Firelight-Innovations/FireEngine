import arcade
import os
from FireEngine.core.resources import data_containers

Assets = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "Game\\Assets")
Objects = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "Game\\Objects")
Code = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "Game\\Code")
Cache = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "Game\\Cache")
Shaders = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "FireEngine\\core\\rendering")

EncodingType = None

DefaultTexture = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "FireEngine\\default\\default.png")

scenes = {}
audio = {}
textures = {}
doors = {}
entities = {}
sprites = {}
dropables = {}
weapons = {}
dimentional_objects = {}

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
    
def load_sprite_sheet(path, texture_size_x=64, texture_size_y=64, texture_buffer=1, return_paths=False):
    import random
    y = 0
    x = 0
    loop = True

    paths = []
    textures = []

    while loop:
        try:
            texture = arcade.load_texture(
                path,
                x=x,
                y=y,
                width=texture_size_x,
                height=texture_size_y
            )

            x += texture_size_x + texture_buffer

            # Check if all pixels are fully transparent
            image = texture.image
            loop = not all(pixel == (0, 0, 0, 0) for pixel in image.getdata())

            if loop:
                output_folder = os.path.join(Cache)
                output_file = f"{x}{y}-{random.randint(0, 100000)}.png"

                # Ensure the folder exists
                os.makedirs(output_folder, exist_ok=True)
                            
                # Save the image to the specified folder
                output_path = os.path.join(output_folder, output_file)
                image.save(output_path)

                textures.append(texture)
                paths.append(output_path)
        except:
            loop = False

    if return_paths:
        return textures, paths
    else:
        return textures

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