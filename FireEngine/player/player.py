from FireEngine.core.decorators import singleton
from FireEngine.core.decorators import register

@singleton
@register
class player():
    def __init__(self):
        from FireEngine.core import scene
        from FireEngine.core import render
        from FireEngine.core.resources import resource_loading
        import os

        #########################
        #   PLAYER ATTRIBUTES   #
        #########################
        
        self.health = 100
        self.max_health = 100
        self.ammo = 30
        self.stamia = 100

        ########################
        #   CAMERA & MOVEMENT  #
        ########################

        self.player_x = 1.5
        self.player_y = 1.5
        self.player_angle = 0

        self.player_rotate_speed = 2
        self.player_speed = 2

        # Movement attributes 
        self.move_up = False
        self.move_down = False
        self.move_right = False
        self.move_left = False

        # Camera turning flags (for arrow keys)
        self.turn_left = False
        self.turn_right = False

        # Initialize direction vector (player facing north by default)
        self.dir_x = 1.0
        self.dir_y = 0.0

        # Initialize camera plane (adjust for FOV)
        self.plane_x = 0.0
        self.plane_y = 0.66

        ##################
        #   FOOT STEPS   #
        ##################

        self.is_moving = False
        self.frame_time = 0.0

        # Footstep sounds
        self.footsteps_folder_path = os.path.join(resource_loading.Assets, "Audio\\Player\\Footsteps")
        self.footstep_sounds = resource_loading.load_folder_sounds(self.footsteps_folder_path)
        self.last_footstep_time = 0  # To manage cooldown between footsteps
        self.footstep_cooldown = 0.4  # Minimum time between footsteps (in seconds)
        self.last_time = 0

        ######################
        #   GUN ATTRIBUTES   #
        ######################

        # Gun position variables
        self.gun_x = render.SCREEN_WIDTH // 2
        self.gun_y = render.SCREEN_HEIGHT // 4  # Slightly lower than center for perspective
        
        # Bobbing effect variables
        self.bob_phase = 0  # Tracks the sine wave phase
        self.bob_amplitude = 5  # How much the gun moves up/down
        self.bob_speed = 5  # Speed of bobbing motion  

        # Gun animation loading
        self.gun_animation_frames = resource_loading.load_animation(os.path.join(resource_loading.Assets, "Textures\\Guns\\Pistol"))
        self.current_frame_index = 0  # Track the current frame of the animation
        self.animation_timer = 0      # Timer to control frame rate
        self.animation_speed = 0.07   # Time (in seconds) between frames
        self.is_shooting = False      # Flag to indicate if the gun is animating

        # Gun sounds
        self.gun_sounds = resource_loading.load_folder_sounds(os.path.join(resource_loading.Assets, "Audio\\Player\\Guns\\Pistol"))

        #####################
        #   SCREEN EFFECT   #
        #####################

        self.health_vfx_indicator_time = .75
        self.health_vfx_indicator = 0

    def update_player_position(self, delta_time: float):
        """Update player position based on movement flags and camera rotation."""
        from FireEngine.core import scene
        import math

        move_speed = min(self.player_speed / scene.TILE_SIZE, scene.TILE_SIZE / 10) * delta_time * 35 # Ensure small steps relative to tile size

        # Calculate direction vector based on player's current angle
        direction_x = math.cos(self.player_angle)
        direction_y = math.sin(self.player_angle)

        new_x = self.player_x
        new_y = self.player_y

        # Move forward (W key) or backward (S key) based on camera direction
        if self.move_up:  # Move forward
            new_x += direction_x * move_speed
            new_y += direction_y * move_speed
            if not self.check_collision(new_x * scene.TILE_SIZE, new_y * scene.TILE_SIZE):  # Only update if no collision detected
                self.player_x = new_x
                self.player_y = new_y

        if self.move_down:  # Move backward
            new_x -= direction_x * move_speed
            new_y -= direction_y * move_speed
            if not self.check_collision(new_x * scene.TILE_SIZE, new_y * scene.TILE_SIZE):  # Only update if no collision detected
                self.player_x = new_x
                self.player_y = new_y

        # Strafe left (A key) or right (D key)
        if self.move_left:  # Strafe left (perpendicular to view direction)
            strafe_x = math.cos(self.player_angle - math.pi / 2)
            strafe_y = math.sin(self.player_angle - math.pi / 2)
            new_x += strafe_x * move_speed
            new_y += strafe_y * move_speed
            if not self.check_collision(new_x * scene.TILE_SIZE, new_y * scene.TILE_SIZE):  # Only update if no collision detected
                self.player_x = new_x
                self.player_y = new_y

        if self.move_right:  # Strafe right (perpendicular to view direction)
            strafe_x = math.cos(self.player_angle + math.pi / 2)
            strafe_y = math.sin(self.player_angle + math.pi / 2)
            new_x += strafe_x * move_speed
            new_y += strafe_y * move_speed
            if not self.check_collision(new_x * scene.TILE_SIZE, new_y * scene.TILE_SIZE):  # Only update if no collision detected
                self.player_x = new_x
                self.player_y = new_y

    def check_collision(self, x: float, y: float):
        """Check if the player's bounding box collides with any walls."""
        from FireEngine.core import scene

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
            map_x = int(corner_x // scene.TILE_SIZE)
            map_y = int(corner_y // scene.TILE_SIZE)

            # Ensure we're not out of bounds
            if map_x < 0 or map_x >= len(scene.scene_data[0]) or map_y < 0 or map_y >= len(scene.scene_data):
                return True  # Treat out-of-bounds as a collision

            # Check if any corner is inside a wall ('█')
            if scene.scene_data[map_y][map_x] == '█' or scene.scene_data[map_y][map_x] == '▓':
                return True  # Collision detected

        return False  # No collision

    def play_random_footstep(self):
        """Play a random footstep sound."""
        import random
        import arcade

        if self.footstep_sounds:
            random_sound = random.choice(self.footstep_sounds)
            arcade.play_sound(random_sound, volume=0.2)  #  Adjust volume as needed

    def play_gun_sound(self):
        """Play a random gun sound."""
        import random
        import arcade

        if self.gun_sounds:
            random_sound = random.choice(self.gun_sounds)
            arcade.play_sound(random_sound, volume=0.5)  # Adjust volume as needed

    def gun_logic(self, delta_time):
        from FireEngine.core import render
        import math

        # Bobs gun as player moves
        if self.is_moving:
            self.bob_phase += self.bob_speed * delta_time
            self.gun_y = (render.SCREEN_HEIGHT // 4) + math.sin(self.bob_phase) * self.bob_amplitude
            self.gun_x = (render.SCREEN_WIDTH // 2) + math.cos(self.bob_phase) * (self.bob_amplitude / 2)
        else:
            self.bob_phase = 0
            self.gun_y = render.SCREEN_HEIGHT // 4

        #############################
        #   GUN ANIMATION HANDLER   #
        #############################

        # Update gun animation if shooting
        if self.is_shooting:
            self.animation_timer += delta_time

            # Advance to next frame when enough time has passed
            if self.animation_timer >= self.animation_speed:
                self.animation_timer -= self.animation_speed
                self.current_frame_index += 1

                # Stop animation if we've reached the last frame
                if self.current_frame_index >= len(self.gun_animation_frames):
                    self.is_shooting = False  # End shooting animation
                    self.current_frame_index = 0  # Reset frame index for next

    def shoot(self):
        """Cast a ray and check for wall or sprite collisions."""
        from FireEngine.objects import entity
        from FireEngine.core import scene
        from FireEngine.core import render
        import math
        
        # Play a gun sound when shooting
        if self.current_frame_index != 0:
            return

        self.play_gun_sound()

        # Start gun animation
        self.is_shooting = True
        self.current_frame_index = 1  # Reset to the first frame of the animation
        self.animation_timer = 0      # Reset animation timer

        # Player's starting position
        ray_x = self.player_x
        ray_y = self.player_y

        # Ray direction (player's facing direction)
        ray_dir_x = math.cos(self.player_angle)
        ray_dir_y = math.sin(self.player_angle)

        # Player's current position in grid units
        map_x = int(ray_x)
        map_y = int(ray_y)

        # Distance increments for each step along x and y axes
        delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else    float('inf')
        delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else    float('inf')

        # Calculate step direction and initial side distances
        if ray_dir_x < 0:
            step_x = -1
            side_dist_x = (ray_x - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - ray_x) * delta_dist_x

        if ray_dir_y < 0:
            step_y = -1
            side_dist_y = (ray_y - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - ray_y) * delta_dist_y

        # Perform DDA to find where the ray hits a wall or sprite
        hit_wall = False
        max_distance = render.MAX_DEPTH  # Limit how far the ray can   travel

        while not hit_wall and max_distance > 0:
            max_distance -= 1

            # Move to the next grid square in either x or y     direction
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0  # Hit was on an x-side (vertical wall)
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1  # Hit was on a y-side (horizontal wall)

            # Check if we've hit a wall ('█' or '▓')
            if scene.scene_data[map_y][map_x] == '█' or scene.scene_data[map_y]   [map_x] == '▓':
                hit_wall = True
                break

            # Check for entity collision at this grid cell  during traversal
            for ent in entity.entities:
                if int(ent.x) == map_x and int(ent.y) ==  map_y:
                    if not ent.is_dying:
                        ent.hurt_sprite(ent, 25, self)
                        return  # Stop after hitting a sprite
                        
        if not hit_wall:
            return

    def hurt_player(self, damage):
        '''Damages the player and plays a sound effect'''
        self.health_vfx_indicator = self.health_vfx_indicator_time
        
        if damage > self.health:
            #arcade.exit()
            dam = self.health
        else:
            dam = damage

        self.health -= dam
        
    def heal_player(self, heal):
        '''Heals the player and plays a sound effect'''

    ########################
    #   Update functions   #
    ########################

    def on_update(self, delta_time: float): 
        import math
        import time

        # Update player position based on movement flags
        self.update_player_position(delta_time=delta_time)

        # Turn speed in radians per frame (e.g., 2 degrees per frame)
        turn_speed = 2 * math.pi / 180 * delta_time * 35 * self.player_rotate_speed

        # Adjust player angle for camera turning (left/right)
        if self.turn_left:
            self.player_angle -= turn_speed  # Turn left (counterclockwise)
        if self.turn_right:
            self.player_angle += turn_speed  # Turn right (clockwise)

        # Update direction vector based on new angle
        self.dir_x = math.cos(self.player_angle)
        self.dir_y = math.sin(self.player_angle)

        # Update camera plane based on new angle
        # This keeps the FOV constant while rotating
        self.plane_x = -(2/3) * math.sin(self.player_angle)  # Adjust -0.66 for FOV scaling
        self.plane_y = (2/3) * math.cos(self.player_angle)

        # Check if player is moving
        is_moving = self.move_up or self.move_down or self.move_left or self.move_right

        # Play footstep sound if moving and cooldown has passed
        current_time = time.time()
        if is_moving and current_time - self.last_footstep_time > self.footstep_cooldown:
            self.play_random_footstep()
            self.last_footstep_time = current_time

        self.frame_time = current_time - self.last_time
        self.last_time = current_time

        self.gun_logic(delta_time)

        # Heal over time
        if(self.health < self.max_health):
            self.health += 6.5 * delta_time

                # Update screen effects
        
        if(self.health_vfx_indicator > 0):
            self.health_vfx_indicator -= delta_time

    def on_render(self):
        from FireEngine.core import render
        import arcade

        self.priority = 1

        # Draw gun texture (either static or animated)
        if self.is_shooting:
            current_frame = self.gun_animation_frames[self.current_frame_index]
            arcade.draw_texture_rectangle(
                center_x=self.gun_x - 20,
                center_y=self.gun_y,
                width=128 * 2.5,  # Adjust based on your texture size
                height=128 * 2.5,
                texture=current_frame # type: ignore
            )
        else:
            # Draw static gun texture when not shooting (optional)
            arcade.draw_texture_rectangle(
                center_x=self.gun_x - 20,
                center_y=self.gun_y,
                width=128 * 2.5,
                height=128 * 2.5,
                texture=self.gun_animation_frames[0]  # Default static frame # type: ignore
            )

        # Screen effects
        arcade.draw_rectangle_filled(
            center_x=render.SCREEN_WIDTH // 2,
            center_y=render.SCREEN_HEIGHT // 2,
            width=render.SCREEN_WIDTH,
            height=render.SCREEN_HEIGHT,
            color=(255, 0, 0, int((self.health_vfx_indicator / self.health_vfx_indicator_time) * 100) + max(0, min((100 - self.health), 100)))
        )

    def on_shoot(self):
        self.shoot()

    def on_move_up(self, state: bool):
        self.move_up = state

    def on_move_down(self, state: bool):
        self.move_down = state

    def on_move_right(self, state: bool):
        self.move_right = state

    def on_move_left(self, state: bool):
        self.move_left = state

    def on_turn_right(self, state: bool):
        self.turn_right = state

    def on_turn_left(self, state: bool):
        self.turn_left = state

Player = player()