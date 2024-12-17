import os
import arcade
import sys
import math
from singleton import singleton

# Importing other scripts
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Code"))

# Importing assets 
DIR = os.path.join(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)), "Assets")

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

FOV = math.pi / 3 # Field of view (60 degrees)
NUM_RAYS = 200     # Number of rays casted for rendering

MAX_DEPTH = 30

@singleton
class render():
    def __init__(self, player_instance):

        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT

        # Initialize ZBuffer as a list with length equal to screen width
        self.z_buffer = [float('inf')] * self.screen_width

        self.player = player_instance

        # Texture loading
        self.wall_texture = os.path.join(DIR, "Textures\\Surfaces\\wolf_bricks.png")
        self.door_closed_texture = os.path.join(DIR, "Textures\\Surfaces\\Door.png")
        self.door_open_texture = os.path.join(DIR, "Textures\\Surfaces\\Open_Door.png")
        self.floor_texture = os.path.join(DIR, "Textures\\Surfaces\\wolf_cobble_floor.png")
        self.ceiling_texture = os.path.join(DIR, "Textures\\Surfaces\\wolf_cobble_floor.png")

    def draw_sprites(self):
        from Code import sprite
        import main
            
        sprite.sprite_count = 0
        # Step 1: Sort sprites by distance from the player
        sprite_distances = []

        for spr in sprite.sprites:
                # Calculate distance from player to each sprite (squared distance to avoid sqrt)
                dist = (spr.x - main.Player.player_x) ** 2 + (spr.y - main.Player.player_y) ** 2
                sprite_distances.append((spr, dist))

        # Sort sprites by distance (farthest to nearest)
        sprite_distances.sort(key=lambda s: s[1], reverse=True)

        # Step 2: Loop through each sprite and project it onto the screen
        for spri, _ in sprite_distances:
            try:
                # Translate sprite position relative to player
                sprite_x = spri.x - main.Player.player_x
                sprite_y = spri.y - main.Player.player_y

                # print(f'{main.Player.player_x}')

                # Apply camera transformation (inverse of camera matrix)
                inv_det = 1.0 / (main.Player.plane_x * main.Player.dir_y - main.Player.dir_x * main.Player.plane_y)
                transform_x = inv_det * (main.Player.dir_y * sprite_x - main.Player.dir_x * sprite_y)
                transform_y = inv_det * (-main.Player.plane_y * sprite_x + main.Player.plane_x * sprite_y)

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
                texture = spri.texture
                texture_width = texture.width
                texture_height = texture.height
                sprite.sprite_count += 1

                # Step 4: Draw each vertical stripe of the sprite if it's closer than walls (using ZBuffer)
                for stripe in range(draw_start_x, draw_end_x):

                    # Only render if this part of the sprite is closer than any wall at this column
                    if stripe >= 0 and stripe < self.screen_width:
                        if transform_y > 0 and transform_y < self.z_buffer[round(stripe / (self.screen_width / NUM_RAYS))]:
                                # Calculate texture column (X-axis) for current vertical stripe of sprite
                                percent_across_sprite = (stripe - draw_start_x) / float(draw_end_x - draw_start_x)
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
                                    file_name=spri.texture_path,
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

    def draw_walls(self):
        """Cast rays from the player's position and render walls with correct depth."""
        from Code import player
        from Code import scene
        import main

        # Starting angle for the first ray (leftmost ray in player's FOV)
        ray_angle = main.Player.player_angle - FOV / 2

        self.z_buffer.clear()

        # Cast each ray
        for ray in range(NUM_RAYS):
            # Calculate direction of the current ray
            ray_dir_x = math.cos(ray_angle)
            ray_dir_y = math.sin(ray_angle)

            # Player's current position in grid units
            map_x = int(main.Player.player_x)
            map_y = int(main.Player.player_y)

            # Distance increments for each step along x and y axes
            delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else float('inf')
            delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else float('inf')

            # Calculate step direction and initial side distances
            if ray_dir_x < 0:
                step_x = -1
                side_dist_x = (main.Player.player_x - map_x) * delta_dist_x
            else:
                step_x = 1
                side_dist_x = (map_x + 1.0 - main.Player.player_x) * delta_dist_x

            if ray_dir_y < 0:
                step_y = -1
                side_dist_y = (main.Player.player_y - map_y) * delta_dist_y
            else:
                step_y = 1
                side_dist_y = (map_y + 1.0 - main.Player.player_y) * delta_dist_y

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

                if scene.mapData[map_y][map_x] == '█' or scene.mapData[map_y][map_x] == '▓':
                    hit = True

            # Calculate distance from player to wall using perpendicular distance correction
            epsilon = 0.0001

            epsilon = 1e-6
            inv_det = 1.0 / (main.Player.plane_x * main.Player.dir_y - main.Player.dir_x * main.Player.plane_y)

            if abs(inv_det) < epsilon:
                continue

            if side == 0:
                perp_wall_dist = max((map_x - main.Player.player_x + (1 - step_x) / 2) / (ray_dir_x + epsilon), epsilon)
            else:
                perp_wall_dist = max((map_y - main.Player.player_y + (1 - step_y) / 2) / (ray_dir_y + epsilon), epsilon)

            perp_wall_dist *= math.cos(ray_angle - main.Player.player_angle)

            # Store this distance in ZBuffer for this column of pixels
            self.z_buffer.append(perp_wall_dist)

            line_height = int(self.screen_height / perp_wall_dist)

            draw_start = max(0, self.screen_height // 2 - line_height // 2)
            draw_end = min(self.screen_height, self.screen_height // 2 + line_height // 2)

            ray_screen_position = int(ray * self.screen_width / NUM_RAYS)

            if side == 0:
                wall_x = main.Player.player_y + (map_x - main.Player.player_x + (1 - step_x) / 2) / ray_dir_x * ray_dir_y
            else:
                wall_x = main.Player.player_x + (map_y - main.Player.player_y + (1 - step_y) / 2) / ray_dir_y * ray_dir_x 

            wall_x %= 1

            texture_path = ''

            if(scene.mapData[map_y][map_x] == '█'):
                texture_path = self.wall_texture
            elif scene.mapData[map_y][map_x] == '▓':
                texture_path = self.door_closed_texture
            elif scene.mapData[map_y][map_x] == '░':
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
    
    ########################
    #   Update functions   #
    ########################

    def on_render(self):
        import main
        #print(self.player.player_x)
        print(main.Player.player_x)
        self.draw_walls()
        self.draw_sprites()