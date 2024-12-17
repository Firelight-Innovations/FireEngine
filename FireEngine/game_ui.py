import arcade
import os

from FireEngine.core.decorators import singleton

# Importing assets 
DIR = os.path.join(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)), "Assets")

@singleton
class game_ui():
    def __init__(self):
        # UI Texture Loading
        self.crosshair = os.path.join(DIR, "Textures\\UI\\crosshair.png")

    def on_render(self):
        import main

        self.priority = 3

        # Draws health
        arcade.draw_text(
            f'Health: {round(main.Player.health)}',
            20,
            20,
            arcade.color.BLACK,
            20
        )

        # Draws the crosshair
        self.draw_crosshair()

    def draw_crosshair(self):
        from FireEngine.core import render
        crosshair_tex = arcade.load_texture(self.crosshair)

        arcade.draw_texture_rectangle(
            center_x=render.SCREEN_WIDTH // 2,
            center_y=render.SCREEN_HEIGHT // 2,
            width=crosshair_tex.width // 2,
            height=crosshair_tex.height // 2,
            texture=crosshair_tex
        )