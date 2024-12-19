import os
import math
from FireEngine.core.decorators import singleton
from FireEngine.core.decorators import register

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

FOV = math.pi / 3 # Field of view (60 degrees)
NUM_RAYS = 200     # Number of rays casted for rendering

MAX_DEPTH = 30

@singleton
@register
class render():
    def __init__(self):
        from FireEngine.core.resources import resource_loading
        from FireEngine.player import player

        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT

        # Initialize ZBuffer as a list with length equal to screen width
        self.z_buffer = [float('inf')] * self.screen_width

        self.player = player.Player

        # Texture loading
        self.wall_texture = os.path.join(resource_loading.Assets, "Textures\\Surfaces\\wolf_bricks.png")
        self.door_closed_texture = os.path.join(resource_loading.Assets, "Textures\\Surfaces\\Door.png")
        self.door_open_texture = os.path.join(resource_loading.Assets, "Textures\\Surfaces\\Open_Door.png")
        self.floor_texture = os.path.join(resource_loading.Assets, "Textures\\Surfaces\\wolf_cobble_floor.png")
        self.ceiling_texture = os.path.join(resource_loading.Assets, "Textures\\Surfaces\\wolf_cobble_floor.png")

    def draw_sprites(self):
        from FireEngine.objects import entity
        from FireEngine.player import player
        import main
        import arcade
            
        entity.sprite_count = 0
        # Step 1: Sort sprites by distance from the player
        sprite_distances = []

        for spr in entity.sprites:
                # Calculate distance from player to each sprite (squared distance to avoid sqrt)
                dist = (spr.x - player.Player.player_x) ** 2 + (spr.y - player.Player.player_y) ** 2
                sprite_distances.append((spr, dist))

        # Sort sprites by distance (farthest to nearest)
        sprite_distances.sort(key=lambda s: s[1], reverse=True)

        # Step 2: Loop through each sprite and project it onto the screen
        for spri, _ in sprite_distances:
            try:
                # Translate sprite position relative to player
                sprite_x = spri.x - player.Player.player_x
                sprite_y = spri.y - player.Player.player_y

                # print(f'{main.Player.player_x}')

                # Apply camera transformation (inverse of camera matrix)
                inv_det = 1.0 / (player.Player.plane_x * player.Player.dir_y - player.Player.dir_x * player.Player.plane_y)
                transform_x = inv_det * (player.Player.dir_y * sprite_x - player.Player.dir_x * sprite_y)
                transform_y = inv_det * (-player.Player.plane_y * sprite_x + player.Player.plane_x * sprite_y)

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
                entity.sprite_count += 1

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
        from FireEngine.core import scene
        from FireEngine.player import player
        import main
        import arcade

        # Starting angle for the first ray (leftmost ray in player's FOV)
        ray_angle = player.Player.player_angle - FOV / 2

        self.z_buffer.clear()

        # Cast each ray
        for ray in range(NUM_RAYS):
            # Calculate direction of the current ray
            ray_dir_x = math.cos(ray_angle)
            ray_dir_y = math.sin(ray_angle)

            # Player's current position in grid units
            map_x = int(player.Player.player_x)
            map_y = int(player.Player.player_y)

            # Distance increments for each step along x and y axes
            delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else float('inf')
            delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else float('inf')

            # Calculate step direction and initial side distances
            if ray_dir_x < 0:
                step_x = -1
                side_dist_x = (player.Player.player_x - map_x) * delta_dist_x
            else:
                step_x = 1
                side_dist_x = (map_x + 1.0 - player.Player.player_x) * delta_dist_x

            if ray_dir_y < 0:
                step_y = -1
                side_dist_y = (player.Player.player_y - map_y) * delta_dist_y
            else:
                step_y = 1
                side_dist_y = (map_y + 1.0 - player.Player.player_y) * delta_dist_y

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
            inv_det = 1.0 / (player.Player.plane_x * player.Player.dir_y - player.Player.dir_x * player.Player.plane_y)

            if abs(inv_det) < epsilon:
                continue

            if side == 0:
                perp_wall_dist = max((map_x - player.Player.player_x + (1 - step_x) / 2) / (ray_dir_x + epsilon), epsilon)
            else:
                perp_wall_dist = max((map_y - player.Player.player_y + (1 - step_y) / 2) / (ray_dir_y + epsilon), epsilon)

            perp_wall_dist *= math.cos(ray_angle - player.Player.player_angle)

            # Store this distance in ZBuffer for this column of pixels
            self.z_buffer.append(perp_wall_dist)

            line_height = int(self.screen_height / perp_wall_dist)

            draw_start = max(0, self.screen_height // 2 - line_height // 2)
            draw_end = min(self.screen_height, self.screen_height // 2 + line_height // 2)

            ray_screen_position = int(ray * self.screen_width / NUM_RAYS)

            if side == 0:
                wall_x = player.Player.player_y + (map_x - player.Player.player_x + (1 - step_x) / 2) / ray_dir_x * ray_dir_y
            else:
                wall_x = player.Player.player_x + (map_y - player.Player.player_y + (1 - step_y) / 2) / ray_dir_y * ray_dir_x 

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
    
    def draw_floor(self):
        """Render textured floor using a raycasting-like approach."""
        import main
        import arcade
        from tkinter import Image

        # Load floor texture from disk
        floor_tex = arcade.load_texture(self.floor_texture)
        texture_image = floor_tex.image  # Get the Pillow image     object of the texture
        texture_width, texture_height = floor_tex.width,    floor_tex.height
    
        # Create an empty image object for rendering the floor
        floor_render = Image.new("RGBA", (SCREEN_WIDTH,     SCREEN_HEIGHT), (0, 0, 0, 255))
        pixels = floor_render.load()  # Access pixel data for   manipulation
    
        # Precompute direction vectors for leftmost and     rightmost rays
        rayDirX0 = main.Player.dir_x - main.Player.plane_x
        rayDirY0 = main.Player.dir_y - main.Player.plane_y
        rayDirX1 = main.Player.dir_x + main.Player.plane_x
        rayDirY1 = main.Player.dir_y + main.Player.plane_y
    
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
            floorX = main.Player.player_x + rowDistance * rayDirX0
            floorY = main.Player.player_y + rowDistance * rayDirY0
    
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

    ########################
    #   Update functions   #
    ########################

    def on_render(self):
        import arcade

        self.priority = 0

        # Draws floor
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

        self.draw_walls()
        self.draw_sprites()

Render = render()