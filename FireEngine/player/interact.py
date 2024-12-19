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
        import math

        # Calculate the direction vector based on player's current angle
        direction_x = math.cos(player.Player.player_angle)
        direction_y = math.sin(player.Player.player_angle)

        # Calculate the tile in front of the player
        front_x = int(player.Player.player_x + direction_x)
        front_y = int(player.Player.player_y + direction_y)

        # Check if the tile in front of the player is interactive (e.g., a door '░')
        if scene.mapData[front_y][front_x] == '░' or scene.mapData[front_y][front_x] == '▓':  # Example: Door tile
            self.interact_door(front_x, front_y)  # Trigger callback to open door

    def interact_door(self, x, y):
        """Open a door at position (x, y)."""
        from FireEngine.core import scene
        
        if(scene.mapData[y][x] == '░'): # Open
            scene.mapData[y] = scene.mapData[y][:x] + '▓' + scene.mapData[y][x+1:]
        else:
            scene.mapData[y] = scene.mapData[y][:x] + '░' + scene.mapData[y][x+1:]

    ###############
    #   Updates   #
    ###############

    def on_interact(self):
        self.interact()

Interact = interact()
print(Interact)