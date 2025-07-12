from typing import List, Tuple, Union, Optional
import arcade
import os
import random

# Compute the base directory to avoid repeated nested os.path operations.
BASE_DIR: str = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
)

# Define resource paths using os.path.join for platform independence.
ASSETS: str = os.path.join(BASE_DIR, "Game", "Assets")
OBJECTS: str = os.path.join(BASE_DIR, "Game", "Objects")
CODE: str = os.path.join(BASE_DIR, "Game", "Code")
CACHE: str = os.path.join(BASE_DIR, "Game", "Cache")
SHADERS: str = os.path.join(BASE_DIR, "FireEngine", "core", "rendering")

# Global encoding type (if needed)
EncodingType: Optional[str] = None

DEFAULT_TEXTURE: str = os.path.join(BASE_DIR, "FireEngine", "default", "default.png")

# Containers for various resource types
scenes: dict = {}
audio: dict = {}
textures: dict = {}
doors: dict = {}
entities: dict = {}
sprites: dict = {}
dropables: dict = {}
weapons: dict = {}
# Fixed typo: "dimensional" rather than "dimentional"
dimensional_objects: dict = {}

def load_animation(folder_path: str, return_paths: bool = False) -> Union[List[arcade.Texture], Tuple[List[arcade.Texture], List[str]]]:
    """
    Load all animation frames from the specified folder.

    This function reads all PNG files found in the provided folder,
    loads them as arcade textures, and returns the list of textures.
    Optionally, it also returns the list of corresponding file paths.

    Args:
        folder_path (str): The directory path containing animation frames.
        return_paths (bool): If True, return a tuple of (textures, paths);
                             otherwise, return only the list of textures.

    Returns:
        Union[List[arcade.Texture], Tuple[List[arcade.Texture], List[str]]]:
            - A list of arcade.Texture objects, or
            - A tuple (textures, file paths) if return_paths is True.
    """
    frames: List[arcade.Texture] = []
    paths: List[str] = []
    # Sorting ensures frames are loaded in the intended order.
    for file in sorted(os.listdir(folder_path)):
        if file.endswith(".png"):
            full_path: str = os.path.join(folder_path, file)
            frames.append(arcade.load_texture(full_path))
            paths.append(full_path)
    if return_paths:
        return frames, paths
    return frames

def load_sprite_sheet(path: str, texture_size_x: int = 64, texture_size_y: int = 64, texture_buffer: int = 1, return_paths: bool = False) -> Union[List[arcade.Texture], Tuple[List[arcade.Texture], List[str]]]:
    """
    Load a sprite sheet and slice it into individual textures.

    The function slices the image specified by 'path' into frames of dimensions
    texture_size_x by texture_size_y, using texture_buffer pixels between frames.
    It continues slicing horizontally until it encounters a completely transparent frame.
    Optionally, it returns the file paths where the sliced textures were saved in the cache folder.

    Args:
        path (str): The file path to the sprite sheet image.
        texture_size_x (int): The width of each sprite frame.
        texture_size_y (int): The height of each sprite frame.
        texture_buffer (int): The buffer (in pixels) between frames.
        return_paths (bool): If True, return a tuple (textures, paths); otherwise, just textures.

    Returns:
        Union[List[arcade.Texture], Tuple[List[arcade.Texture], List[str]]]:
            - A list of arcade.Texture objects, or
            - A tuple (list of textures, list of file paths) if return_paths is True.
    """
    y: int = 0
    x: int = 0
    loop: bool = True

    textures_list: List[arcade.Texture] = []
    paths_list: List[str] = []

    while loop:
        try:
            # Load a frame at the current x, y coordinates.
            texture = arcade.load_texture(
                path,
                x=x,
                y=y,
                width=texture_size_x,
                height=texture_size_y
            )

            # Move to the next frame horizontally.
            x += texture_size_x + texture_buffer

            # Stop loop if the texture is fully transparent.
            image = texture.image
            loop = not all(pixel == (0, 0, 0, 0) for pixel in image.getdata())

            if loop:
                # Define a file name and output folder in CACHE.
                output_folder: str = CACHE
                output_file: str = f"{x}{y}-{random.randint(0, 100000)}.png"

                # Ensure that the output folder exists.
                os.makedirs(output_folder, exist_ok=True)

                # Save the current frame image to the output path.
                output_path: str = os.path.join(output_folder, output_file)
                image.save(output_path)

                textures_list.append(texture)
                paths_list.append(output_path)
        except Exception:
            loop = False

    if return_paths:
        return textures_list, paths_list
    return textures_list

def load_folder_sounds(folder_path: str) -> List[arcade.Sound]:
    """
    Load all audio files from the specified folder.

    This function searches for files with extensions .wav or .mp3 within the given folder,
    loads each as an arcade sound, and returns a list of these sounds.

    Args:
        folder_path (str): The directory containing the audio files.

    Returns:
        List[arcade.Sound]: A list of arcade.Sound objects loaded from the folder.
    """
    folder_contents: List[arcade.Sound] = []
    for file in os.listdir(folder_path):
        if file.endswith(('.wav', '.mp3')):
            full_path: str = os.path.join(folder_path, file)
            folder_contents.append(arcade.load_sound(full_path))
    return folder_contents

def delete_all_files_in_directory(directory_path: str) -> None:
    """
    Delete all files in the specified directory.

    Iterates over each file in the directory and removes it if it is a file.
    If an exception occurs (e.g., due to permissions), the function will silently exit.

    Args:
        directory_path (str): The directory path from which to delete all files.

    Returns:
        None
    """
    try:
        for filename in os.listdir(directory_path):
            file_path: str = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
    except Exception as e:
        # Optionally log the error here; for now, we simply exit.
        return