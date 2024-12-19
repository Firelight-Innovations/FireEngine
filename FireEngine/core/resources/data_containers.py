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
        pass

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
            self.texture = os.path.join(resource_loading.Assets, location) #arcade.load_texture(os.path.join(resource_loading.Assets, location))
        except:
            self.texture = resource_loading.DefaultTexture #arcade.load_texture(resource_loading.DefaultTexture)

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
                 open_icon = '', 
                 close_icon = '',
                 hit_sfx = object,
                 walk_sfx = object):
        from FireEngine.core.resources import resource_loading
        import os
        import arcade
    
        self.name = name

        # Try to load textures
        try:
            self.close_texture = arcade.load_texture(os.path.join(resource_loading.Assets, close_location))
        except:
             self.close_texture_texture = arcade.load_texture(resource_loading.DefaultTexture)
        
        try:
            self.open_texture = arcade.load_texture(os.path.join(resource_loading.Assets, open_location))
        except:
             self.open_texture = arcade.load_texture(resource_loading.DefaultTexture)

        try:
            self.wall_texture = arcade.load_texture(os.path.join(resource_loading.Assets, wall_location)) 
        except:
             self.wall_texture_texture = arcade.load_texture(resource_loading.DefaultTexture)

        self.open_icon = open_icon
        self.close_icon = close_icon
        self.hit_sfx = hit_sfx
        self.walk_sfx = walk_sfx
        pass

# scene object data container
class objects:
    def __init__(self):
        pass