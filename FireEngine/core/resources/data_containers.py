# scene data container
class scene:
    def __init__(self, scene_name='', difficulty=0, scene_order=0, scene_data=object):
        self.scene_name = scene_name
        self.difficulty = difficulty
        self.scene_order = scene_order
        self.scene_data = scene_data
        pass

# scene object data container
class objects:
    def __init__(self):
        pass