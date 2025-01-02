import math
from FireEngine.core.decorators import singleton, register

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

RAYS_PER_100_PIXELS = 4
NUM_RAYS = 500     # Number of rays casted for rendering

MAX_DEPTH = 30

@singleton
@register
class render():
    def __init__(self):
        from FireEngine.player import player
        import arcade

        global SCREEN_WIDTH
        global SCREEN_HEIGHT

        SCREEN_WIDTH, SCREEN_HEIGHT = arcade.get_display_size()

        self.aspect_ratio = SCREEN_WIDTH / SCREEN_HEIGHT
        player.Player.FOV = player.Player.original_FOV * self.aspect_ratio

        # Initialize ZBuffer as a list with length equal to screen width
        self.z_buffer = [float('inf')] * SCREEN_WIDTH
        self.draw_list = arcade.SpriteList() # used for batching

        self.player = player.Player
        self.inv_det = 1.0 / (player.Player.plane_x * player.Player.dir_y - player.Player.dir_x * player.Player.plane_y)
        self.epsilon = 1e-6
        self.object_count = 0

    def draw_objects(self):
        from FireEngine.objects import entity
        from FireEngine.objects import sprite
        from FireEngine.objects import dropable
        from FireEngine.player import player
        import arcade
            
        self.object_count = 0

        # Step 1: Sort object by distance from the player
        object_distances = []
        objects = []

        objects = entity.entities + sprite.sprites + dropable.dropables

        for obj in objects:
            # Calculate distance from player to each sprite (squared distance to avoid sqrt)
            dist = (obj.x - player.Player.player_x) ** 2 + (obj.y - player.Player.player_y) ** 2
            object_distances.append((obj, dist))

        # Sort object by distance (farthest to nearest)
        object_distances.sort(key=lambda s: s[1], reverse=True)

        # Step 2: Loop through each object and project it onto the screen
        for objs, _ in object_distances:
            # Translate object position relative to player
            entity_x = objs.x - player.Player.player_x
            entity_y = objs.y - player.Player.player_y

            # Apply camera transformation (inverse of camera matrix)
            inv_det = 1.0 / (player.Player.plane_x * player.Player.dir_y - player.Player.dir_x * player.Player.plane_y)
            transform_x = inv_det * (player.Player.dir_y * entity_x - player.Player.dir_x * entity_y)
            perp_distance = inv_det * (-player.Player.plane_y * entity_x + player.Player.plane_x * entity_y)

            # Check if the object is in front of the player (perp_distance > 0)
            if perp_distance <= 0:
                    continue
            
            # Step 3: Project the object onto the screen
            entity_screen_x = int((SCREEN_WIDTH / 2) * (1 + transform_x / perp_distance))

            # Calculate height and width of the object on screen
            entity_height = abs(int(SCREEN_HEIGHT / perp_distance))  # Correct scaling based on depth

            # Calculate vertical start and end positions for drawing the object
            draw_start_y = max(0, SCREEN_HEIGHT // 2 - entity_height // 2)
            draw_end_y = min(SCREEN_HEIGHT, SCREEN_HEIGHT // 2 + entity_height // 2)

            # Calculate horizontal start and end positions for drawing the object
            draw_start_x = int(entity_screen_x - (entity_height / 2))
            draw_end_x = int(entity_screen_x + (entity_height / 2))

            texture = objs.texture
            texture_width = texture.width
            texture_height = texture.height

            self.object_count += 1

            '''
            if not abs(draw_start_x) <= 2 * SCREEN_WIDTH and not abs(draw_start_x) <= -2 * SCREEN_WIDTH:
                return
            
            if not abs(draw_end_x) <= 2 * SCREEN_WIDTH and not abs(draw_end_x) <= -2 * SCREEN_WIDTH:
                return
            '''
                
            draw_start_x = int(draw_start_x / (SCREEN_WIDTH / NUM_RAYS))
            draw_end_x = int(draw_end_x / (SCREEN_WIDTH / NUM_RAYS))

            # Step 4: Draw each vertical stripe of the object if it's closer than walls (using ZBuffer)
            for stripe in range(draw_start_x, draw_end_x):
                # Only render if this part of the object is closer than any wall at this column
                if stripe >= 0 and stripe < (SCREEN_WIDTH + (SCREEN_WIDTH / NUM_RAYS)) / (SCREEN_WIDTH / NUM_RAYS):
                    if perp_distance > 0 and perp_distance < self.z_buffer[round(stripe)]: # Fix the minus one issues, causing one coloum to not be rendered, causing visual bugs                           
                        # Calculate texture column (X-axis) for current vertical stripe of object
                        percent_across_sprite = (stripe - draw_start_x) / float(draw_end_x - draw_start_x)
                        texture_column = int(percent_across_sprite * texture_width)

                        # Ensure we don't exceed bounds of texture width
                        if texture_column >= texture_width:
                            texture_column = texture_width - 1
                        elif texture_column < 0:
                            texture_column = 0

                        # Load only a vertical slice of the texture using arcade.load_texture()
                        texture_slice = arcade.load_texture(
                            file_name=objs.texture_path,
                            x=texture_column,
                            y=0,
                            width=1,
                            height=texture_height,
                        )

                        # Draw this slice of the texture on screen at this position
                        image = arcade.Sprite(
                            center_x=stripe * SCREEN_WIDTH / NUM_RAYS,
                            center_y=(draw_start_y + draw_end_y) // 2,
                            texture=texture_slice,
                        )
                        
                        image.width = SCREEN_WIDTH / NUM_RAYS
                        image.height = entity_height
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
        ray_angle = player.Player.player_angle - player.Player.FOV / 2

        # Cast each ray
        for ray in range(NUM_RAYS + 1):
            # Calculate direction of the current ray
            # From -1 -> 1
            mapped_value = (ray - 0) * (1 - -1) / ((NUM_RAYS + 1) - 0) + -1
            ray_dir_x = player.Player.dir_x + player.Player.plane_x * mapped_value
            ray_dir_y = player.Player.dir_y + player.Player.plane_y * mapped_value

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
                perp_wall_dist = side_dist_x - delta_dist_x
            else:
                perp_wall_dist = side_dist_y - delta_dist_y

            #perp_wall_dist *= math.cos(ray_angle - player.Player.player_angle)

            # Store this distance in ZBuffer for this column of pixels
            self.z_buffer.append(perp_wall_dist)

            line_height = int(SCREEN_HEIGHT / perp_wall_dist)

            draw_start = max(0, SCREEN_HEIGHT // 2 - line_height // 2)
            draw_end = min(SCREEN_HEIGHT, SCREEN_HEIGHT // 2 + line_height // 2)

            ray_screen_position = int(ray * SCREEN_WIDTH / NUM_RAYS)

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
            
            sprite.width = SCREEN_WIDTH / NUM_RAYS + 1
            sprite.height = line_height

            self.draw_list.append(sprite)

            ray_angle += player.Player.FOV / NUM_RAYS

        self.z_buffer.append(0)

    def draw_floor_and_ceiling(self):
        """Render textured floor using a raycasting-like approach."""
        import arcade
        import math
        from PIL import Image
        from FireEngine.player import player

        # posZ is how high the camera is above the "floor"
        posZ = 0.5 * SCREEN_HEIGHT

        # Precompute left & right ray directions
        rayDirX0 = player.Player.dir_x - player.Player.plane_x
        rayDirY0 = player.Player.dir_y - player.Player.plane_y
        rayDirX1 = player.Player.dir_x + player.Player.plane_x
        rayDirY1 = player.Player.dir_y + player.Player.plane_y

        # Load your floor and ceiling textures
        floor_tex = arcade.load_texture("C:\\Users\\bjsea\\Documents\\Projects\\FireEngine\\Game\\Assets\\Textures\\Surfaces\\dirt.jpg")
        ceil_tex = arcade.load_texture("C:\\Users\\bjsea\\Documents\\Projects\\FireEngine\\Game\\Assets\\Textures\\Surfaces\\cobble_stone.png")

        # Create a Pillow image for manual pixel drawing
        floor_render = Image.new("RGBA", (SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0, 255))
        pixels = floor_render.load()

        # For each row in the screen
        for y in range(SCREEN_HEIGHT):
            # p is the distance from the center/horizon
            p = (y - (SCREEN_HEIGHT // 2))

            # Avoid division by zero
            if p == 0:
                p = 0.000001

            # rowDistance decides how far we are in the world
            rowDistance = posZ / p

            # X,Y ceil/floor step increments
            floorStepX = rowDistance * (rayDirX1 - rayDirX0) / SCREEN_WIDTH
            floorStepY = rowDistance * (rayDirY1 - rayDirY0) / SCREEN_WIDTH

            # Compute starting floorX/floorY
            floorX = player.Player.player_x + rowDistance * rayDirX0
            floorY = player.Player.player_y + rowDistance * rayDirY0

            # Loop through each screen column
            for x in range(SCREEN_WIDTH):
                # Determine the map tile
                cellX = int(floorX)
                cellY = int(floorY)

                # Fractional parts for the texture
                tx = int((floorX - cellX) * floor_tex.width) % floor_tex.width
                ty = int((floorY - cellY) * floor_tex.height) % floor_tex.height

                # Sample floor pixel
                floor_color = floor_tex.image.getpixel((tx, ty))

                # Same for ceiling (flip the row if you want symmetrical)
                ceil_color = ceil_tex.image.getpixel((tx, ty))

                pixels[x, y] = floor_color  # Draw floor
                # Optionally draw ceiling on the symmetrical row:
                # top_y = screen_height - y - 1
                # pixels[x, top_y] = ceil_color

                # Increment floorX/floorY for next column
                floorX += floorStepX
                floorY += floorStepY

        # Convert the Pillow image into an Arcade texture and draw it
        arcade_texture = arcade.Texture(name="floor_render", image=floor_render)
        arcade.draw_texture_rectangle(
            center_x=SCREEN_WIDTH // 2,
            center_y=SCREEN_HEIGHT // 2,
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            texture=arcade_texture,
        )

    ########################
    #   Update functions   #
    ########################

    def on_update(self, delta_time):
        import arcade
        from FireEngine.player import player
        
        global SCREEN_WIDTH, SCREEN_HEIGHT
        SCREEN_WIDTH, SCREEN_HEIGHT = arcade.get_window().get_size()
        player.Player.FOV = math.pi / 3

        self.aspect_ratio = SCREEN_WIDTH / SCREEN_HEIGHT

        # Recalculate FOV or other parameters if necessary
        player.Player.FOV = player.Player.original_FOV * self.aspect_ratio

        # Update camera plane based on new angle
        # This keeps the FOV constant while rotating
        player.Player.plane_x = -player.Player.FOV * math.sin(player.Player.player_angle)  # Adjust -0.66 for FOV scaling
        player.Player.plane_y = player.Player.FOV * math.cos(player.Player.player_angle)

        # Update direction vector based on new angle
        player.Player.dir_x = math.cos(player.Player.player_angle)
        player.Player.dir_y = math.sin(player.Player.player_angle)

    def on_render(self):
        import arcade
        import arcade.gl
        self.priority = 0
        self.z_buffer.clear()

        '''
        # Draws floor
        arcade.draw_rectangle_filled(
            center_x=SCREEN_WIDTH // 2,
            center_y=SCREEN_HEIGHT // 4,  
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT // 2,
            color=(120, 120, 120, 255)
        )
        
        # Ceiling
        arcade.draw_rectangle_filled(
            center_x=SCREEN_WIDTH // 2,
            center_y=(3 * SCREEN_HEIGHT) // 4,  
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT // 2,
            color=(71, 71, 71, 255)
        )
        '''

        # Clears batch cache
        self.draw_list.clear()
        self.draw_walls()
        self.draw_floor_and_ceiling()
        self.draw_objects()

        # Renders batched objects
        self.draw_list.draw(filter=arcade.gl.NEAREST)

Render = render()