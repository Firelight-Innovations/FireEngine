import math
from FireEngine.core.decorators import singleton, register

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

RAYS_PER_100_PIXELS = 4
NUM_RAYS = 1000     # Number of rays casted for rendering

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

    def on_render(self):
        import arcade
        import arcade.gl
        self.priority = 0
        self.z_buffer.clear()
        
        # Clears batch cache
        self.draw_list.clear()
        self.draw_walls()

        # Renders batched objects
        self.draw_list.draw(filter=arcade.gl.NEAREST)

Render = render()