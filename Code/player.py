import random
import os
import arcade
import sys
import math

# Importing other scripts
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Code"))
from Code import resource_loading as res_load
from Code import scene
from Code import manager

import main

# Importing assets 
DIR = os.path.join(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)), "Assets")

class player():
    def __init__(self):
        # Player attributes
        self.player_x, self.player_y = scene.get_player_spawn()
        self.player_angle = 0
        self.player_rotate_speed = 2
        self.player_speed = 2

        # Movement attributes 
        self.move_up = False
        self.move_down = False
        self.move_right = False
        self.move_left = False

    def update_player_position(self, delta_time):
        """Update player position based on movement flags and camera rotation."""
        # print('Update Player! 1')

        move_speed = min(self.player_speed / main.TILE_SIZE, main.TILE_SIZE / 10) * delta_time * 35 # Ensure small steps relative to tile size
        # Calculate direction vector based on player's current angle
        direction_x = math.cos(self.player_angle)
        direction_y = math.sin(self.player_angle)

        new_x = self.player_x
        new_y = self.player_y

        # Move forward (W key) or backward (S key) based on camera direction
        if self.move_up:  # Move forward
            new_x += direction_x * move_speed
            new_y += direction_y * move_speed
            if not self.check_collision(new_x * main.TILE_SIZE, new_y * main.TILE_SIZE):  # Only update if no collision detected
                self.player_x = new_x
                self.player_y = new_y

        if self.move_down:  # Move backward
            new_x -= direction_x * move_speed
            new_y -= direction_y * move_speed
            if not self.check_collision(new_x * main.TILE_SIZE, new_y * main.TILE_SIZE):  # Only update if no collision detected
                self.player_x = new_x
                self.player_y = new_y

        # Strafe left (A key) or right (D key)
        if self.move_left:  # Strafe left (perpendicular to view direction)
            strafe_x = math.cos(self.player_angle - math.pi / 2)
            strafe_y = math.sin(self.player_angle - math.pi / 2)
            new_x += strafe_x * move_speed
            new_y += strafe_y * move_speed
            if not self.check_collision(new_x * main.TILE_SIZE, new_y * main.TILE_SIZE):  # Only update if no collision detected
                self.player_x = new_x
                self.player_y = new_y

        if self.move_right:  # Strafe right (perpendicular to view direction)
            strafe_x = math.cos(self.player_angle + math.pi / 2)
            strafe_y = math.sin(self.player_angle + math.pi / 2)
            new_x += strafe_x * move_speed
            new_y += strafe_y * move_speed
            if not self.check_collision(new_x * main.TILE_SIZE, new_y * main.TILE_SIZE):  # Only update if no collision detected
                self.player_x = new_x
                self.player_y = new_y

        # print(f'Update Player! {self.player_x} {self.player_y}')

    def check_collision(self, x, y):
        """Check if the player's bounding box collides with any walls."""
        # Define a small collision buffer around the player
        buffer = 0.15  # Adjust this value as needed

        # Check four corners of the player's bounding box
        corners = [
            (x - buffer, y - buffer),  # Bottom-left
            (x + buffer, y - buffer),  # Bottom-right
            (x - buffer, y + buffer),  # Top-left
            (x + buffer, y + buffer)   # Top-right
        ]

        for corner_x, corner_y in corners:
            # Convert corner coordinates to map grid indices
            map_x = int(corner_x // main.TILE_SIZE)
            map_y = int(corner_y // main.TILE_SIZE)

            # Ensure we're not out of bounds
            if map_x < 0 or map_x >= len(scene.mapData[0]) or map_y < 0 or map_y >= len(scene.mapData):
                return True  # Treat out-of-bounds as a collision

            # Check if any corner is inside a wall ('█')
            if scene.mapData[map_y][map_x] == '█' or scene.mapData[map_y][map_x] == '▓':
                return True  # Collision detected

        return False  # No collision
    
    def on_update(self, delta_time):
        # Update player position based on movement flags
        self.update_player_position(delta_time=delta_time)

    def on_move_up(self, state):
        self.move_up = state

    def on_move_down(self, state):
        self.move_down = state

    def on_move_right(self, state):
        self.move_right = state

    def on_move_left(self, state):
        self.move_left = state