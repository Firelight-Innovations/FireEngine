import configparser
import os
from pathlib import Path
import chardet

from FireEngine.core.decorators import singleton
from FireEngine.core.decorators import register

# System to descide which scene to load
# Either from main menu OR from within an exisiting scene

# Load SCENE.scene file
# Load SCENE.dat

# Load SCENE assets
# Get references to each texture in the SCENE

# Load SCENE objects
# Get references to each object in the SCENE

@singleton
@register
class scene_loader:
    def __init__(self):
        self.data_file = configparser.ConfigParser()

    def load_scene_data(self):
        """Loads all scenes into memory"""
        from FireEngine.core.resources import resource_loading
        from FireEngine.core.resources import data_containers
        # Load all .dat files
        # Find file with matching scene name
        # Load scene data

        scene_path = os.path.join(resource_loading.Objects, "Scenes")

        # Walk through the directory and its subdirectories
        for root, dirs, files in os.walk(scene_path):
            for file in files:
                if file.endswith('.dat'):  # Check if the file is a .dat file
                    data_path = os.path.join(root, file)

                    # Read the .ini file
                    self.data_file.read(data_path)

                    scene_file_path = Path(root) / (Path(file).stem + '.scene')
                    scene_name = self.data_file['Scene Info']['name']
                    scene_data = []

                    # Loading .scene
                    with open(file=scene_file_path, mode="r", encoding=self.detect_encoding(scene_file_path)) as scene:
                        for line in scene:
                            scene_data.append(line.replace("\n", ""))

                    # Load data from .scene & .dat into memory 
                    resource_loading.scenes[scene_name] = data_containers.scene(
                        scene_name=scene_name,
                        difficulty=self.data_file['Scene Info']['difficulty'],
                        scene_order=self.data_file['Scene Info']['scene_order'],
                        scene_data=scene_data
                    )

    def load_scene(self, scene_name:str):
        """Loads a scene from it's name"""
        from FireEngine.core.resources import resource_loading
        from FireEngine.core import scene
        from FireEngine.objects import entity
        from FireEngine.player import player

        # Loads scene data
        scene.scene_data = resource_loading.scenes[scene_name].scene_data

        # Loads player data
        player.Player.player_x = scene.get_player_spawn_x()
        player.Player.player_y = scene.get_player_spawn_y()

        # Loads texture data

        # Loads entity data
        guard = os.path.join(resource_loading.Assets, "Textures\\Sprites\\Guard\\guard_sheet.png")

        for y in range(len(scene.scene_data)):
            for x in range(len(scene.scene_data[0])):
                if scene.scene_data[y][x] == '$':
                    scene.scene_data[y] = scene.scene_data[y][:x] + ' ' + scene.scene_data[y][x+1:]
                    entity.entity(x, y, 0, 0.3, 0.3, guard, health=100) # Instantiates a new sprite object, inherits from the sprite class

        # Loads sprite data

    def detect_encoding(self, file_path):
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result['encoding']

    def on_start(self):
        self.load_scene_data()
        self.load_scene('Default Scene')

SceneLoader = scene_loader()