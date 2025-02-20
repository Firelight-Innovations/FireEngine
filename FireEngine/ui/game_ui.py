import arcade
import os

from FireEngine.core.decorators import singleton
from FireEngine.core.decorators import register
from FireEngine.core.resources import resource_loading

@singleton
@register
class game_ui():
    def __init__(self):
        # UI Texture Loading
        self.crosshair = os.path.join(resource_loading.Assets, "Textures\\UI\\crosshair.png")

    def on_render(self):
        from FireEngine.player import player

        self.priority = 3

        # Draws health
        arcade.draw_text(
            f'Health: {round(player.Player.health)}',
            20,
            20,
            arcade.color.BLACK,
            20
        )

        # Draws the crosshair
        self.draw_crosshair()

    def draw_crosshair(self):
        from FireEngine.core.rendering import render
        crosshair_tex = arcade.load_texture(self.crosshair)

        arcade.draw_texture_rectangle(
            center_x=render.SCREEN_WIDTH // 2,
            center_y=render.SCREEN_HEIGHT // 2,
            width=crosshair_tex.width // 2,
            height=crosshair_tex.height // 2,
            texture=crosshair_tex
        )

GameUI = game_ui()