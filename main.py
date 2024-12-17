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

# USING, 'arcade'

# Imports
import arcade
import arcade.color
import arcade.color
import arcade.key
import math
import random
import os
import time
from PIL import Image
import sys

# Importing other scripts
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Code"))
from Code import scene
from Code import resource_loading as res_load
from Code import sprite
from Code import manager
from Code import player
from Code import render

# Constants
SCREEN_TITLE = "Minenstien"

TILE_SIZE = 20  # Size of each tile on the map

# Get the directory of the current script
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Assets")

# Creates new game manager object, register update and render functions to it so they are ran.
game_manager = manager.GameManager()
Player = player.player()
Render = render.render(Player)

# Game class inheriting from arcade.Window
class GameLoop(arcade.Window):
    def __init__(self):
        super().__init__(render.SCREEN_WIDTH, render.SCREEN_HEIGHT, SCREEN_TITLE, resizable=True, vsync=True) # type: ignore

        # Clear out texture Cache
        res_load.delete_all_files_in_directory(os.path.join(DIR, "Cache"))

        # Inits player class and registers it with the game manager
        game_manager.register(Player)
        game_manager.register(Render)
        
        # Sprite Texture Loading
        self.guard = os.path.join(DIR, "Textures\\Sprites\\Guard\\guard_sheet.png")

        # UI Texture Loading
        self.crosshair = os.path.join(DIR, "Textures\\UI\\crosshair.png")

        # Audio Loading
        self.songs_folder_path = os.path.join(DIR, "Sounds\\Music")
        self.songs = self.get_music_files()
        random.shuffle(self.songs)  # Shuffle the song list randomly
        self.current_song_index = 0
        self.current_player = None

        # Create a list of sprites with their positions in the game world
        for y in range(len(scene.mapData)):
            for x in range(len(scene.mapData[0])):
                if scene.mapData[y][x] == '$':
                    scene.mapData[y] = scene.mapData[y][:x] + ' ' + scene.mapData[y][x+1:]
                    new_sprite = sprite.Sprite(x, y, 0, 0.3, 0.3, self.guard, health=100)
                    sprite.sprites.append(new_sprite)
                    game_manager.register(new_sprite)

        self.last_time = time.time()  # Store the time of the last frame
        self.fps = 0  # Initialize FPS value
        self.frame_count = 0  # Track number of frames for averaging FPS
        self.fps_update_interval = 1.0  # Update FPS every second
        self.time_accumulator = 0.0  # Accumulate time for FPS update

    def on_update(self, delta_time):
        """Update game state."""
        game_manager.update(delta_time)

        # print(f'Obj reg {game_manager.registered_objects}')

        # Audio update
        self.play_next_song()

        # Accumulate frame times and count frames
        self.time_accumulator += Player.frame_time
        self.frame_count += 1

        # Update FPS every second (or based on your chosen interval)
        if self.time_accumulator >= self.fps_update_interval:
            self.fps = self.frame_count / self.time_accumulator  # Calculate average FPS
            self.frame_count = 0  # Reset frame count
            self.time_accumulator = 0.0  # Reset accumulator

        # Update screen effects
        if(Player.health_vfx_indicator > 0):
            Player.health_vfx_indicator -= delta_time

        # Rest of your game update logic...
        super().on_update(delta_time)  # Call parent class update if needed

    def on_draw(self):
        """Render the screen."""
        arcade.start_render()

        # Draws floor
        #self.draw_floor()
        arcade.draw_rectangle_filled(
            center_x=Render.screen_width // 2,
            center_y=Render.screen_height // 4,  
            width=Render.screen_width,
            height=Render.screen_height // 2,
            color=(120, 120, 120, 255)
        )
        
        # Ceiling
        arcade.draw_rectangle_filled(
            center_x=Render.screen_width // 2,
            center_y=(3 * Render.screen_height) // 4,  
            width=Render.screen_width,
            height=Render.screen_height // 2,
            color=(71, 71, 71, 255)
        )

        # Draw the map and player 
        #self.draw_map()
        #self.draw_grid()
        #arcade.draw_rectangle_filled((Player.player_x * TILE_SIZE), self.screen_height - (Player.player_y * TILE_SIZE), TILE_SIZE / 2, TILE_SIZE / 2, arcade.color.RED)

        # Draw FPS counter and general stats
        self.draw_stats()

        # Draws health
        arcade.draw_text(
            f'Health: {round(Player.health)}',
            20,
            20,
            arcade.color.BLACK,
            20
        )

        # Draws the crosshair
        self.draw_crosshair()

        game_manager.render()

    def on_key_press(self, key, modifiers):
        """Handle key press events."""
        if key == arcade.key.W:
            self.move_up = True
            game_manager.move_up(True)
        elif key == arcade.key.S:
            self.move_down = True
            game_manager.move_down(True)
        elif key == arcade.key.A:
            self.move_left = True
            game_manager.move_left(True)
        elif key == arcade.key.D:
            self.move_right = True
            game_manager.move_right(True)
        elif key == arcade.key.LEFT:  # Turn camera left
            self.turn_left = True
            game_manager.turn_left(True)
        elif key == arcade.key.RIGHT:  # Turn camera right
            self.turn_right = True
            game_manager.turn_right(True)
        elif key == arcade.key.E:  # Interact with objects
            self.interact()  # Call interaction function
        elif key == arcade.key.SPACE:  # Example: SPACE key for shooting
            game_manager.on_shoot()

    def on_key_release(self, key, modifiers):
        """Handle key release events."""
        if key == arcade.key.W:
            self.move_up = False
            game_manager.move_up(False)
        elif key == arcade.key.S:
            self.move_down = False
            game_manager.move_down(False)
        elif key == arcade.key.A:
            self.move_left = False
            game_manager.move_left(False)
        elif key == arcade.key.D:
            self.move_right = False
            game_manager.move_right(False)
        elif key == arcade.key.LEFT:  # Stop turning left
            self.turn_left = False
            game_manager.turn_left(False)
        elif key == arcade.key.RIGHT:  # Stop turning right
            self.turn_right = False
            game_manager.turn_right(False)

    def draw_grid(self):
        # Define the grid size (matches TILE_SIZE)

        # Draw horizontal lines
        for x in range(self.screen_height, self.screen_height - (len(scene.mapData) * TILE_SIZE), -TILE_SIZE):
            arcade.draw_line(0, x, len(scene.mapData[0]) * TILE_SIZE, x, arcade.color.LIGHT_GRAY)

        # Draw vertical lines
        for y in range(0, len(scene.mapData[0]) * TILE_SIZE, TILE_SIZE):
            arcade.draw_line(y, self.screen_height, y, self.screen_height - (len(scene.mapData) * TILE_SIZE), arcade.color.LIGHT_GRAY)

    def draw_stats(self):
        """Draw FPS counter and general game stats in the top-right corner."""
        # Display FPS in top-right corner
        arcade.draw_text(
            f"FPS: {self.fps:.1f} \nPlayer X: {Player.player_x:.1f} \nPlayer Y: {Player.player_y:.1f} \nPlayer Rot: {(Player.player_angle * (180 / math.pi)):.1f}º \nSprites on Screen: {(sprite.sprite_count)}", 
            10, 
            render.SCREEN_HEIGHT - 20, 
            arcade.color.BLACK
        )

    def draw_map(self):
        for row_index, row in enumerate(scene.mapData):
            for col_index, tile in enumerate(row):
                x = col_index * TILE_SIZE
                y = self.screen_height - (row_index * TILE_SIZE)  # Invert y-axis to match screen    coordinates

                if tile == '█':  # Wall
                    color = arcade.color.GRAY
                elif tile == '░':  # Open Door
                    color = arcade.color.GREEN
                elif tile == '▓':
                    color = arcade.color.RED
                else:  # Empty space or other characters
                    color = arcade.color.WHITE_SMOKE

                arcade.draw_rectangle_filled(x + TILE_SIZE / 2, y - TILE_SIZE / 2, TILE_SIZE,   TILE_SIZE, color)

    def draw_floor(self):
        """Render textured floor using a raycasting-like    approach."""
        # Load floor texture from disk
        floor_tex = arcade.load_texture(self.floor_texture)
        texture_image = floor_tex.image  # Get the Pillow image     object of the texture
        texture_width, texture_height = floor_tex.width,    floor_tex.height
    
        # Create an empty image object for rendering the floor
        floor_render = Image.new("RGBA", (SCREEN_WIDTH,     SCREEN_HEIGHT), (0, 0, 0, 255))
        pixels = floor_render.load()  # Access pixel data for   manipulation
    
        # Precompute direction vectors for leftmost and     rightmost rays
        rayDirX0 = Player.dir_x - Player.plane_x
        rayDirY0 = Player.dir_y - Player.plane_y
        rayDirX1 = Player.dir_x + Player.plane_x
        rayDirY1 = Player.dir_y + Player.plane_y
    
        # Loop through each row below the horizon (bottom half  of the screen)
        for y in range(0 + 1, SCREEN_HEIGHT):
            # Current y position compared to the center of the  screen (the horizon)
            p = y - 0 / 2
    
            # Vertical position of the camera
            posZ = 0.5 * SCREEN_HEIGHT
    
            # Horizontal distance from the camera to the floor  for this row
            rowDistance = posZ / p
    
            # Calculate real-world step vector for each x   (parallel to camera plane)
            floorStepX = rowDistance * (rayDirX1 - rayDirX0) /  SCREEN_WIDTH
            floorStepY = rowDistance * (rayDirY1 - rayDirY0) /  SCREEN_WIDTH
    
            # Real-world coordinates of the leftmost column
            floorX = self.player_x + rowDistance * rayDirX0
            floorY = self.player_y + rowDistance * rayDirY0
    
            # Loop through each column (pixel) in this row
            for x in range(SCREEN_WIDTH):
                # Get map cell coordinates (integer parts of    floorX and floorY)
                cellX = int(floorX)
                cellY = int(floorY)
    
                # Get texture coordinates from fractional parts of floorX and floorY using bitwise operations
                tx = int(texture_width * (floorX - int(floorX))) % texture_width
                ty = int(texture_height * (floorY - int(floorY))) % texture_height
    
                # Increment real-world coordinates for the next     pixel
                floorX += floorStepX
                floorY += floorStepY
    
                # Sample color from the texture at (tx, ty)
                color = floor_tex.image.getpixel((tx, ty))

                # Set pixel color in the output image at (x, y)
                pixels[x, y] = color # type: ignore
    
        # Convert Pillow image back to an Arcade texture and    draw it on screen
        arcade_texture = arcade.Texture(name="floor_render", image=floor_render)
        arcade.draw_texture_rectangle(
            center_x=SCREEN_WIDTH // 2,
            center_y=SCREEN_HEIGHT // 4,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT // 2,
            texture=arcade_texture,
        )

    def draw_crosshair(self):
        crosshair_tex = arcade.load_texture(self.crosshair)

        arcade.draw_texture_rectangle(
            center_x=render.SCREEN_WIDTH // 2,
            center_y=render.SCREEN_HEIGHT // 2,
            width=crosshair_tex.width // 2,
            height=crosshair_tex.height // 2,
            texture=crosshair_tex
        )

    def interact(self):
        """Check if the player is facing an interactive object and trigger a callback."""

        # Calculate the direction vector based on player's current angle
        direction_x = math.cos(Player.player_angle)
        direction_y = math.sin(Player.player_angle)

        # Calculate the tile in front of the player
        front_x = int(Player.player_x + direction_x)
        front_y = int(Player.player_y + direction_y)

        # Check if the tile in front of the player is interactive (e.g., a door '░')
        if scene.mapData[front_y][front_x] == '░' or scene.mapData[front_y][front_x] == '▓':  # Example: Door tile
            self.interact_door(front_x, front_y)  # Trigger callback to open door

    def interact_door(self, x, y):
        """Open a door at position (x, y)."""
        if(scene.mapData[y][x] == '░'): # Open
            scene.mapData[y] = scene.mapData[y][:x] + '▓' + scene.mapData[y][x+1:]
        else:
            scene.mapData[y] = scene.mapData[y][:x] + '░' + scene.mapData[y][x+1:]

    def get_music_files(self):
        """Get all music files from the specified folder."""
        music_files = []
        for file in os.listdir(self.songs_folder_path):
            if file.endswith(('.mp3', '.wav')):  # Filter by audio file types
                music_files.append(os.path.join(self.songs_folder_path, file))
        return music_files

    def play_next_song(self):
        """Play the next song in the shuffled list."""
        if self.current_player is None or not self.current_player.playing:
            if self.current_song_index < len(self.songs):
                song_path = self.songs[self.current_song_index]
                sound = arcade.load_sound(song_path)
                self.current_player = arcade.play_sound(sound, volume=0.2) # type: ignore
                self.current_song_index += 1
            else:
                self.songs = self.get_music_files()
                random.shuffle(self.songs)  # Shuffle the song list randomly
                self.current_song_index = 0
                self.current_player = None

# Main function to start the game
def main():
    """Main function to set up and run the game."""
    game = GameLoop()
    arcade.run()

if __name__ == "__main__":
    main()