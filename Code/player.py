import random
import os
import arcade
import sys
import math

# Importing other scripts
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Code"))
from Code import resource_loading as res_load
from Code import scene

import main

# Importing assets 
DIR = os.path.join(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)), "Assets")

        # Player attributes
player_x, player_y = scene.get_player_spawn()
player_angle = 0
player_rotate_speed = 2
player_speed = 2

def update_player_position(self, delta_time):
        """Update player position based on movement flags and camera rotation."""
        move_speed = min(player_speed / main.TILE_SIZE, main.TILE_SIZE / 10) * delta_time * 35 # Ensure small steps relative to tile size

        # Calculate direction vector based on player's current angle
        direction_x = math.cos(player_angle)
        direction_y = math.sin(player_angle)

        new_x = player_x
        new_y = player_y

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