# Project start date: 19 November 2024
# IMPORTANT: Classes are loaded & instantiated based on the order of imports in this file!

# Importing dependencies 
import arcade
import arcade.color
import arcade.key

# Constants
SCREEN_TITLE: str = "FireEngine Kraken"

class GameLoop(arcade.Window):
    """
    The main game loop class that handles game updates and rendering.
    """
    
    def __init__(self) -> None:
        """
        Initializes the game window and sets up the game environment.
        
        :return: None
        """
        super().__init__(1440, 810, SCREEN_TITLE, resizable=True, vsync=True, update_rate=1/60) # type: ignore
        
        # Clears game cache
        resource_loading.delete_all_files_in_directory(resource_loading.CACHE)
        manager.Game.start()
        music = audio.music() # Initializes & registers music object

    def on_update(self, delta_time: float) -> None:
        """
        Updates the game state based on the delta time.
        
        :param delta_time: Time elapsed since the last update.
        :return: None
        """
        manager.Game.update(delta_time)
        super().on_update(delta_time)  # Call parent class update if needed

    def on_draw(self) -> None:
        """
        Renders the game screen.
        
        :return: None
        """
        arcade.start_render()
        # Clear the texture cache
        manager.Game.render()

    def on_key_press(self, key: int, modifiers: int) -> None:
        """
        Handles key press events.
        
        :param key: The key that was pressed.
        :param modifiers: Any modifier keys being held.
        :return: None
        """
        if key == arcade.key.W:
            # Move up
            manager.Game.move_up(True)
        elif key == arcade.key.S:
            # Move down
            manager.Game.move_down(True)
        elif key == arcade.key.A:
            # Move left
            manager.Game.move_left(True)
        elif key == arcade.key.D:
            # Move right
            manager.Game.move_right(True)
        elif key == arcade.key.LEFT:  # Turn camera left
            manager.Game.turn_left(True)
        elif key == arcade.key.RIGHT:  # Turn camera right
            manager.Game.turn_right(True)
        elif key == arcade.key.E:  # Interact with objects
            # Call interaction function
            manager.Game.interact() 
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

    def on_key_release(self, key: int, modifiers: int) -> None:
        """
        Handles key release events.
        
        :param key: The key that was released.
        :param modifiers: Any modifier keys being held.
        :return: None
        """
        if key == arcade.key.W:
            # Stop moving up
            manager.Game.move_up(False)
        elif key == arcade.key.S:
            # Stop moving down
            manager.Game.move_down(False)
        elif key == arcade.key.A:
            # Stop moving left
            manager.Game.move_left(False)
        elif key == arcade.key.D: 
            # Stop moving right
            manager.Game.move_right(False)
        elif key == arcade.key.LEFT:  # Stop turning left
            manager.Game.turn_left(False)
        elif key == arcade.key.RIGHT:  # Stop turning right
            manager.Game.turn_right(False)
        elif key == arcade.key.SPACE: # SPACE key for shooting
            manager.Game.shoot(False) 

    def on_close(self) -> None:
        """
        Handles the window close event.
        
        :return: None
        """
        import sys
        from FireEngine.audio import audio
        
        '''
        # Perform audio cleanup
        try:
            audio.audiomanager.cleanup()
        finally:
            pass
        '''
        
        # Exit the program gracefully
        super().on_close()

#############################
#   Importing engine code   #
#############################

# Importing game manager
from FireEngine.core import manager

# Resource loading 
from FireEngine.core.resources import resource_loading
from FireEngine.core.resources import scene_loading
from FireEngine.core.resources import data_containers

# Gameplay logic
# Main function to start the Game

def main() -> None:
    """
    Main function to set up and run the Game.
    
    :return: None
    """
    global game
    manager.game_loop = GameLoop()
    arcade.run()

def signal_handler(self, sig: int, frame: object) -> None:
    """
    Handles termination signals.
    
    :param sig: The signal received.
    :param frame: The current stack frame.
    :return: None
    """
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
    from FireEngine.core.rendering import render
    from FireEngine.objects import entity
    from FireEngine.objects import sprite
    from FireEngine.player import player
    from FireEngine.player import interact

    from FireEngine.audio import audio
    from FireEngine.ui import debug
    from FireEngine.ui import game_ui

    # Import all files dynamically from the game
    #from Game.code import death

    # Import all files dynamically from mods

    main()