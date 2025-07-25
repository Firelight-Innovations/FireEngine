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

        scene_path = os.path.join(resource_loading.OBJECTS, "Scenes")

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
                    resource_loading.scenes[scene_name] = data_containers.Scene(
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

        texture_path = os.path.join(resource_loading.OBJECTS, "Textures")

        for file in os.listdir(texture_path):
            if file.endswith('.dat'):  # Check if the file is a .dat file
                # Read the .dat file
                data_file = configparser.ConfigParser()
                data_file.read(os.path.join(texture_path, file))

                if data_file['Info']['type'] != 'texture':
                    continue

                texture_icon = data_file['Texture Info']['icon']

                # Load from .dat into memory 
                resource_loading.textures[texture_icon] = data_containers.Texture(
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

        texture_path = os.path.join(resource_loading.OBJECTS, "Doors")

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
                resource_loading.doors[name] = data_containers.Door(
                    name = name,
                    close_location = data_file['Texture Info']['close_location'],
                    open_location = data_file['Texture Info']['open_location'],
                    wall_location= data_file['Texture Info']['wall_location'],
                    close_icon = data_file['Texture Info']['close_icon'],
                    open_icon = data_file['Texture Info']['open_icon'],
                    render_open = str_to_bool[data_file['Texture Info']['render_open_door']],
                    hit_sfx = data_file['Audio Info']['hit_sfx'],
                )

    def load_entity_data(self):
        """Loads all entites into a list"""
        from FireEngine.core.resources import resource_loading
        from FireEngine.core.resources import data_containers

        texture_path = os.path.join(resource_loading.OBJECTS, "Entities")

        for file in os.listdir(texture_path):
            if file.endswith('.dat'):  # Check if the file is a .dat file
                # Read the .dat file       
                data_file = configparser.ConfigParser(strict=False)
                data_file.read(os.path.join(texture_path, file))

                if data_file['Info']['type'] != 'entity':
                    continue

                name = data_file['Info']['name']
                icon = data_file['Entity Info']['icon']

                data = {
                    #Entity Info
                    'hitbox_x': data_file['Entity Info']['hitbox_x'],
                    'hitbox_y': data_file['Entity Info']['hitbox_y'],

                    'animation': data_file['Entity Info']['animation'],
                    'speed': data_file['Entity Info']['speed'],
                    'weapon': data_file['Entity Info']['weapon'],
                    'health': data_file['Entity Info']['health'],
                    'armor': data_file['Entity Info']['armor'],
                    'damage_low': data_file['Entity Info']['damage_low'],
                    'damage_high': data_file['Entity Info']['damage_high'],
                    'fire_range': data_file['Entity Info']['fire_range'],
                    'hit_chance_close': data_file['Entity Info']['hit_chance_close'],
                    'hit_chance_far': data_file['Entity Info']['hit_chance_close'],
                    'fire_freq_low': data_file['Entity Info']['fire_freq_low'],
                    'fire_freq_high': data_file['Entity Info']['fire_freq_high'],
        
                    # Enemy AI Info
                    'view_range': data_file['AI Info']['view_range'],
                    'ai_system': data_file['AI Info']['ai_system'],
                    'patrol_wait': data_file['AI Info']['patrol_wait'],
        
                    # Enemy Audio Info
                    'death_sfx': data_file['Audio Info']['death_sfx'],
                    'gore_sfx': data_file['Audio Info']['gore_sfx'],
                    'scream_sfx': data_file['Audio Info']['scream_sfx'],
                    'pistol_sfx': data_file['Audio Info']['pistol_sfx'],
                    'shotgun_sfx': data_file['Audio Info']['shotgun_sfx'],
                    'rifle_sfx': data_file['Audio Info']['rifle_sfx']
                }

                # Load from .dat into memory 
                resource_loading.entities[name] = data_containers.Entity(
                    name = name,
                    icon = icon,
                    data = data
                )

    def load_sprite_data(self):
        """Loads all sprites into a list"""
        from FireEngine.core.resources import resource_loading
        from FireEngine.core.resources import data_containers

        texture_path = os.path.join(resource_loading.OBJECTS, "Sprites")

        for file in os.listdir(texture_path):
            if file.endswith('.dat'):  # Check if the file is a .dat file
                # Read the .dat file       
                data_file = configparser.ConfigParser()
                data_file.read(os.path.join(texture_path, file))

                str_to_bool = {
                    'True': True,
                    'true': True,
                    'False': False,
                    'false': False
                }

                if data_file['Info']['type'] != 'sprite':
                    continue

                name = data_file['Info']['name']
                icon = data_file['Sprite Info']['icon']
                data = {}

                data = {
                    # Sprite Info
                    'hitbox_x': data_file['Sprite Info']['hitbox_x'],
                    'hitbox_y': data_file['Sprite Info']['hitbox_y'],
                    'animation_sheet': data_file['Sprite Info']['animation_sheet'],
                    'transparent': str_to_bool[data_file['Sprite Info']['transparent']],
                    'postional': str_to_bool[data_file['Sprite Info']['postional']],

                    # Audio Info
                    'hit_sfx': data_file['Audio Info']['hit_sfx'],
                }  

                # Load from .dat into memory 
                resource_loading.sprites[name] = data_containers.Sprite(
                    name = name,
                    icon = icon,
                    data = data
                )

    def load_weapon_data(self):
        """Loads all weapon into a list"""
        from FireEngine.core.resources import resource_loading
        from FireEngine.core.resources import data_containers

        texture_path = os.path.join(resource_loading.OBJECTS, "Weapons")

        for file in os.listdir(texture_path):
            if file.endswith('.dat'):  # Check if the file is a .dat file
                # Read the .dat file       
                data_file = configparser.ConfigParser()
                data_file.read(os.path.join(texture_path, file))

                str_to_bool = {
                    'True': True,
                    'true': True,
                    'False': False,
                    'false': False
                }

                if data_file['Info']['type'] != 'weapon':
                    continue

                name = data_file['Info']['name']
                data = {}

                x, y = data_file['Weapon Info']['texture_size'].split(',')

                data = {
                    # Weapon info
                    'fire_animation': str(data_file['Weapon Info']['fire_animation']),
                    'reload_animation': str(data_file['Weapon Info']['reload_animation']),
                    'jam_animation': str(data_file['Weapon Info']['jam_animation']),
                    'texture_size_x': int(x),
                    'texture_size_y': int(y),
                    'texture_buffer': int(data_file['Weapon Info']['texture_buffer']),
                    'weapon_x': float(data_file['Weapon Info']['weapon_x']),
                    'weapon_y': float(data_file['Weapon Info']['weapon_y']),
                    'weapon_scale': float(data_file['Weapon Info']['weapon_scale']),
                    'damage_high': int(data_file['Weapon Info']['damage_high']),
                    'damage_low': int(data_file['Weapon Info']['damage_low']),
                    'range': float(data_file['Weapon Info']['range']),
                    'max_ammo': int(data_file['Weapon Info']['max_ammo']),
                    'start_ammo': int(data_file['Weapon Info']['start_ammo']),

                    'unlock_on_start': str_to_bool[data_file['Weapon Info']['unlock_on_start']],
                    'is_automatic': str_to_bool[data_file['Weapon Info']['is_automatic']],
                    'loose_on_death': str_to_bool[data_file['Weapon Info']['loose_on_death']],
                    'uses_ammo': str_to_bool[data_file['Weapon Info']['uses_ammo']],
                    'does_reload': str_to_bool[data_file['Weapon Info']['does_reload']],
                    'does_jam': str_to_bool[data_file['Weapon Info']['does_jam']],

                    'ammo_type': str(data_file['Weapon Info']['ammo_type']),
                    'weapon_id': int(data_file['Weapon Info']['weapon_id']),
                    'reload_time': float(data_file['Weapon Info']['reload_time']),
                    'fire_time': float(data_file['Weapon Info']['fire_time']),

                    # Audio Info
                    'loudness': float(data_file['Audio Info']['loudness']),
                    'fire_sfx': str(data_file['Audio Info']['fire_sfx']),
                    'reload_sfx': str(data_file['Audio Info']['reload_sfx']),
                    'jam_sfx': str(data_file['Audio Info']['jam_sfx']),
                }  

                # Load from .dat into memory 
                resource_loading.weapons[data['weapon_id']] = data_containers.Weapon(
                    name = name,
                    data = data
                )

    def load_dropables_data(self):
        """Loads all sprites into a list"""
        from FireEngine.core.resources import resource_loading
        from FireEngine.core.resources import data_containers

        texture_path = os.path.join(resource_loading.OBJECTS, "Dropables")

        for file in os.listdir(texture_path):
            if file.endswith('.dat'):  # Check if the file is a .dat file
                # Read the .dat file       
                data_file = configparser.ConfigParser()
                data_file.read(os.path.join(texture_path, file))

                if data_file['Info']['type'] != 'dropable':
                    continue

                name = data_file['Info']['name']
                icon = data_file['Dropable Info']['icon']
                data = {}

                data = {
                    'hitbox_x': float(data_file['Dropable Info']['hitbox_x']),
                    'hitbox_y': float(data_file['Dropable Info']['hitbox_y']),
                    'texture': str(data_file['Dropable Info']['texture']),

                    'health': int(data_file['Dropable Info']['health']),
                    'max_health': int(data_file['Dropable Info']['max_health']),
                    'armor': int(data_file['Dropable Info']['armor']),
                    'max_armor': int(data_file['Dropable Info']['max_armor']),
                    'stamina': float(data_file['Dropable Info']['stamina']),
                    'max_stamina': float(data_file['Dropable Info']['max_stamina']),

                    'score': int(data_file['Dropable Info']['score']),

                    'give_weapon_id': int(data_file['Dropable Info']['give_weapon_id']),

                    'pistol_ammo': int(data_file['Dropable Info']['pistol_ammo']),
                    'shotgun_ammo': int(data_file['Dropable Info']['shotgun_ammo']),
                    'rifle_ammo': int(data_file['Dropable Info']['rifle_ammo']),

                    'pickup_vfx': str(data_file['Dropable Info']['pickup_vfx']),

                    #my Audio Info
                    'pickup_sfx': str(data_file['Audio Info']['pickup_sfx'])
                }  

                # Load from .dat into memory 
                resource_loading.dropables[name] = data_containers.Droppable(
                    name = name,
                    icon = icon,
                    data = data
                )

    def load_scene(self, scene_name:str):
        """Loads a scene from it's name"""
        from FireEngine.core.resources import resource_loading
        from FireEngine.core import scene
        from FireEngine.objects import entity
        from FireEngine.objects import sprite
        from FireEngine.objects import dropable
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
        self.load_entity_data()

        # Instanitates entities into memory
        for enti in resource_loading.entities:
            for y in range(len(scene.scene_data)):
                for x in range(len(scene.scene_data[y])):
                    if scene.scene_data[y][x] == resource_loading.entities[enti].icon:
                        scene.scene_data[y] = scene.scene_data[y][:x] + ' ' + scene.scene_data[y][x+1:]
                        entity.Entity(x, y, 0, entity=resource_loading.entities[enti]) # Instantiates a new entity object, inherits from the entity class

        #########################
        #   Loads sprite data   #
        #########################
        self.load_sprite_data()

        # Instanitates sprites into memory
        for spri in resource_loading.sprites:
            for y in range(len(scene.scene_data)):
                for x in range(len(scene.scene_data[y])):
                    if scene.scene_data[y][x] == resource_loading.sprites[spri].icon:
                        scene.scene_data[y] = scene.scene_data[y][:x] + ' ' + scene.scene_data[y][x+1:]
                        sprite.sprite(x, y, 0, _sprite=resource_loading.sprites[spri]) # Instantiates a new sprite object, inherits from the sprite class

        #####################################
        #   Loads dimentional object data   #
        #####################################

        ############################
        #   Loads dropables data   #
        ############################
        self.load_dropables_data()

        # Instanitates dropables into memory
        for drop in resource_loading.dropables:
            for y in range(len(scene.scene_data)):
                for x in range(len(scene.scene_data[y])):
                    if scene.scene_data[y][x] == resource_loading.dropables[drop].icon:
                        scene.scene_data[y] = scene.scene_data[y][:x] + ' ' + scene.scene_data[y][x+1:]
                        dropable.dropable(x, y, 0, _dropable=resource_loading.dropables[drop]) # Instantiates a new sprite object, inherits from the sprite class

        ########################
        #   Loads audio data   #
        ########################

        #######################
        #   Loads note data   #
        #######################

        #########################
        #   Loads weapon data   #
        #########################
        self.load_weapon_data()

    def detect_encoding(self, file_path):
        from FireEngine.core.resources import resource_loading
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            resource_loading.EncodingType = result['encoding']
            return result['encoding']

    def on_start(self):
        from FireEngine.core.resources import resource_loading
        self.load_scene_data() 
        self.load_scene('Test Scene')

SceneLoader = scene_loader()