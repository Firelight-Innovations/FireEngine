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
        from FireEngine.player import player
        import arcade

        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT

        # Initialize ZBuffer as a list with length equal to screen width
        self.z_buffer = [float('inf')] * self.screen_width
        self.draw_list = arcade.SpriteList() # used for batching

        self.player = player.Player
        self.inv_det = 1.0 / (player.Player.plane_x * player.Player.dir_y - player.Player.dir_x * player.Player.plane_y)
        self.epsilon = 1e-6

    def draw_entities(self):
        from FireEngine.objects import entity
        from FireEngine.player import player
        import arcade
            
        entity.entity_count = 0
        # Step 1: Sort sprites by distance from the player
        entity_distances = []

        for ent in entity.entities:
                # Calculate distance from player to each sprite (squared distance to avoid sqrt)
                dist = (ent.x - player.Player.player_x) ** 2 + (ent.y - player.Player.player_y) ** 2
                entity_distances.append((ent, dist))

        # Sort sprites by distance (farthest to nearest)
        entity_distances.sort(key=lambda s: s[1], reverse=True)

        # Step 2: Loop through each sprite and project it onto the screen
        for enti, _ in entity_distances:
            # Translate sprite position relative to player
            entity_x = enti.x - player.Player.player_x
            entity_y = enti.y - player.Player.player_y

            # Apply camera transformation (inverse of camera matrix)
            inv_det = 1.0 / (player.Player.plane_x * player.Player.dir_y - player.Player.dir_x * player.Player.plane_y)
            transform_x = inv_det * (player.Player.dir_y * entity_x - player.Player.dir_x * entity_y)
            transform_y = inv_det * (-player.Player.plane_y * entity_x + player.Player.plane_x * entity_y)

            # Check if the sprite is in front of the player (transform_y > 0)
            if transform_y <= 0:
                    continue
            
            # Step 3: Project the sprite onto the screen
            entity_screen_x = int((self.screen_width / 2) * (1 + transform_x / transform_y))

            # Calculate height and width of the sprite on screen
            entity_height = abs(int(self.screen_height / transform_y))  # Correct scaling based on depth
            entity_width = abs(int(self.screen_height / transform_y * (self.screen_width / self.screen_height)))

            # Calculate vertical start and end positions for drawing the sprite
            draw_start_y = max(0, self.screen_height // 2 - entity_height // 2)
            draw_end_y = min(self.screen_height, self.screen_height // 2 + entity_height // 2)

            # Calculate horizontal start and end positions for drawing the sprite
            draw_start_x = int(entity_screen_x - (entity_width / 2))
            draw_end_x = int(entity_screen_x + (entity_width / 2))

            texture = enti.texture
            texture_width = texture.width
            texture_height = texture.height

            entity.entity_count += 1

            # Step 4: Draw each vertical stripe of the sprite if it's closer than walls (using ZBuffer)
            for stripe in range(draw_start_x, draw_end_x):
                # Only render if this part of the sprite is closer than any wall at this column
                if stripe >= 0 and stripe < self.screen_width:
                    if transform_y > 0 and transform_y < self.z_buffer[round(stripe / (self.screen_width / NUM_RAYS)) - 1]: # Fix the minus one issues, causing one coloum to not be rendered, causing visual bugs                           
                            # Calculate texture column (X-axis) for current vertical stripe of sprite
                            percent_across_sprite = (stripe - draw_start_x) / float(draw_end_x - draw_start_x)
                            texture_column = int(percent_across_sprite * texture_width)

                            # Ensure we don't exceed bounds of texture width
                            if texture_column >= texture_width:
                                texture_column = texture_width - 1
                            elif texture_column < 0:
                                texture_column = 0

                            # Load only a vertical slice of the texture using arcade.load_texture()
                            texture_slice_arcade = arcade.load_texture(
                                file_name=enti.texture_path,
                                x=texture_column,
                                y=0,
                                width=1,
                                height=texture_height,
                            )
                            
                            # Draw this slice of the texture on screen at this position
                            image = arcade.Sprite(
                                center_x=stripe * (self.screen_width / NUM_RAYS) / 4,
                                center_y=(draw_start_y + draw_end_y) // 2,
                                texture=texture_slice_arcade,
                            )

                            image.width = 1
                            image.height = entity_height
                            self.draw_list.append(image)

    def draw_sprirtes(self):
        from FireEngine.objects import sprite
        from FireEngine.player import player
        import arcade
            
        sprite.sprite_count = 0
        # Step 1: Sort sprites by distance from the player
        sprite_distances = []

        for spt in sprite.sprites:
                # Calculate distance from player to each sprite (squared distance to avoid sqrt)
                dist = (spt.x - player.Player.player_x) ** 2 + (spt.y - player.Player.player_y) ** 2
                sprite_distances.append((spt, dist))

        # Sort sprites by distance (farthest to nearest)
        sprite_distances.sort(key=lambda s: s[1], reverse=True)

        # Step 2: Loop through each sprite and project it onto the screen
        for spri, _ in sprite_distances:
            # Translate sprite position relative to player
            sprite_x = spri.x - player.Player.player_x
            sprite_y = spri.y - player.Player.player_y

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

            texture = spri.texture
            texture_width = texture.width
            texture_height = texture.height

            sprite.sprite_count += 1

            # Step 4: Draw each vertical stripe of the sprite if it's closer than walls (using ZBuffer)
            for stripe in range(draw_start_x, draw_end_x):
                # Only render if this part of the sprite is closer than any wall at this column
                if stripe >= 0 and stripe < self.screen_width:
                    if transform_y > 0 and transform_y < self.z_buffer[round(stripe / (self.screen_width / NUM_RAYS)) - 1]:
                            # Calculate texture column (X-axis) for current vertical stripe of sprite
                            percent_across_sprite = (stripe - draw_start_x) / float(draw_end_x - draw_start_x)
                            texture_column = int(percent_across_sprite * texture_width)

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
                            image = arcade.Sprite(
                                center_x=stripe * (self.screen_width / NUM_RAYS) / 4,
                                center_y=(draw_start_y + draw_end_y) // 2,
                                texture=texture_slice_arcade,
                            )

                            image.width = 1
                            image.height = sprite_height
                            self.draw_list.append(image)

    def draw_3d_objects(self):
        pass

    def draw_walls(self):
        """Cast rays from the player's position and render walls with correct depth."""
        from FireEngine.core import scene
        from FireEngine.player import player
        from FireEngine.core.resources import resource_loading
        import arcade

        # Starting angle for the first ray (leftmost ray in player's FOV)
        ray_angle = player.Player.player_angle - FOV / 2

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

                tile = scene.scene_data[map_y][map_x]
                        
                if tile != ' ':
                    hit = True

                for door in resource_loading.doors:
                    if not resource_loading.doors[door].render_open_door:
                        if tile == resource_loading.doors[door].open_icon:
                            hit = False

            # Calculate distance from player to wall using perpendicular distance correction
            if abs(self.inv_det) < self.epsilon:
                continue

            if side == 0:
                perp_wall_dist = max((map_x - player.Player.player_x + (1 - step_x) / 2) / (ray_dir_x + self.epsilon), self.epsilon)
            else:
                perp_wall_dist = max((map_y - player.Player.player_y + (1 - step_y) / 2) / (ray_dir_y + self.epsilon), self.epsilon)

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
                
            texture = ''

            # determine texture to render
            icon = scene.scene_data[map_y][map_x]

            for key in resource_loading.textures:
                if key == icon:
                    texture = resource_loading.textures[key].texture_path
                    break

            # determine which door texture to render
            if texture == '':
                for Door in resource_loading.doors:
                    if icon == resource_loading.doors[Door].close_icon:
                        texture = resource_loading.doors[Door].close_texture
                        door = Door
                        break
                    elif icon == resource_loading.doors[Door].open_icon:
                        texture = resource_loading.doors[Door].open_texture
                        door = Door
                        break

            if texture == '':
                texture = resource_loading.DefaultTexture

            # Determine which part of texture to sample using wall hit position (wall_x)
            loaded_texture = arcade.load_texture(texture)

            # Calculate which column of pixels corresponds to this part of the wall
            texture_column = int(wall_x * loaded_texture.width)

            # Ensure we don't exceed the bounds of the texture width
            if texture_column >= loaded_texture.width:
                texture_column = loaded_texture.width - 1
            
            # Load only a vertical slice of the texture using arcade.load_texture()
            texture_slice = arcade.load_texture(
                file_name = texture, 
                x = texture_column, 
                y = 0, 
                width = 1, 
                height = loaded_texture.height # Full height of the texture
            )

            # Render the cropped texture slice
            sprite = arcade.Sprite(
                center_x = ray_screen_position,
                center_y = (draw_start + draw_end) // 2,
                texture = texture_slice,
            )
            
            sprite.width = self.screen_width / (NUM_RAYS / 1.05)
            sprite.height = line_height

            self.draw_list.append(sprite)

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
        self.z_buffer.clear()

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
        
        # Clears batch cache
        self.draw_list.clear()
        self.draw_walls()
        self.draw_entities()
        self.draw_sprirtes()
        self.draw_3d_objects()

        # Renders batched objects
        self.draw_list.draw()

Render = render()