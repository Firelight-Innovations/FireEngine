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
from asyncio.windows_events import NULL
from turtle import color
import arcade
import arcade.color
import arcade.color
import arcade.key
import math
import random
import os
import time
from PIL import Image, ImageDraw
from matplotlib.pylab import rand
from pyparsing import col

# Wall: '█'
# Door: '░'
# Open door: '░'
# Empty Space: ' '
# Player Spawn:'*'
# Enemy Spawn: '$'

mapData = ['██████████████▓██████████████████████',
           '█   █   $█  ██  █   $    █ █        █',
           '█*  ▓  $ ▓   $  █        ▓ ▓   $    █',
           '█   █    █  ██ $██████████ █     $  █',
           '██▓███████████▓███████████ ██████████',
           '█      $ █ $    █   $    ▓$▓     $  █',
           '█    $   █     $█        █ █  $     █',
           '█▓█████████████▓██████████▓██████████',
           '█    $            $           $     █',
           '████▓████▓███████▓███▓████▓██████████',
           '█  $   █       █   █   $█  $      $ █',
           '█  █   █  $█   █   █    █         $ █',
           '█  █   █   █   █ $ █    █   $       █',
           '█ $█ $     █$ $█   █ $  █       $   █',
           '█████████████████████████████████████']

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Minenstien"

TILE_SIZE = 20  # Size of each tile on the map
MAX_DEPTH = 30

FOV = math.pi / 3 # Field of view (60 degrees)
NUM_RAYS = 200     # Number of rays casted for rendering

# Get the directory of the current script
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Assets")

def get_player_spawn(self):
    x = 0
    y = 0

    for row_index, row in enumerate(mapData):
        for col_index, tile in enumerate(row):
            x = col_index
            y = row_index# Invert y-axis to match screencoordinates
            if tile == '*':  # Player Spawn
                return x + 0.5, y + 0.5

def delete_all_files_in_directory(directory_path):
    try:
        # List all files in the directory
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            # Check if it's a file before deleting
            if os.path.isfile(file_path):
                os.remove(file_path)
    except Exception as e:
        return

# Resource loading
def load_animation(folder_path, return_paths=False):
    """Load all animation frames from the specified folder."""
    frames = []
    paths = []
    for file in sorted(os.listdir(folder_path)):  # Sort ensures frames are in order
        if file.endswith(".png"):  # Only load PNG files
            full_path = os.path.join(folder_path, file)
            frames.append(arcade.load_texture(full_path))
            paths.append(full_path)
    
    if return_paths:
        return frames, paths
    else:
        return frames
    
def load_folder_sounds(folder_path):
    """Load all gore/scream sounds from the specified folder."""
    folder_contents = []
    for file in os.listdir(folder_path):
        if file.endswith(('.wav', '.mp3')):  # Filter for valid audio files
            full_path = os.path.join(folder_path, file)
            folder_contents.append(arcade.load_sound(full_path))
    return folder_contents

class Sprite:
    def __init__(self, x, y, rotation, hitbox_x, hitbox_y, sprite_sheet_path, health=math.inf):
        self.x = float(x + 0.5)
        self.y = float(y + 0.5)
        self.rotation = rotation
        self.animation_rotation = 0
        self.hitbox_x = float(hitbox_x)
        self.hitbox_y = float(hitbox_y)
        self.health = health
        self.sprite_sheet_path = sprite_sheet_path
        
        self.walk_ani_0, self.walk_ani_0_path, self.walk_ani_45, self.walk_ani_45_path, self.walk_ani_90, self.walk_ani_90_path, self.walk_ani_135, self.walk_ani_135_path, self.walk_ani_180, self.walk_ani_180_path, self.walk_ani_225, self.walk_ani_225_path, self.walk_ani_270, self.walk_ani_270_path, self.walk_ani_315, self.walk_ani_315_path, self.shoot_ani, self.shoot_ani_path, self.death_ani, self.death_ani_path = self.load_animations(self.sprite_sheet_path)

        # Death animation properties
        self.death_animation = self.death_ani or []
        self.is_dying = False
        self.current_death_frame = 0
        self.death_timer = 0
        self.death_frame_duration = 0.2  # Time (in seconds) per frame

        self.patrol_timer = random.uniform(1, 3)  # Time to move from current spot to the other
        self.patrol_wait = random.uniform(1, 3) # Time to wait between movements
        self.target_x = None
        self.target_y = None

        self.max_detect_distance = 4.5

        # Walking animation
        self.is_walking = False
        self.current_walk_frame = 0
        self.walk_timer = 0
        self.walk_frame_duration = .2

        # Shooting animation
        self.is_shooting = False
        self.current_shoot_frame = 0
        self.shoot_timer = 0
        self.fire_frame_duration = 0.1
        self.no_fire_frame_duration = random.uniform(1, 8) / 10

        # Audio
        self.gun_shot = arcade.load_sound(os.path.join(DIR, "Sounds\\Enemies\\Gun\\Pistol Single Shot.wav"))

        # Textures
        self.texture = self.shoot_ani[1]
        self.texture_path = self.shoot_ani_path[1]

        # Load gore/scream sounds
        self.gore_sounds = load_folder_sounds(os.path.join(DIR, "Sounds\\Enemies\\Gore"))

        # Load specific death sound
        self.scream_sounds = load_folder_sounds(os.path.join(DIR, "Sounds\\Enemies\\Scream"))

        # Load specific death sound
        self.death_sound = load_folder_sounds(os.path.join(DIR, "Sounds\\Enemies\\Death"))

    def load_animations(self, path):
        '''Loads all animations and textures from a sprite sheet'''
        walk_ani_0 = []
        walk_ani_0_path = []
        walk_ani_45 = []
        walk_ani_45_path = []
        walk_ani_90 = []
        walk_ani_90_path = []
        walk_ani_135 = []
        walk_ani_135_path = []
        walk_ani_180 = []
        walk_ani_180_path = []
        walk_ani_225 = []
        walk_ani_225_path = []
        walk_ani_270 = []
        walk_ani_270_path = []
        walk_ani_315 = []
        walk_ani_315_path = []
        shoot_ani = []
        shoot_ani_path = []
        death_ani = []
        death_ani_path = []

        # Load sheet
        sheet = arcade.load_texture(path)
        height, width = sheet.height, sheet.width

        # Splice sheet
        # Load all shoot_ani

        y = height - 64

        # Scans file from the very bottom to the very top
        # Loops through all rows in sprite sheet
        for i in range(0, round(height / 65)):
            # Loops through row
            loop = True
            x = 0 # x-val for sprite sheet
            j = 0 # index of sprite for that row, used to seperarate walk cycle angles
            while loop:
                try:
                    texture = arcade.load_texture(
                        path,
                        x=x,
                        y=y,
                        width=64,
                        height=64
                    )
                    x += 65

                    # Check if all pixels are fully transparent
                    image = texture.image
                    loop = not all(pixel == (0, 0, 0, 0) for pixel in image.getdata())
                    if loop:
                        output_folder = os.path.join(DIR, "Cache")
                        output_file = f"{x}{y}{i}{j}-{height * random.randint(0, 10)}.png"

                        # Ensure the folder exists
                        os.makedirs(output_folder, exist_ok=True)

                        # Save the image to the specified folder
                        output_path = os.path.join(output_folder, output_file)
                        image.save(output_path)

                        if i == 0:
                            shoot_ani.append(texture)
                            shoot_ani_path.append(output_path)
                        elif i == 1:
                            death_ani.append(texture)
                            death_ani_path.append(output_path)
                        elif i > 1:
                            if j == 0:
                                walk_ani_0.append(texture)
                                walk_ani_0_path.append(output_path)
                            elif j == 1:
                                walk_ani_45.append(texture)
                                walk_ani_45_path.append(output_path)
                            elif j == 2:
                                walk_ani_90.append(texture)
                                walk_ani_90_path.append(output_path)
                            elif j == 3:
                                walk_ani_135.append(texture)
                                walk_ani_135_path.append(output_path)
                            elif j == 4:
                                walk_ani_180.append(texture)
                                walk_ani_180_path.append(output_path)
                            elif j == 5:
                                walk_ani_225.append(texture)
                                walk_ani_225_path.append(output_path)
                            elif j == 6:
                                walk_ani_270.append(texture)
                                walk_ani_270_path.append(output_path)
                            elif j == 7:
                                walk_ani_315.append(texture)
                                walk_ani_315_path.append(output_path)
                except:
                    loop = False
                
                j += 1

            y -= 65

        self.texture = walk_ani_0[0]

        # Reversed lists before returning values
        return walk_ani_0[::-1], walk_ani_0_path[::-1], walk_ani_45[::-1], walk_ani_45_path[::-1], walk_ani_90[::-1], walk_ani_90_path[::-1], walk_ani_135[::-1], walk_ani_135_path[::-1], walk_ani_180[::-1], walk_ani_180_path[::-1], walk_ani_225[::-1], walk_ani_225_path[::-1], walk_ani_270[::-1], walk_ani_270_path[::-1], walk_ani_315[::-1], walk_ani_315_path[::-1], shoot_ani, shoot_ani_path, death_ani, death_ani_path

    def update_texture(self, player_x, player_y):
        '''Updates the enemies texture based on a rotation, movement, and status.'''
         # Step 1: Calculate direction vector from enemy to player
        dx = player_x - self.x
        dy = player_y - self.y

        # Walking animation
        if self.is_walking:
            i = self.current_walk_frame
        else:
            i = 0

        # Step 2: Calculate angle from enemy to player
        angle_to_player = math.atan2(dy, dx)

        # Step 3: Calculate relative angle (difference between enemy rotation and angle_to_player)
        relative_angle = angle_to_player - self.rotation

        # Normalize relative_angle to range [0, 2π]
        relative_angle = (relative_angle + math.pi * 2) % (math.pi * 2)

        # Step 4: Determine which texture to use based on 45° segments
        if 0 <= relative_angle < math.pi / 8 or 15 * math.pi / 8 <= relative_angle < 2 * math.pi: # Correct
            # Front (0°)
            self.texture = self.walk_ani_0[i]
            self.texture_path = self.walk_ani_0_path[i]
        elif (9 * math.pi / 8) + (math.pi / 2) <= relative_angle < (11 * math.pi / 8) + (math.pi / 2): # Correct
            # Front-right (45°)
            self.texture = self.walk_ani_45[i]
            self.texture_path = self.walk_ani_45_path[i]
        elif 11 * math.pi / 8 <= relative_angle < 13 * math.pi / 8: # Correct
            # Right (90°)
            self.texture = self.walk_ani_90[i]
            self.texture_path = self.walk_ani_90_path[i]
        elif (5 * math.pi / 8) + (math.pi / 2) <= relative_angle < (7 * math.pi / 8) + (math.pi / 2): # Correct
            # Back-right (135°)
            self.texture = self.walk_ani_135[i]
            self.texture_path = self.walk_ani_135_path[i]
        elif 7 * math.pi / 8 <= relative_angle < 9 * math.pi / 8: # Correct
            # Back (180°)
            self.texture = self.walk_ani_180[i]
            self.texture_path = self.walk_ani_180_path[i]
        elif (math.pi / 8) + (math.pi / 2) <= relative_angle < (3 * math.pi / 8) + (math.pi / 2): # Correct
            # Back-left (225°)
            self.texture = self.walk_ani_225[i]
            self.texture_path = self.walk_ani_225_path[i]
        elif 3 * math.pi / 8 <= relative_angle < 5 * math.pi / 8: # Correct
            # Left (270°)
            self.texture = self.walk_ani_270[i]
            self.texture_path = self.walk_ani_270_path[i]
        else:
            # Front-left (315°)
            self.texture = self.walk_ani_315[i]
            self.texture_path = self.walk_ani_315_path[i]

        # Updates other animations
        if self.is_dying:
            self.texture = self.death_ani[self.current_death_frame]
            self.texture_path = self.death_ani_path[self.current_death_frame]

    def patrol(self, delta_time, player_x, player_y):
        """Move randomly to valid tiles unless the player is visible."""
        if self.is_dying:
            return

        if self.patrol_wait > 0:
            self.patrol_wait -= delta_time
            return

        # Check if the player is visible and within range
        dx = player_x - self.x
        dy = player_y - self.y

        distance_squared = dx ** 2 + dy ** 2

        # Increase visibility range (e.g., up to 5 tiles)
        if distance_squared <= math.pow(self.max_detect_distance, 2) and self.can_see(player_x, player_y):  # Adjusted from <= 9 to <= 25
            # Player is visible and within range; stop patrolling
            self.target_x = None
            self.target_y = None
            return  # Enemy stands still
    
        # Continue patrolling if the player is not visible
        self.patrol_timer -= delta_time
    
        if self.patrol_timer <= 0 or (self.target_x is None or self.target_y is None):
            # Reset patrol timer
            self.patrol_timer = random.uniform(1, 3)
    
            # Find a random valid tile within line of sight
            valid_tiles = []
            for dy in range(-5, 6):  # Adjust range for line of sight distance
                for dx in range(-5, 6):
                    target_x = int(self.x + dx)
                    target_y = int(self.y + dy)
                    if self.can_see(target_x, target_y) and mapData[target_y][target_x] == ' ':
                        valid_tiles.append((target_x + 0.5, target_y + 0.5))
    
            if valid_tiles:
                self.target_x, self.target_y = random.choice(valid_tiles)
    
        # Move towards target position if set
        if self.target_x is not None and self.target_y is not None:
            speed = 1 * delta_time  # Adjust speed as needed
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            # Update rotation for sprite
            self.rotation = math.atan2(dx, dy)

            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance > speed:
                self.x += (dx / distance) * speed
                self.y += (dy / distance) * speed
                self.is_walking = True
            else:
                # Reached target position
                self.x, self.y = self.target_x, self.target_y
                self.target_x, self.target_y = None, None
                self.is_walking = False
                self.patrol_wait = random.uniform(1, 3)

    def can_see(self, target_x, target_y):
        """Check if this sprite can see a given tile."""
        ray_x, ray_y = self.x, self.y
        dir_x = target_x - ray_x
        dir_y = target_y - ray_y
        distance = math.sqrt(dir_x ** 2 + dir_y ** 2)

        # Prevent division by zero
        if distance == 0:
            return True

        # Normalize direction vector
        dir_x /= distance
        dir_y /= distance

        max_distance = self.max_detect_distance  # Maximum visibility range in tiles (adjust as needed)
        traveled_distance = 0.0

        while traveled_distance < max_distance:
            # Step along the ray
            ray_x += dir_x * 0.1
            ray_y += dir_y * 0.1
            traveled_distance += 0.1

            # Convert to map grid coordinates
            map_x, map_y = int(ray_x), int(ray_y)

            # Check for out-of-bounds access
            if map_x < 0 or map_x >= len(mapData[0]) or map_y < 0 or map_y >= len(mapData):
                return False

            # Check if we've reached the target tile
            if int(ray_x) == int(target_x) and int(ray_y) == int(target_y):
                return True

            # Check for walls blocking the view
            if mapData[map_y][map_x] in ('█', '▓'):
                return False

        return False  # Target is out of maximum range or blocked by walls

    def shoot_at_player(self, delta_time, player):
        """Shoot at the player."""
        dx = player.player_x - self.x
        dy = player.player_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if self.is_dying:
            return

        # Increase shooting range (e.g., up to 5 tiles)
        if distance <= self.max_detect_distance:
            if self.can_see(player.player_x, player.player_y):
                if self.current_shoot_frame == 0: #When the enemy is not firing
                    self.texture = self.shoot_ani[0]
                    self.texture_path = self.shoot_ani_path[0]
                elif self.current_shoot_frame == 1:
                    self.texture = self.shoot_ani[1]
                    self.texture_path = self.shoot_ani_path[1]

                if self.shoot_timer >= self.no_fire_frame_duration and self.current_shoot_frame == 0:
                    arcade.play_sound(self.gun_shot, 0.7) # type: ignore

                    if random.uniform(0, 100) <= ((distance) / self.max_detect_distance) * 100:
                        upper_dam = 30 / (distance / self.max_detect_distance)
                        lower_dam = 10 / (distance / self.max_detect_distance)
                        player.hurt_player(random.uniform(lower_dam, upper_dam))

                    self.shoot_timer = 0
                    self.current_shoot_frame = 1
                elif self.shoot_timer >= self.fire_frame_duration and self.current_shoot_frame == 1:
                    self.shoot_timer = 0
                    self.current_shoot_frame = 0

                self.shoot_timer += delta_time
                return
        else:
            self.shoot_timer = 0

    def hurt_sprite(self, sprite, damage, player):
        """Remove a sprite when it is hit."""
        sprite.health -= damage

        if sprite.health <= 0 and not sprite.is_dying:
            # Start death animation
            sprite.is_dying = True
            sprite.current_death_frame = 0
            sprite.death_timer = 0
            random_death_sound = random.choice(self.death_sound)
            arcade.play_sound(random_death_sound, volume=1)
            player.max_health += 5
            player.health += 5
        elif sprite.health <= 0 and sprite.is_dying:
            random_gore_sound = random.choice(self.gore_sounds)
            arcade.play_sound(random_gore_sound, volume=1)
        else:
            random_gore_sound = random.choice(self.gore_sounds)
            random_scream_sound = random.choice(self.scream_sounds)
            arcade.play_sound(random_gore_sound, volume=1)
            arcade.play_sound(random_scream_sound, volume=1)

# Game class inheriting from arcade.Window
class GameLoop(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True, vsync=True) # type: ignore
        
        # Clear out texture Cache
        delete_all_files_in_directory(os.path.join(DIR, "Cache"))

        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT

        # Texture loading
        self.wall_texture = os.path.join(DIR, "Textures\\Surfaces\\wolf_bricks.png")
        self.door_closed_texture = os.path.join(DIR, "Textures\\Surfaces\\Door.png")
        self.door_open_texture = os.path.join(DIR, "Textures\\Surfaces\\Open_Door.png")
        self.floor_texture = os.path.join(DIR, "Textures\\Surfaces\\wolf_cobble_floor.png")
        self.ceiling_texture = os.path.join(DIR, "Textures\\Surfaces\\wolf_cobble_floor.png")
        
        # Sprite Texture Loading
        self.guard = os.path.join(DIR, "Textures\\Sprites\\Guard\\guard_sheet.png")

        # UI Texture Loading
        self.crosshair = os.path.join(DIR, "Textures\\UI\\crosshair.png")

        # Gun animation loading
        self.gun_animation_frames = load_animation(os.path.join(DIR, "Textures\\Guns\\Pistol"))
        self.current_frame_index = 0  # Track the current frame of the animation
        self.animation_timer = 0      # Timer to control frame rate
        self.animation_speed = 0.07   # Time (in seconds) between frames
        self.is_shooting = False      # Flag to indicate if the gun is animating

        # Audio Loading
        self.songs_folder_path = os.path.join(DIR, "Sounds\\Music")
        self.songs = self.get_music_files()
        random.shuffle(self.songs)  # Shuffle the song list randomly
        self.current_song_index = 0
        self.current_player = None

        # Footstep sounds
        self.footsteps_folder_path = os.path.join(DIR, "Sounds\\Player\\Footsteps")
        self.footstep_sounds = load_folder_sounds(self.footsteps_folder_path)
        self.last_footstep_time = 0  # To manage cooldown between footsteps
        self.footstep_cooldown = 0.4  # Minimum time between footsteps (in seconds)

        # Gun sounds
        self.gun_sounds = load_folder_sounds(os.path.join(DIR, "Sounds\\Player\\Gun"))

        # Gun atributes        
        # Gun position variables
        self.gun_x = SCREEN_WIDTH // 2
        self.gun_y = SCREEN_HEIGHT // 4  # Slightly lower than center for perspective
        
        # Bobbing effect variables
        self.bob_phase = 0  # Tracks the sine wave phase
        self.bob_amplitude = 5  # How much the gun moves up/down
        self.bob_speed = 5  # Speed of bobbing motion

        # Player attributes
        self.player_x, self.player_y = get_player_spawn(self) # type: ignore
        self.player_angle = 0
        self.player_rotate_speed = 2
        self.player_speed = 2
        
        # Movement flags
        self.move_up = False
        self.move_down = False
        self.move_left = False
        self.move_right = False

        # Camera turning flags (for arrow keys)
        self.turn_left = False
        self.turn_right = False

        # Initialize direction vector (player facing north by default)
        self.dir_x = 1.0
        self.dir_y = 0.0

        # Initialize camera plane (adjust for FOV)
        self.plane_x = 0.0
        self.plane_y = 0.66

        # Initialize ZBuffer as a list with length equal to screen width
        self.z_buffer = [float('inf')] * self.screen_width

        self.sprites = []
        self.sprite_count = 0

        # Create a list of sprites with their positions in the game world
        for y in range(len(mapData)):
            for x in range(len(mapData[0])):
                if mapData[y][x] == '$':
                    mapData[y] = mapData[y][:x] + ' ' + mapData[y][x+1:]
                    self.sprites.append(Sprite(x, y, 0, 0.3, 0.3, self.guard, health=100))

        # Player Stats
        self.health = 100
        self.max_health = 100
        self.ammo = 30
        self.stamia = 100

        # Screen effect variables
        self.health_vfx_indicator_time = .75
        self.health_vfx_indicator = 0

        self.last_time = time.time()  # Store the time of the last frame
        self.fps = 0  # Initialize FPS value
        self.frame_count = 0  # Track number of frames for averaging FPS
        self.fps_update_interval = 1.0  # Update FPS every second
        self.time_accumulator = 0.0  # Accumulate time for FPS update

    def on_update(self, delta_time):
        """Update game state."""
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

        # Update player position based on movement flags
        self.update_player_position(delta_time=delta_time)

        # Audio update
        self.play_next_song()

        # Check if player is moving
        is_moving = self.move_up or self.move_down or self. move_left or self.move_right

        # Play footstep sound if moving and cooldown has passed
        current_time = time.time()
        if is_moving and current_time - self.last_footstep_time > self.footstep_cooldown:
            self.play_random_footstep()
            self.last_footstep_time = current_time

        current_time = time.time()
        frame_time = current_time - self.last_time
        self.last_time = current_time

        # Bobs gun as player moves
        # Check if player is moving
        is_moving = self.move_up or self.move_down or self.move_left or self.move_right
        
        if is_moving:
            self.bob_phase += self.bob_speed * delta_time
            self.gun_y = (SCREEN_HEIGHT // 4) + math.sin(self.bob_phase) * self.bob_amplitude
            self.gun_x = (SCREEN_WIDTH // 2) + math.cos(self.bob_phase) * (self.bob_amplitude / 2)
        else:
            self.bob_phase = 0
            self.gun_y = SCREEN_HEIGHT // 4

        # Gun animation handler
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

        # Update enemy behavior
        for sprite in self.sprites:
            # Update death animation timer
            sprite.walk_timer += delta_time
            
            if sprite.walk_timer >= sprite.walk_frame_duration:
                if sprite.current_walk_frame + 2 >= len(sprite.walk_ani_0):
                    sprite.current_walk_frame = 1
                    sprite.walk_timer = 0
                else:
                    sprite.current_walk_frame += 1
                    sprite.walk_timer = 0
  
            if sprite.is_dying:
                # Update death animation timer
                sprite.death_timer += delta_time

                if (sprite.death_timer + sprite.death_frame_duration >= sprite.current_death_frame * sprite.death_frame_duration) and (sprite.current_death_frame + 1 < len(sprite.death_animation)):
                    sprite.current_death_frame += 1

                # Remove sprite once animation is complete
                if sprite.death_timer  >= (len(sprite.death_animation) * sprite.death_frame_duration) + 5:
                    self.sprites.remove(sprite)

            sprite.patrol(delta_time, self.player_x, self.player_y)
            # Check if the enemy should shoot at the player
            sprite.update_texture(player_x=self.player_x, player_y=self.player_y)
            sprite.shoot_at_player(delta_time, self)

        # Accumulate frame times and count frames
        self.time_accumulator += frame_time
        self.frame_count += 1

        # Update FPS every second (or based on your chosen interval)
        if self.time_accumulator >= self.fps_update_interval:
            self.fps = self.frame_count / self.time_accumulator  # Calculate average FPS
            self.frame_count = 0  # Reset frame count
            self.time_accumulator = 0.0  # Reset accumulator

        # Update screen effects
        if(self.health_vfx_indicator > 0):
            self.health_vfx_indicator -= delta_time

        # Heal over time
        if(self.health < self.max_health):
            self.health += 6.5 * delta_time

        # Rest of your game update logic...
        super().on_update(delta_time)  # Call parent class update if needed

    def on_draw(self):
        """Render the screen."""
        arcade.start_render()

        # Draws floor
        #self.draw_floor()
        arcade.draw_rectangle_filled(
            center_x=self.screen_width // 2,
            center_y=self.screen_height // 4,  
            width=self.screen_width,
            height=self.screen_height // 2,
            color=(120, 120, 120, 255)
        )
        
        # Ceiling
        arcade.draw_rectangle_filled(
            center_x=self.screen_width // 2,
            center_y=(3 * self.screen_height) // 4,  
            width=self.screen_width,
            height=self.screen_height // 2,
            color=(71, 71, 71, 255)
        )

        self.cast_rays()

        self.draw_sprites()

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
            center_x=SCREEN_WIDTH // 2,
            center_y=SCREEN_HEIGHT // 2,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            color=(255, 0, 0, int((self.health_vfx_indicator / self.health_vfx_indicator_time) * 100) + max(0, min((100 - self.health), 100)))
        )

        # Draw the map and player 
        #self.draw_map()
        #self.draw_grid()
        #arcade.draw_rectangle_filled((self.player_x * TILE_SIZE), self.screen_height - (self.player_y * TILE_SIZE), TILE_SIZE / 2, TILE_SIZE / 2, arcade.color.RED)

        # Draw FPS counter and general stats
        self.draw_stats()

        # Draws health
        arcade.draw_text(
            f'Health: {round(self.health)}',
            20,
            20,
            arcade.color.BLACK,
            20
        )

        # Draws the crosshair
        self.draw_crosshair()

    def on_key_press(self, key, modifiers):
        """Handle key press events."""
        if key == arcade.key.W:
            self.move_up = True
        elif key == arcade.key.S:
            self.move_down = True
        elif key == arcade.key.A:
            self.move_left = True
        elif key == arcade.key.D:
            self.move_right = True
        elif key == arcade.key.LEFT:  # Turn camera left
            self.turn_left = True
        elif key == arcade.key.RIGHT:  # Turn camera right
            self.turn_right = True
        elif key == arcade.key.E:  # Interact with objects
            self.interact()  # Call interaction function
        elif key == arcade.key.SPACE:  # Example: SPACE key for shooting
            self.shoot()

    def on_key_release(self, key, modifiers):
        """Handle key release events."""
        if key == arcade.key.W:
            self.move_up = False
        elif key == arcade.key.S:
            self.move_down = False
        elif key == arcade.key.A:
            self.move_left = False
        elif key == arcade.key.D:
            self.move_right = False
        elif key == arcade.key.LEFT:  # Stop turning left
            self.turn_left = False
        elif key == arcade.key.RIGHT:  # Stop turning right
            self.turn_right = False

    def cast_rays(self):
        """Cast rays from the player's position and render walls with correct depth."""

        # Starting angle for the first ray (leftmost ray in player's FOV)
        ray_angle = self.player_angle - FOV / 2

        self.z_buffer.clear()

        # Cast each ray
        for ray in range(NUM_RAYS):
            # Calculate direction of the current ray
            ray_dir_x = math.cos(ray_angle)
            ray_dir_y = math.sin(ray_angle)

            # Player's current position in grid units
            map_x = int(self.player_x)
            map_y = int(self.player_y)

            # Distance increments for each step along x and y axes
            delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else float('inf')
            delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else float('inf')

            # Calculate step direction and initial side distances
            if ray_dir_x < 0:
                step_x = -1
                side_dist_x = (self.player_x - map_x) * delta_dist_x
            else:
                step_x = 1
                side_dist_x = (map_x + 1.0 - self.player_x) * delta_dist_x

            if ray_dir_y < 0:
                step_y = -1
                side_dist_y = (self.player_y - map_y) * delta_dist_y
            else:
                step_y = 1
                side_dist_y = (map_y + 1.0 - self.player_y) * delta_dist_y

            # Perform DDA to find where the ray hits a wall
            hit = False
            while not hit:
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_dist_x
                    map_x += step_x
                    side = 0  # Hit was on an x-side (vertical wall)
                else:
                    side_dist_y += delta_dist_y
                    map_y += step_y
                    side = 1  # Hit was on a y-side (horizontal wall)

                if mapData[map_y][map_x] == '█' or mapData[map_y][map_x] == '▓':
                    hit = True

            # Calculate distance from player to wall using perpendicular distance correction
            epsilon = 0.0001

            epsilon = 1e-6
            inv_det = 1.0 / (self.plane_x * self.dir_y - self.dir_x * self.plane_y)

            if abs(inv_det) < epsilon:
                continue

            if side == 0:
                perp_wall_dist = max((map_x - self.player_x + (1 - step_x) / 2) / (ray_dir_x + epsilon), epsilon)
            else:
                perp_wall_dist = max((map_y - self.player_y + (1 - step_y) / 2) / (ray_dir_y + epsilon), epsilon)

            perp_wall_dist *= math.cos(ray_angle - self.player_angle)

            # Store this distance in ZBuffer for this column of pixels
            self.z_buffer.append(perp_wall_dist)

            line_height = int(self.screen_height / perp_wall_dist)

            draw_start = max(0, self.screen_height // 2 - line_height // 2)
            draw_end = min(self.screen_height, self.screen_height // 2 + line_height // 2)

            ray_screen_position = int(ray * self.screen_width / NUM_RAYS)

            if side == 0:
                wall_x = self.player_y + (map_x - self.player_x + (1 - step_x) / 2) / ray_dir_x * ray_dir_y
            else:
                wall_x = self.player_x + (map_y - self.player_y + (1 - step_y) / 2) / ray_dir_y * ray_dir_x 

            wall_x %= 1

            texture_path = ''

            if(mapData[map_y][map_x] == '█'):
                texture_path = self.wall_texture
            elif mapData[map_y][map_x] == '▓':
                texture_path = self.door_closed_texture
            elif mapData[map_y][map_x] == '░':
                texture_path = self.door_open_texture

            # Determine which part of texture to sample using wall hit position (wall_x)
            texture_width = arcade.load_texture(texture_path).width

            # Calculate which column of pixels corresponds to this part of the wall
            texture_column = int(wall_x * texture_width)

            # Ensure we don't exceed the bounds of the texture width
            if texture_column >= texture_width:
                texture_column = texture_width - 1

            # Load only a vertical slice of the texture using arcade.load_texture()
            texture_slice_arcade = arcade.load_texture(
                file_name=texture_path,
                x=texture_column,   # Start at this column in the texture
                y=0,                # Start at the top of the texture
                width=1,            # Only load one column width (slice)
                height=arcade.load_texture(texture_path).height   # Full height of the texture
            )

            arcade.draw_texture_rectangle(
                center_x=ray_screen_position,
                center_y=(draw_start + draw_end) // 2,
                width=self.screen_width / (NUM_RAYS / 1.05),   # Each slice corresponds to one column wide slice.
                height=line_height,
                texture=texture_slice_arcade,
                angle=0,
                alpha=255
            )

            ray_angle += FOV / NUM_RAYS

    def update_player_position(self, delta_time):
        """Update player position based on movement flags and camera rotation."""
        move_speed = min(self.player_speed / TILE_SIZE, TILE_SIZE / 10) * delta_time * 35 # Ensure small steps relative to tile size

        # Calculate direction vector based on player's current angle
        direction_x = math.cos(self.player_angle)
        direction_y = math.sin(self.player_angle)

        new_x = self.player_x
        new_y = self.player_y

        # Move forward (W key) or backward (S key) based on camera direction
        if self.move_up:  # Move forward
            new_x += direction_x * move_speed
            new_y += direction_y * move_speed
            if not self.check_collision(new_x * TILE_SIZE, new_y * TILE_SIZE):  # Only update if no collision detected
                self.player_x = new_x
                self.player_y = new_y

        if self.move_down:  # Move backward
            new_x -= direction_x * move_speed
            new_y -= direction_y * move_speed
            if not self.check_collision(new_x * TILE_SIZE, new_y * TILE_SIZE):  # Only update if no collision detected
                self.player_x = new_x
                self.player_y = new_y

        # Strafe left (A key) or right (D key)
        if self.move_left:  # Strafe left (perpendicular to view direction)
            strafe_x = math.cos(self.player_angle - math.pi / 2)
            strafe_y = math.sin(self.player_angle - math.pi / 2)
            new_x += strafe_x * move_speed
            new_y += strafe_y * move_speed
            if not self.check_collision(new_x * TILE_SIZE, new_y * TILE_SIZE):  # Only update if no collision detected
                self.player_x = new_x
                self.player_y = new_y

        if self.move_right:  # Strafe right (perpendicular to view direction)
            strafe_x = math.cos(self.player_angle + math.pi / 2)
            strafe_y = math.sin(self.player_angle + math.pi / 2)
            new_x += strafe_x * move_speed
            new_y += strafe_y * move_speed
            if not self.check_collision(new_x * TILE_SIZE, new_y * TILE_SIZE):  # Only update if no collision detected
                self.player_x = new_x
                self.player_y = new_y
    
    def draw_grid(self):
        # Define the grid size (matches TILE_SIZE)

        # Draw horizontal lines
        for x in range(self.screen_height, self.screen_height - (len(mapData) * TILE_SIZE), -TILE_SIZE):
            arcade.draw_line(0, x, len(mapData[0]) * TILE_SIZE, x, arcade.color.LIGHT_GRAY)

        # Draw vertical lines
        for y in range(0, len(mapData[0]) * TILE_SIZE, TILE_SIZE):
            arcade.draw_line(y, self.screen_height, y, self.screen_height - (len(mapData) * TILE_SIZE), arcade.color.LIGHT_GRAY)

    def draw_stats(self):
        """Draw FPS counter and general game stats in the top-right corner."""
        # Display FPS in top-right corner
        arcade.draw_text(
            f"FPS: {self.fps:.2f} \nPlayer X: {self.player_x:.2f} \nPlayer Y: {self.player_y:.2f} \nPlayer Rot: {(self.player_angle * (180 / math.pi)):.2f}º \nSprites on Screen: {(self.sprite_count)}", 
            10, 
            SCREEN_HEIGHT - 20, 
            arcade.color.BLACK
        )

    def draw_map(self):
        for row_index, row in enumerate(mapData):
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

    def draw_sprites(self):
        self.sprite_count = 0

        # Step 1: Sort sprites by distance from the player
        sprite_distances = []
        for sprite in self.sprites:
            # Calculate distance from player to each sprite (squared distance to avoid sqrt)
            dist = (sprite.x - self.player_x) ** 2 + (sprite.y - self.player_y) ** 2
            sprite_distances.append((sprite, dist))

        # Sort sprites by distance (farthest to nearest)
        sprite_distances.sort(key=lambda s: s[1], reverse=True)

        # Step 2: Loop through each sprite and project it onto the screen
        for sprite, _ in sprite_distances:
            try:
                # Translate sprite position relative to player
                sprite_x = sprite.x - self.player_x
                sprite_y = sprite.y - self.player_y

                # Apply camera transformation (inverse of camera matrix)
                inv_det = 1.0 / (self.plane_x * self.dir_y - self.dir_x * self.plane_y)
                transform_x = inv_det * (self.dir_y * sprite_x - self.dir_x * sprite_y)
                transform_y = inv_det * (-self.plane_y * sprite_x + self.plane_x * sprite_y)

                # Check if the sprite is in front of the player (transform_y > 0)
                if transform_y <= 0:
                    continue
                
                # Step 3: Project the sprite onto the screen
                sprite_screen_x = int((self.screen_width / 2) * (1 + transform_x / transform_y))

                # Calculate height and width of the sprite on screen
                sprite_height = abs(int(self.screen_height / transform_y))  # Correct scaling based on depth
                sprite_width = abs(int(self.screen_height / transform_y * (self.screen_width / self.screen_height)))

                # Calculate vertical start and end positions for drawing the sprite
                draw_start_y = max(0, self.screen_height // 2 - sprite_height // 2)
                draw_end_y = min(self.screen_height, self.screen_height // 2 + sprite_height // 2)

                # Calculate horizontal start and end positions for drawing the sprite
                draw_start_x = int(sprite_screen_x - (sprite_width / 2))
                draw_end_x = int(sprite_screen_x + (sprite_width / 2))

                # sprite.death_animation[sprite.current_death_frame]
                texture = sprite.texture
                texture_width = texture.width
                texture_height = texture.height

                self.sprite_count += 1

                # Step 4: Draw each vertical stripe of the sprite if it's closer than walls (using ZBuffer)
                for stripe in range(draw_start_x, draw_end_x):
                    # Only render if this part of the sprite is closer than any wall at this column
                    if stripe >= 0 and stripe < self.screen_width:
                        if transform_y > 0 and transform_y < self.z_buffer[round(stripe / (self.screen_width / NUM_RAYS))]:
                                # Calculate texture column (X-axis) for current vertical stripe of sprite
                                percent_across_sprite = (stripe - draw_start_x) / float(draw_end_x -    draw_start_x)
                                texture_column = int(percent_across_sprite * texture_width)

                                # Ensure we don't exceed bounds of texture width
                                if texture_column >= texture_width:
                                    texture_column = texture_width - 1
                                elif texture_column < 0:
                                    texture_column = 0

                                # Ensure we don't exceed bounds of texture width
                                if texture_column >= texture_width:
                                    texture_column = texture_width - 1
                                elif texture_column < 0:
                                    texture_column = 0

                                # Load only a vertical slice of the texture using arcade.load_texture()
                                texture_slice_arcade = arcade.load_texture(
                                    file_name=sprite.texture_path,
                                    x=texture_column,
                                    y=0,
                                    width=1,
                                    height=texture_height,
                                )

                                # Draw this slice of the texture on screen at this position
                                arcade.draw_texture_rectangle(
                                    center_x=stripe * (self.screen_width / NUM_RAYS) / 4,
                                    center_y=(draw_start_y + draw_end_y) // 2,
                                    width=1,
                                    height=sprite_height,
                                    texture=texture_slice_arcade,
                                    angle=0,
                                    alpha=255
                                )
            except:
                continue

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
        rayDirX0 = self.dir_x - self.plane_x
        rayDirY0 = self.dir_y - self.plane_y
        rayDirX1 = self.dir_x + self.plane_x
        rayDirY1 = self.dir_y + self.plane_y
    
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
            center_x=SCREEN_WIDTH // 2,
            center_y=SCREEN_HEIGHT // 2,
            width=crosshair_tex.width // 2,
            height=crosshair_tex.height // 2,
            texture=crosshair_tex
        )

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
            map_x = int(corner_x // TILE_SIZE)
            map_y = int(corner_y // TILE_SIZE)

            # Ensure we're not out of bounds
            if map_x < 0 or map_x >= len(mapData[0]) or map_y < 0 or map_y >= len(mapData):
                return True  # Treat out-of-bounds as a collision

            # Check if any corner is inside a wall ('█')
            if mapData[map_y][map_x] == '█' or mapData[map_y][map_x] == '▓':
                return True  # Collision detected

        return False  # No collision

    def interact(self):
        """Check if the player is facing an interactive object and trigger a callback."""

        # Calculate the direction vector based on player's current angle
        direction_x = math.cos(self.player_angle)
        direction_y = math.sin(self.player_angle)

        # Calculate the tile in front of the player
        front_x = int(self.player_x + direction_x)
        front_y = int(self.player_y + direction_y)

        # Check if the tile in front of the player is interactive (e.g., a door '░')
        if mapData[front_y][front_x] == '░' or mapData[front_y][front_x] == '▓':  # Example: Door tile
            self.interact_door(front_x, front_y)  # Trigger callback to open door

    def interact_door(self, x, y):
        """Open a door at position (x, y)."""
        if(mapData[y][x] == '░'): # Open
            mapData[y] = mapData[y][:x] + '▓' + mapData[y][x+1:]
        else:
            mapData[y] = mapData[y][:x] + '░' + mapData[y][x+1:]

    def shoot(self):
        """Cast a ray and check for wall or sprite collisions."""
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
        max_distance = MAX_DEPTH  # Limit how far the ray can   travel

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
            if mapData[map_y][map_x] == '█' or mapData[map_y]   [map_x] == '▓':
                hit_wall = True
                break

            # Check for sprite collision at this grid cell  during traversal
            for sprite in self.sprites:
                if int(sprite.x) == map_x and int(sprite.y) ==  map_y:
                    if not sprite.is_dying:
                        sprite.hurt_sprite(sprite, 25, self)
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

    def play_random_footstep(self):
        """Play a random footstep sound."""
        if self.footstep_sounds:
            random_sound = random.choice(self.footstep_sounds)
            arcade.play_sound(random_sound, volume=0.2)  #  Adjust volume as needed
   
    def play_gun_sound(self):
        """Play a random gun sound."""
        if self.gun_sounds:
            random_sound = random.choice(self.  gun_sounds)
            arcade.play_sound(random_sound, volume=0.5)  # Adjust volume as     needed

# Main function to start the game
def main():
    """Main function to set up and run the game."""
    game = GameLoop()
    arcade.run()

if __name__ == "__main__":
    main()