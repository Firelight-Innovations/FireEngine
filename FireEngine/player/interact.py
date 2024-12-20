from FireEngine.core.decorators import singleton
from FireEngine.core.decorators import register

@singleton
@register
class interact:
    def __init__(self):
        pass

    def interact(self):
        """Check if the player is facing an interactive object and trigger a callback."""
        from FireEngine.core import scene
        from FireEngine.player import player
        from FireEngine.core.resources import resource_loading
        import math

        # Calculate the direction vector based on player's current angle
        direction_x = math.cos(player.Player.player_angle)
        direction_y = math.sin(player.Player.player_angle)

        # Calculate the tile in front of the player
        front_x = int(player.Player.player_x + direction_x)
        front_y = int(player.Player.player_y + direction_y)

        tile_data = scene.scene_data[front_y][front_x]

        # Check if the tile in front of the player is interactive (e.g., a door '░')
        for door in resource_loading.doors:
            if tile_data == resource_loading.doors[door].open_icon or tile_data == resource_loading.doors[door].close_icon:
                self.interact_door(front_x, front_y, door, tile_data) # Trigger callback to open door

    def interact_door(self, x, y, door, tile):
        """Open a door at position (x, y)."""
        from FireEngine.core import scene
        from FireEngine.core.resources import resource_loading
        
        if tile == resource_loading.doors[door].open_icon:
            # We need to close the door
            scene.scene_data[y] = scene.scene_data[y][:x] + resource_loading.doors[door].close_icon + scene.scene_data[y][x+1:]
        else: 
            # We need to open the door
            scene.scene_data[y] = scene.scene_data[y][:x] + resource_loading.doors[door].open_icon + scene.scene_data[y][x+1:]

    ###############
    #   Updates   #
    ###############

    def on_interact(self):
        self.interact()

Interact = interact()