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
        pass

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
                    data_file = configparser.ConfigParser()

                    # Read the .dat file
                    data_file.read(data_path)

                    if data_file['Info']['type'] != 'scene':
                        continue

                    scene_file_path = Path(root) / (Path(file).stem + '.scene')
                    scene_name = data_file['Info']['name']
                    scene_data = []

                    # Loading .scene
                    with open(file=scene_file_path, mode="r", encoding=self.detect_encoding(scene_file_path)) as scene:
                        for line in scene:
                            scene_data.append(line.replace("\n", ""))

                    # Load data from .scene & .dat into memory 
                    resource_loading.scenes[scene_name] = data_containers.scene(
                        name = scene_name,
                        difficulty = data_file['Scene Info']['difficulty'],
                        order = data_file['Scene Info']['scene_order'],
                        description = data_file['Scene Info']['description'],
                        data = scene_data
                    )

    def load_texture_data(self):
        """Loads all textures into texture list"""
        from FireEngine.core.resources import resource_loading
        from FireEngine.core.resources import data_containers

        texture_path = os.path.join(resource_loading.Objects, "Textures")

        for file in os.listdir(texture_path):
            if file.endswith('.dat'):  # Check if the file is a .dat file
                # Read the .dat file
                data_file = configparser.ConfigParser()
                data_file.read(os.path.join(texture_path, file))

                if data_file['Info']['type'] != 'texture':
                    continue

                texture_icon = data_file['Texture Info']['icon']

                # Load from .dat into memory 
                resource_loading.textures[texture_icon] = data_containers.texture(
                    name = data_file['Info']['name'],
                    location= data_file['Texture Info']['location'],
                    icon= texture_icon,
                    hit_sfx= data_file['Audio Info']['hit_sfx'],
                    walk_sfx= data_file['Audio Info']['walk_sfx']
                )

    def load_door_data(self):
        """Loads all doors into a list"""
        from FireEngine.core.resources import resource_loading
        from FireEngine.core.resources import data_containers

        texture_path = os.path.join(resource_loading.Objects, "Doors")

        for file in os.listdir(texture_path):
            if file.endswith('.dat'):  # Check if the file is a .dat file
                # Read the .dat file       
                data_file = configparser.ConfigParser()
                data_file.read(os.path.join(texture_path, file))

                if data_file['Info']['type'] != 'door':
                    continue

                name = data_file['Info']['name']

                str_to_bool = {
                    'True': True,
                    'true': True,
                    'False': False,
                    'false': False
                }

                # Load from .dat into memory 
                resource_loading.doors[name] = data_containers.door(
                    name = name,
                    close_location = data_file['Texture Info']['close_location'],
                    open_location = data_file['Texture Info']['open_location'],
                    wall_location= data_file['Texture Info']['wall_location'],
                    close_icon = data_file['Texture Info']['close_icon'],
                    open_icon = data_file['Texture Info']['open_icon'],
                    render_open = str_to_bool[data_file['Texture Info']['render_open_door']],
                    hit_sfx = data_file['Audio Info']['hit_sfx'],
                )

    def load_scene(self, scene_name:str):
        """Loads a scene from it's name"""
        from FireEngine.core.resources import resource_loading
        from FireEngine.core import scene
        from FireEngine.objects import entity
        from FireEngine.player import player

        ########################
        #   Loads scene data   #
        ########################
        try:
            scene.scene_data = resource_loading.scenes[scene_name].data
        except:
            scene.scene_data = resource_loading.scenes['Default Scene'].data

        #########################
        #   Loads player data   #
        #########################
        player.Player.player_x, player.Player.player_y = scene.get_player_spawn()

        ##########################
        #   Loads texture data   #
        ##########################
        self.load_texture_data()
        self.load_door_data()

        #########################
        #   Loads entity data   #
        #########################
        guard = os.path.join(resource_loading.Assets, "Textures\\Sprites\\Guard\\guard_sheet.png")

        # Instanitates entities into memory
        for y in range(len(scene.scene_data)):
            for x in range(len(scene.scene_data[0])):
                if scene.scene_data[y][x] == '$':
                    scene.scene_data[y] = scene.scene_data[y][:x] + ' ' + scene.scene_data[y][x+1:]
                    entity.entity(x, y, 0, 0.3, 0.3, guard, health=100) # Instantiates a new sprite object, inherits from the sprite class

        # Loads sprite data

    def detect_encoding(self, file_path):
        from FireEngine.core.resources import resource_loading
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            resource_loading.EncodingType = result['encoding']
            return result['encoding']

    def on_start(self):
        self.load_scene_data()
        self.load_scene('Default Scene')

SceneLoader = scene_loader()