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

from FireEngine.core import scene
from FireEngine.core import manager
from FireEngine.core import player
from FireEngine.core import render
from FireEngine.core.resources import resource_loading as res_load

from FireEngine.objects import sprite
from FireEngine.ui import debug
from FireEngine.ui import game_ui
from FireEngine.audio import audio
from FireEngine.player import interact
from FireEngine.firemods import mods

# Constants
SCREEN_TITLE = "Minenstien"

TILE_SIZE = 20  # Size of each tile on the map

# Get the directory of the current script
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Assets")

# Creates new Game manager object, register update and render functions to it so they are ran.
Game = manager.game_manager()
Resource = res_load.resource_loading()
SpriteInit = sprite.sprite_init()
Player = player.player()
Render = render.render(Player)
Music = audio.music()
Debug = debug.debug()
GameUI = game_ui.game_ui()
Interact = interact.interact()

class GameLoop(arcade.Window):
    def __init__(self):
        super().__init__(render.SCREEN_WIDTH, render.SCREEN_HEIGHT, SCREEN_TITLE, resizable=True, vsync=True) # type: ignore

        # Inits singleton classes and registers it with the Game manager
        Game.register(Resource)
        Game.register(SpriteInit)
        Game.start()

    def on_update(self, delta_time):
        """Update Game state."""
        Game.update(delta_time)
        super().on_update(delta_time)  # Call parent class update if needed

    def on_draw(self):
        """Render the screen."""
        arcade.start_render()
        Game.render()

    def on_key_press(self, key, modifiers):
        """Handle key press events."""
        if key == arcade.key.W:
            self.move_up = True
            Game.move_up(True)
        elif key == arcade.key.S:
            self.move_down = True
            Game.move_down(True)
        elif key == arcade.key.A:
            self.move_left = True
            Game.move_left(True)
        elif key == arcade.key.D:
            self.move_right = True
            Game.move_right(True)
        elif key == arcade.key.LEFT:  # Turn camera left
            self.turn_left = True
            Game.turn_left(True)
        elif key == arcade.key.RIGHT:  # Turn camera right
            self.turn_right = True
            Game.turn_right(True)
        elif key == arcade.key.E:  # Interact with objects
            Game.interact()  # Call interaction function
        elif key == arcade.key.SPACE:  # Example: SPACE key for shooting
            Game.shoot()

    def on_key_release(self, key, modifiers):
        """Handle key release events."""
        if key == arcade.key.W:
            self.move_up = False
            Game.move_up(False)
        elif key == arcade.key.S:
            self.move_down = False
            Game.move_down(False)
        elif key == arcade.key.A:
            self.move_left = False
            Game.move_left(False)
        elif key == arcade.key.D:
            self.move_right = False
            Game.move_right(False)
        elif key == arcade.key.LEFT:  # Stop turning left
            self.turn_left = False
            Game.turn_left(False)
        elif key == arcade.key.RIGHT:  # Stop turning right
            self.turn_right = False
            Game.turn_right(False)

# Main function to start the Game
def main():
    """Main function to set up and run the Game."""
    game = GameLoop()
    arcade.run()

if __name__ == "__main__":
    main()