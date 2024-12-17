import arcade
import math
import time

from FireEngine.core.decorators import singleton
from FireEngine.core.decorators import register

@singleton
@register
class debug():
    def __init__(self):
        self.last_time = time.time()  # Store the time of the last frame
        self.fps = 0  # Initialize FPS value
        self.frame_count = 0  # Track number of frames for averaging FPS
        self.fps_update_interval = 1.0  # Update FPS every second
        self.time_accumulator = 0.0  # Accumulate time for FPS update

    def draw_grid(self):
        import main
        from FireEngine.core import scene
        # Define the grid size (matches TILE_SIZE)

        # Draw horizontal lines
        for x in range(main.Render.screen_height, main.Render.screen_height - (len(scene.mapData) * main.TILE_SIZE), - main.TILE_SIZE):
            arcade.draw_line(0, x, len(scene.mapData[0]) * main.TILE_SIZE, x, arcade.color.LIGHT_GRAY)

        # Draw vertical lines
        for y in range(0, len(scene.mapData[0]) * main.TILE_SIZE, main.TILE_SIZE):
            arcade.draw_line(y, main.Render.screen_height, y, main.Render.screen_height - (len(scene.mapData) * main.TILE_SIZE), arcade.color.LIGHT_GRAY)

    def draw_stats(self):
        """Draw FPS counter and general game stats in the top-right corner."""
        import main
        from FireEngine.objects import sprite
        from FireEngine.core import render
        
        # Display FPS in top-right corner
        arcade.draw_text(
            f"FPS: {self.fps:.1f} \nPlayer X: {main.Player.player_x:.1f} \nPlayer Y: {main.Player.player_y:.1f} \nPlayer Rot: {(main.Player.player_angle * (180 / math.pi)):.1f}º \nSprites on Screen: {(sprite.sprite_count)}", 
            10, 
            render.SCREEN_HEIGHT - 20, 
            arcade.color.BLACK
        )

    def draw_map(self):
        import main
        from FireEngine.core import scene

        for row_index, row in enumerate(scene.mapData):
            for col_index, tile in enumerate(row):
                x = col_index * main.TILE_SIZE
                y = main.Render.screen_height - (row_index * main.TILE_SIZE)  # Invert y-axis to match screen    coordinates

                if tile == '█':  # Wall
                    color = arcade.color.GRAY
                elif tile == '░':  # Open Door
                    color = arcade.color.GREEN
                elif tile == '▓':
                    color = arcade.color.RED
                else:  # Empty space or other characters
                    color = arcade.color.WHITE_SMOKE

                arcade.draw_rectangle_filled(x + main.TILE_SIZE / 2, y - main.TILE_SIZE / 2, main.TILE_SIZE,   main.TILE_SIZE, color)

    ########################
    #   Update functions   #
    ########################

    def on_update(self, delta_time):
        import main

        # Accumulate frame times and count frames
        self.time_accumulator += main.Player.frame_time
        self.frame_count += 1

        # Update FPS every second (or based on your chosen interval)
        if self.time_accumulator >= self.fps_update_interval:
            self.fps = self.frame_count / self.time_accumulator  # Calculate average FPS
            self.frame_count = 0  # Reset frame count
            self.time_accumulator = 0.0  # Reset accumulator

    def on_render(self):
        import main 

        self.priority = 4

        # Draw the map and player 
        self.draw_map()
        self.draw_grid()
        arcade.draw_rectangle_filled((main.Player.player_x * main.TILE_SIZE), main.Render.screen_height - (main.Player.player_y * main.TILE_SIZE), main.TILE_SIZE / 2, main.TILE_SIZE / 2, arcade.color.RED)

        # Draw FPS counter and general stats
        self.draw_stats()