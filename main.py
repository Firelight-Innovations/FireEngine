# Project start date: 19 November 2024
# IMPORTANT: Classes are loaded & instantiated based on the order of imports in this file!

# Importing depedencies 
import os

import arcade
import arcade.color
import arcade.color
import arcade.key

import arcade.key
import arcade.key

# Constants
SCREEN_TITLE = "FireEngine Kraken"

class GameLoop(arcade.Window):
    def __init__(self):
        super().__init__(render.SCREEN_WIDTH, render.SCREEN_HEIGHT, SCREEN_TITLE, resizable=True, vsync=True, update_rate=1/60) # type: ignore

        # clears game cache
        resource_loading.delete_all_files_in_directory(resource_loading.Cache)
        manager.Game.start()

    def on_update(self, delta_time):
        """Update Game state."""
        manager.Game.update(delta_time)
        super().on_update(delta_time)  # Call parent class update if needed

    def on_draw(self):
        """Render the screen."""
        arcade.start_render()
        # Clear the texture cache
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
        elif key == arcade.key.SPACE: # SPACE key for shooting
            manager.Game.shoot(True) 
        elif key == arcade.key.KEY_0: # Change the weapon
            manager.Game.change_weapon(0)
        elif key == arcade.key.KEY_1:
            manager.Game.change_weapon(1)
        elif key == arcade.key.KEY_2:
            manager.Game.change_weapon(2)
        elif key == arcade.key.KEY_3:
            manager.Game.change_weapon(3)
        elif key == arcade.key.KEY_4:
            manager.Game.change_weapon(4)
        elif key == arcade.key.KEY_5:
            manager.Game.change_weapon(5)
        elif key == arcade.key.KEY_6:
            manager.Game.change_weapon(6)
        elif key == arcade.key.KEY_7:
            manager.Game.change_weapon(7)
        elif key == arcade.key.KEY_8:
            manager.Game.change_weapon(8)
        elif key == arcade.key.KEY_9:
            manager.Game.change_weapon(9)

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
        elif key == arcade.key.SPACE: # SPACE key for shooting
            manager.Game.shoot(False) 

    def on_close(self):
        """Handle window close event."""
        import sys
        from FireEngine.audio import audio
        
        # Perform audio cleanup
        audio.audiomanager.cleanup()
        
        # Exit the program gracefully
        super().on_close()

#############################
#   Importing engine code   #
#############################

# Importing game manager
from FireEngine.core import manager

# Resouurce loading 
from FireEngine.core.resources import resource_loading
from FireEngine.core.resources import scene_loading
from FireEngine.core.resources import data_containers

# Gameplay logic
# Main function to start the Game

def main():
    """Main function to set up and run the Game."""
    game = GameLoop()
    arcade.run()

def signal_handler(self, sig, frame):
    """Handle termination signals."""
    import sys
    from FireEngine.audio import audio

    print(f"Received signal {sig}, shutting down...")
    audio.audiomanager.cleanup()
    sys.exit(0)  # Exit gracefully after cleanup

# Importing & initializing code in a particular order to get multithreading to work.
if __name__ == "__main__":
    from FireEngine.core import multiprocess

    # Initialize the Manager
    #man = multiprocess.createManager()

    #print(f'Multi: {man}')
    from FireEngine.core import render
    from FireEngine.objects import entity
    from FireEngine.objects import sprite
    from FireEngine.player import player
    from FireEngine.player import interact

    from FireEngine.audio import audio
    from FireEngine.ui import debug
    from FireEngine.ui import game_ui

    # Import all files dynamically from the game

    # Import all files dynamically from mods

    main()