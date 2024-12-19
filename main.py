# By submitting this assignment, I agree to the following:
#   "Aggies do not lie, cheat, or steal, or tolerate those who do."
#   "I have not given or received any unauthorized aid on this assignment."
#
# Names:        
#               Angel Vega
#               Braden Seaborn
#               Will Hassan
# Section:      532
# Assignment:   Lab 7 Activity 1
# Date:         19 November 2024

# Imports
import arcade
import arcade.color
import arcade.color
import arcade.key
import os

from FireEngine.core import manager
from FireEngine.core import render
from FireEngine.core.resources import resource_loading
from FireEngine.objects import entity
from FireEngine.objects import sprite
from FireEngine.player import player
from FireEngine.player import interact
from FireEngine.ui import debug
from FireEngine.ui import game_ui

# Constants
SCREEN_TITLE = "Minenstien"

class GameLoop(arcade.Window):
    def __init__(self):
        super().__init__(render.SCREEN_WIDTH, render.SCREEN_HEIGHT, SCREEN_TITLE, resizable=True, vsync=True) # type: ignore

        # clears game cache
        resource_loading.delete_all_files_in_directory(os.path.join(resource_loading.Assets, "Cache"))
        manager.Game.start()

    def on_update(self, delta_time):
        """Update Game state."""
        manager.Game.update(delta_time)
        super().on_update(delta_time)  # Call parent class update if needed

    def on_draw(self):
        """Render the screen."""
        arcade.start_render()
        manager.Game.render()

    def on_key_press(self, key, modifiers):
        """Handle key press events."""
        if key == arcade.key.W:
            manager.Game.move_up(True)
        elif key == arcade.key.S:
            manager.Game.move_down(True)
        elif key == arcade.key.A:
            manager.Game.move_left(True)
        elif key == arcade.key.D:
            manager.Game.move_right(True)
        elif key == arcade.key.LEFT:  # Turn camera left
            manager.Game.turn_left(True)
        elif key == arcade.key.RIGHT:  # Turn camera right
            manager.Game.turn_right(True)
        elif key == arcade.key.E:  # Interact with objects
            manager.Game.interact()  # Call interaction function
        elif key == arcade.key.SPACE:  # Example: SPACE key for shooting
            manager.Game.shoot()

    def on_key_release(self, key, modifiers):
        """Handle key release events."""
        if key == arcade.key.W:
            manager.Game.move_up(False)
        elif key == arcade.key.S:
            manager.Game.move_down(False)
        elif key == arcade.key.A:
            manager.Game.move_left(False)
        elif key == arcade.key.D:
            manager.Game.move_right(False)
        elif key == arcade.key.LEFT:  # Stop turning left
            manager.Game.turn_left(False)
        elif key == arcade.key.RIGHT:  # Stop turning right
            manager.Game.turn_right(False)

# Main function to start the Game
def main():
    """Main function to set up and run the Game."""
    game = GameLoop()
    arcade.run()

if __name__ == "__main__":
    main()