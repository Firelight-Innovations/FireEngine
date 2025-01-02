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
        from FireEngine.core import render
        # Define the grid size (matches TILE_SIZE)

        # Draw horizontal lines
        for x in range(render.SCREEN_HEIGHT, render.SCREEN_HEIGHT - (len(scene.scene_data) * scene.TILE_SIZE), - scene.TILE_SIZE):
            arcade.draw_line(0, x, len(scene.scene_data[0]) * scene.TILE_SIZE, x, arcade.color.LIGHT_GRAY)

        # Draw vertical lines
        for y in range(0, len(scene.scene_data[0]) * scene.TILE_SIZE, scene.TILE_SIZE):
            arcade.draw_line(y, render.SCREEN_HEIGHT, y, render.SCREEN_HEIGHT - (len(scene.scene_data) * scene.TILE_SIZE), arcade.color.LIGHT_GRAY)

    def draw_stats(self):
        """Draw FPS counter and general game stats in the top-right corner."""
        from FireEngine.core import render
        from FireEngine.player import player
        
        # Display FPS in top-right corner
        '''
        arcade.draw_text(
            text=f"FPS: {self.fps:.1f} \nPlayer X: {player.Player.player_x:.1f} \nPlayer Y: {player.Player.player_y:.1f} \nPlayer Rot: {(player.Player.player_angle * (180 / math.pi)):.1f}º \nObjects on Screen: {render.Render.object_count}", 
            start_x=10, 
            start_y=render.SCREEN_HEIGHT - 20, 
            color=arcade.color.BLACK,
            anchor_x="center"
        )
        '''

    def draw_map(self):
        from FireEngine.core import scene
        from FireEngine.core import render

        for row_index, row in enumerate(scene.scene_data):
            for col_index, tile in enumerate(row):
                x = col_index * scene.TILE_SIZE
                y = render.SCREEN_HEIGHT - (row_index * scene.TILE_SIZE)  # Invert y-axis to match screen    coordinates

                if tile == '█':  # Wall
                    color = arcade.color.GRAY
                elif tile == '░':  # Open Door
                    color = arcade.color.GREEN
                elif tile == '▓':
                    color = arcade.color.RED
                else:  # Empty space or other characters
                    color = arcade.color.WHITE_SMOKE

                arcade.draw_rectangle_filled(x + scene.TILE_SIZE / 2, y - scene.TILE_SIZE / 2, scene.TILE_SIZE,   scene.TILE_SIZE, color)

    ########################
    #   Update functions   #
    ########################

    def on_update(self, delta_time):
        from FireEngine.player import player

        # Accumulate frame times and count frames
        self.time_accumulator += player.Player.frame_time
        self.frame_count += 1

        # Update FPS every second (or based on your chosen interval)
        if self.time_accumulator >= self.fps_update_interval:
            self.fps = self.frame_count / self.time_accumulator  # Calculate average FPS
            self.frame_count = 0  # Reset frame count
            self.time_accumulator = 0.0  # Reset accumulator

    def on_render(self):
        from FireEngine.player import player 
        from FireEngine.core import scene
        from FireEngine.core import render

        self.priority = 4

        # Draw the map and player 
        self.draw_map()
        self.draw_grid()
        arcade.draw_rectangle_filled((player.Player.player_x * scene.TILE_SIZE), render.SCREEN_HEIGHT - (player.Player.player_y * scene.TILE_SIZE), scene.TILE_SIZE / 2, scene.TILE_SIZE / 2, arcade.color.RED)

        # Draw FPS counter and general stats
        self.draw_stats()

Debug = debug()