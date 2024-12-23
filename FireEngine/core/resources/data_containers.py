class scene:
    """Scene data container"""
    def __init__(self, 
                 name='', 
                 difficulty=0, 
                 order=0, 
                 description='', 
                 data=object):
        self.name = name
        self.difficulty = difficulty
        self.order = order
        self.data = data
        self.description = description

class texture:
    """Texture data container"""
    def __init__(self, 
                 name='', 
                 location='', 
                 icon='', 
                 hit_sfx='', 
                 walk_sfx=''):
        from FireEngine.core.resources import resource_loading
        import os
        import arcade

        self.name = name

        try:
            self.texture_path = os.path.join(resource_loading.Assets, location)
        except:
            self.texture_path = resource_loading.DefaultTexture

        self.icon = icon

        # Load sfx 
        try:
            self.hit_sfx = arcade.load_sound(os.path.join(resource_loading.Assets, hit_sfx))
        except:
            # Replace with a default sound
            self.hit_sfx = hit_sfx

        try:
            # Load folder of sounds!
            self.walk_sfx = arcade.load_sound(os.path.join(resource_loading.Assets, walk_sfx))
        except:
            # Replace with a default sound
            self.walk_sfx = walk_sfx

class door:
    """Door data container"""
    def __init__(self, 
                 name='', 
                 close_location = '',
                 open_location = '', 
                 wall_location = '',
                 close_icon = '', 
                 open_icon = '',
                 render_open = False,
                 hit_sfx = object):
        from FireEngine.core.resources import resource_loading
        import os
    
        self.name = name

        # Try to load textures
        try:
            self.close_texture = os.path.join(resource_loading.Assets, close_location)
        except:
             self.close_texture = resource_loading.DefaultTexture
        
        try:
            self.open_texture = os.path.join(resource_loading.Assets, open_location)
        except:
             self.open_texture = resource_loading.DefaultTexture

        try:
            self.wall_texture = os.path.join(resource_loading.Assets, wall_location)
        except:
             self.wall_texture = resource_loading.DefaultTexture

        self.close_icon = close_icon
        self.open_icon = open_icon
        self.render_open_door = render_open
        self.hit_sfx = hit_sfx

class entity:
    """Door data container"""
    def __init__(self, 
                 name='', 
                 _type='',
                 icon='',
                 data={}):
        from FireEngine.core.resources import resource_loading
        import os
    
        # Info
        self.name = name

        # Entity Info
        self._type = _type
        self.icon = icon

        self.hitbox_x = float(data['hitbox_x'])
        self.hitbox_y = float(data['hitbox_y'])

        if _type == 'enemy':
            # Enemy Info
            self.animation_sheet = os.path.join(resource_loading.Assets, data['animation_sheet'])
            self.speed = float(data['speed'])
            self.weapon = data['weapon']
            self.health = float(data['health'])
            self.armor = float(data['armor'])
            self.damage_low = float(data['damage_low'])
            self.damage_high = float(data['damage_high'])
            self.fire_range = float(data['fire_range'])
            self.hit_chance_close = float(data['hit_chance_close'])
            self.hit_chance_far = float(data['hit_chance_far'])
            self.fire_freq_low = float(data['fire_freq_low'])
            self.fire_freq_high = float(data['fire_freq_high'])

            # Enemy AI Info
            self.view_range = float(data['view_range'])
            self.ai_system = data['ai_system']
            self.patrol_wait = float(data['patrol_wait'])

            # Enemy Audio Info
            self.death_sfx = os.path.join(resource_loading.Assets, data['death_sfx'])
            self.gore_sfx = os.path.join(resource_loading.Assets, data['gore_sfx'])
            self.scream_sfx = os.path.join(resource_loading.Assets, data['scream_sfx'])
            self.pistol_sfx = os.path.join(resource_loading.Assets, data['pistol_sfx'])
            self.shotgun_sfx = os.path.join(resource_loading.Assets, data['shotgun_sfx'])
            self.rifle_sfx = os.path.join(resource_loading.Assets, data['rifle_sfx'])

        if _type == 'dropable':
            # Dropable Info
            self.asset_location = data['asset_location']
            self.health = float(data['health'])
            self.armor = float(data['armor'])
            self.pistol_ammo = int(data['pistol_ammo'])
            self.shotgun_ammo = int(data['shotgun_ammo'])
            self.rifle_ammo = int(data['rifle_ammo'])
            self.equip_vfx = data['equip_vfx']

            # Dropable Audio Info
            self.equip_sfx = data['equip_sfx']
            

# scene object data container
class objects:
    def __init__(self):
        pass