# Line 39 of texture_atlas.py
# TEXCOORD_BUFFER_SIZE = 8192 * 2 * 2
# Game is crashing from to small of a buffer size
# Need better solution, temp fix however

import math
from FireEngine.core.decorators import singleton, register

SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600

RAYS_PER_100_PIXELS: int = 4
NUM_RAYS:int = 250     # Number of rays casted for rendering

MAX_DEPTH: int = 30

@singleton
@register
class Renderer:
    """
    Handles rendering of 3D objects and walls in the game.
    """

    def __init__(self) -> None:
        """
        Initializes the renderer with necessary attributes.
        
        :return: None
        """
        from FireEngine.player import player
        from FireEngine.core import manager
        import arcade

        global SCREEN_WIDTH
        global SCREEN_HEIGHT

        SCREEN_WIDTH, SCREEN_HEIGHT = arcade.get_display_size()

        self.aspect_ratio: float = SCREEN_WIDTH / SCREEN_HEIGHT
        player.Player.FOV = player.Player.original_FOV * self.aspect_ratio

        # Initialize ZBuffer as a list with length equal to screen width
        self.z_buffer: list[float] = [float('inf')] * SCREEN_WIDTH
        self.draw_list: arcade.SpriteList = arcade.SpriteList(use_spatial_hash=True, is_static=False, capacity=100000) # used for batching

        self.player = player.Player
        self.inv_det: float = 1.0 / (player.Player.plane_x * player.Player.dir_y - player.Player.dir_x * player.Player.plane_y)
        self.epsilon: float = 1e-6
        self.object_count: int = 0

    def draw_objects(self) -> None:
        """
        Draws 3D objects in the game world.
        
        :return: None
        """
        from FireEngine.objects import entity
        from FireEngine.objects import sprite
        from FireEngine.objects import dropable
        from FireEngine.player import player
        import arcade
            
        self.object_count = 0

        # Step 1: Sort objects by distance from the player
        object_distances: list[tuple[object, float]] = []
        objects: list[object] = []

        objects = entity.entities + sprite.sprites + dropable.dropables

        for obj in objects:
            # Calculate distance from player to each sprite (squared distance to avoid sqrt)
            dist: float = (obj.x - player.Player.player_x) ** 2 + (obj.y - player.Player.player_y) ** 2
            object_distances.append((obj, dist))

        # Sort objects by distance (farthest to nearest)
        object_distances.sort(key=lambda s: s[1], reverse=True)

        # Step 2: Loop through each object and project it onto the screen
        for objs, _ in object_distances:
            # Translate object position relative to player
            entity_x: float = objs.x - player.Player.player_x
            entity_y: float = objs.y - player.Player.player_y

            # Apply camera transformation (inverse of camera matrix)
            inv_det: float = 1.0 / (player.Player.plane_x * player.Player.dir_y - player.Player.dir_x * player.Player.plane_y)
            transform_x: float = inv_det * (player.Player.dir_y * entity_x - player.Player.dir_x * entity_y)
            perp_distance: float = inv_det * (-player.Player.plane_y * entity_x + player.Player.plane_x * entity_y)

            # Check if the object is in front of the player (perp_distance > 0)
            if perp_distance <= 0:
                continue
            
            # Step 3: Project the object onto the screen
            entity_screen_x: int = int((SCREEN_WIDTH / 2) * (1 + transform_x / perp_distance))

            # Calculate height and width of the object on screen
            entity_height: int = abs(int(SCREEN_HEIGHT / perp_distance))  # Correct scaling based on depth

            # Calculate vertical start and end positions for drawing the object
            draw_start_y: int = max(0, SCREEN_HEIGHT // 2 - entity_height // 2)
            draw_end_y: int = min(SCREEN_HEIGHT, SCREEN_HEIGHT // 2 + entity_height // 2)

            # Calculate horizontal start and end positions for drawing the object
            draw_start_x: int = int(entity_screen_x - (entity_height / 2))
            draw_end_x: int = int(entity_screen_x + (entity_height / 2))

            texture = objs.texture
            texture_width: int = texture.width
            texture_height: int = texture.height

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
                    if perp_distance > 0 and perp_distance < self.z_buffer[round(stripe)]:
                        # Calculate texture column (X-axis) for current vertical stripe of object
                        percent_across_sprite: float = (stripe - draw_start_x) / float(draw_end_x - draw_start_x)
                        texture_column: int = int(percent_across_sprite * texture_width)
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

    def draw_3d_objects(self) -> None:
        """
        Currently not implemented.
        
        :return: None
        """
        pass

    def draw_walls(self) -> None:
        """
        Casts rays from the player's position and renders walls with correct depth.
        
        :return: None
        """
        from FireEngine.core import scene
        from FireEngine.player import player
        from FireEngine.core.resources import resource_loading
        import arcade

        # Starting angle for the first ray (leftmost ray in player's FOV)
        ray_angle: float = player.Player.player_angle - player.Player.FOV / 2

        # Cast each ray
        for ray in range(NUM_RAYS + 1):
            # Calculate direction of the current ray
            # From -1 -> 1
            mapped_value: float = (ray - 0) * (1 - -1) / ((NUM_RAYS + 1) - 0) + -1
            ray_dir_x: float = player.Player.dir_x + player.Player.plane_x * mapped_value
            ray_dir_y: float = player.Player.dir_y + player.Player.plane_y * mapped_value

            # Player's current position in grid units
            map_x: int = int(player.Player.player_x)
            map_y: int = int(player.Player.player_y)

            # Distance increments for each step along x and y axes
            delta_dist_x: float = abs(1 / ray_dir_x) if ray_dir_x != 0 else float('inf')
            delta_dist_y: float = abs(1 / ray_dir_y) if ray_dir_y != 0 else float('inf')

            # Calculate step direction and initial side distances
            if ray_dir_x < 0:
                step_x: int = -1
                side_dist_x: float = (player.Player.player_x - map_x) * delta_dist_x
            else:
                step_x: int = 1
                side_dist_x: float = (map_x + 1.0 - player.Player.player_x) * delta_dist_x

            if ray_dir_y < 0:
                step_y: int = -1
                side_dist_y: float = (player.Player.player_y - map_y) * delta_dist_y
            else:
                step_y: int = 1
                side_dist_y: float = (map_y + 1.0 - player.Player.player_y) * delta_dist_y

            # Perform DDA to find where the ray hits a wall
            hit: bool = False
            while not hit:
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_dist_x
                    map_x += step_x
                    side: int = 0  # Hit was on an x-side (vertical wall)
                else:
                    side_dist_y += delta_dist_y
                    map_y += step_y
                    side: int = 1  # Hit was on a y-side (horizontal wall)

                tile: str = scene.scene_data[map_y][map_x]
                        
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
                perp_wall_dist: float = side_dist_x - delta_dist_x
            else:
                perp_wall_dist: float = side_dist_y - delta_dist_y

            #perp_wall_dist *= math.cos(ray_angle - player.Player.player_angle)

            # Store this distance in ZBuffer for this column of pixels
            self.z_buffer.append(perp_wall_dist)

            line_height: int = int(SCREEN_HEIGHT / perp_wall_dist)

            draw_start: int = max(0, SCREEN_HEIGHT // 2 - line_height // 2)
            draw_end: int = min(SCREEN_HEIGHT, SCREEN_HEIGHT // 2 + line_height // 2)

            ray_screen_position: int = int(ray * SCREEN_WIDTH / NUM_RAYS)
            if side == 0:
                wall_x: float = player.Player.player_y + (map_x - player.Player.player_x + (1 - step_x) / 2) / ray_dir_x * ray_dir_y
            else:
                wall_x: float = player.Player.player_x + (map_y - player.Player.player_y + (1 - step_y) / 2) / ray_dir_y * ray_dir_x 

            wall_x %= 1
                
            texture_path: str = ''

            # Determine texture to render
            icon: str = scene.scene_data[map_y][map_x]

            for key in resource_loading.textures:
                if key == icon:
                    texture_path = resource_loading.textures[key].texture_path
                    break

            # Determine which door texture to render
            if texture_path == '':
                for Door in resource_loading.doors:
                    if icon == resource_loading.doors[Door].close_icon:
                        texture_path = resource_loading.doors[Door].close_texture
                        door = Door
                        break
                    elif icon == resource_loading.doors[Door].open_icon:
                        texture_path = resource_loading.doors[Door].open_texture
                        door = Door
                        break

            if texture_path == '':
                texture_path = resource_loading.DefaultTexture

            # Determine which part of texture to sample using wall hit position (wall_x)
            loaded_texture = arcade.load_texture(texture_path)

            # Calculate which column of pixels corresponds to this part of the wall
            texture_column: int = int(wall_x * loaded_texture.width)

            # Ensure we don't exceed the bounds of the texture width
            if texture_column >= loaded_texture.width:
                texture_column = loaded_texture.width - 1
            
            # Load only a vertical slice of the texture using arcade.load_texture()
            texture_slice = arcade.load_texture(
                file_name=texture_path, 
                x=texture_column, 
                y=0, 
                width=1, 
                height=loaded_texture.height # Full height of the texture
            )

            # Render the cropped texture slice
            sprite = arcade.Sprite(
                center_x=ray_screen_position,
                center_y=(draw_start + draw_end) // 2,
                texture=texture_slice,
            )
            
            sprite.width = SCREEN_WIDTH / NUM_RAYS + 1
            sprite.height = line_height

            self.draw_list.append(sprite)

            ray_angle += player.Player.FOV / NUM_RAYS

        self.z_buffer.append(0)

    def load_shaders(self) -> None:
        """
        Loads shaders for rendering floor and ceiling.
        
        :return: None
        """
        import arcade
        from FireEngine.core import manager

        def load_shader(vertex_path: str, fragment_path: str) -> arcade.gl.Program:
            """
            Loads a shader program from vertex and fragment files.
            
            :param vertex_path: Path to the vertex shader file.
            :param fragment_path: Path to the fragment shader file.
            :return: The loaded shader program.
            """
            if arcade.Window.ctx:
                with open(vertex_path, 'r') as f:
                    vertex_shader: str = f.read()
                with open(fragment_path, 'r') as f:
                    fragment_shader: str = f.read()

                shader_program = manager.game_loop.ctx.program(
                    vertex_shader=vertex_shader,
                    fragment_shader=fragment_shader
                )

                return shader_program
            
        # Load textures (as you do in your existing code)
        self.floor_tex = arcade.load_texture("C:\\Users\\bjsea\\Documents\\Projects\\FireEngine\\Game\\Assets\\Textures\\Surfaces\\floor.jpg")
        self.ceil_tex = arcade.load_texture("C:\\Users\\bjsea\\Documents\\Projects\\FireEngine\\Game\\Assets\\Textures\\Surfaces\\ceiling.png")
        self.floor_shader = load_shader('C:\\Users\\bjsea\\Documents\\Projects\\FireEngine\\FireEngine\\core\\rendering\\viewport.vert', 'C:\\Users\\bjsea\\Documents\\Projects\\FireEngine\\FireEngine\\core\\rendering\\floor.frag')
        self.ceiling_shader = load_shader('C:\\Users\\bjsea\\Documents\\Projects\\FireEngine\\FireEngine\\core\\rendering\\viewport.vert',  'C:\\Users\\bjsea\\Documents\\Projects\\FireEngine\\FireEngine\\core\\rendering\\ceiling.frag')

        # Create textures and FBOs
        floor_tex_data = self.floor_tex.image.convert("RGBA").tobytes("raw", "RGBA", 0, -1)
        ceil_tex_data = self.ceil_tex.image.convert("RGBA").tobytes("raw", "RGBA", 0, -1)

        # Create Arcade GL textures using the manager.game_loop.ctx
        self.tex_0 = manager.game_loop.ctx.texture(
            size=(self.floor_tex.width, self.floor_tex.height),
            data=floor_tex_data,
            components=4,              # RGBA = 4 color components
            wrap_x=arcade.gl.REPEAT,
            wrap_y=arcade.gl.REPEAT,
            filter=(arcade.gl.NEAREST, arcade.gl.NEAREST)
        )
        self.fbo_0 = manager.game_loop.ctx.framebuffer(color_attachments=[self.tex_0])

        self.tex_1 = manager.game_loop.ctx.texture(
            size=(self.ceil_tex.width, self.ceil_tex.height),
            data=ceil_tex_data,
            components=4,
            wrap_x=arcade.gl.REPEAT,
            wrap_y=arcade.gl.REPEAT,
            filter=(arcade.gl.NEAREST, arcade.gl.NEAREST)
        )
        self.fbo_1 = manager.game_loop.ctx.framebuffer(color_attachments=[self.tex_1])

    def draw_floor_ceiling(self) -> None:
        """
        Renders textured floor and ceiling using GPU shaders.
        
        :return: None
        """
        import arcade
        import arcade.gl
        from FireEngine.core import manager

        # Use the shader program
        self.floor_shader.use()
        self.ceiling_shader.use()

        # Set uniforms
        self.floor_shader["SCREEN_WIDTH"] = SCREEN_WIDTH
        self.floor_shader["SCREEN_HEIGHT"] = SCREEN_HEIGHT
        self.floor_shader['posZ'] = 0.5 * SCREEN_HEIGHT
        self.floor_shader['rayDir0'] = (self.player.dir_x - self.player.plane_x, self.player.dir_y - self.player.plane_y)
        self.floor_shader['rayDir1'] = (self.player.dir_x + self.player.plane_x, self.player.dir_y + self.player.plane_y)
        self.floor_shader['playerPos'] = (self.player.player_x, self.player.player_y)

        self.ceiling_shader["SCREEN_WIDTH"] = SCREEN_WIDTH
        self.ceiling_shader["SCREEN_HEIGHT"] = SCREEN_HEIGHT
        self.ceiling_shader['posZ'] = 0.5 * SCREEN_HEIGHT
        self.ceiling_shader['rayDir0'] = (self.player.dir_x - self.player.plane_x, self.player.dir_y - self.player.plane_y)
        self.ceiling_shader['rayDir1'] = (self.player.dir_x + self.player.plane_x, self.player.dir_y + self.player.plane_y)
        self.ceiling_shader['playerPos'] = (self.player.player_x, self.player.player_y)

        self.floor_shader['floor_texture'] = 0
        self.tex_0.use(0)

        self.ceiling_shader['ceil_texture'] = 1
        self.tex_1.use(1)

        # Draw a full-screen quad
        quad_f = arcade.gl.geometry.quad_2d_fs()
        quad_f.render(self.floor_shader)

        quad_c = arcade.gl.geometry.quad_2d_fs()
        quad_c.render(self.ceiling_shader)

    ########################
    #   Update functions   #
    ########################
    
    def on_start(self) -> None:
        """
        Initializes rendering resources and sets up sprite batching.
    
        This method creates a custom texture atlas and initializes the draw list
        used for batching sprites, which optimizes rendering performance.
        """
        import arcade

        # Calculate the atlas size as twice 4096x4096
        atlas_size: tuple[int, int] = (4096 * 2, 4096 * 2)
        # Create a custom texture atlas using the current window’s context
        custom_atlas = arcade.TextureAtlas(atlas_size, ctx=arcade.get_window().ctx)
        # Initialize the draw list with spatial hashing to optimize sprite lookup
        self.draw_list = arcade.SpriteList(
            use_spatial_hash=True,
            is_static=False,
            capacity=100000,
            atlas=custom_atlas
        )
        # No additional initialization needed for now
    
    def on_update(self, delta_time: float) -> None:
        """
        Updates display parameters and player orientation based on elapsed time.
    
        This method updates global screen dimensions, recalculates the aspect ratio,
        adjusts the player's field of view (FOV), camera plane, and direction vectors
        according to the player's current angle.
        
        :param delta_time: Time elapsed since the last update.
        """
        import arcade
        from FireEngine.player import player

        # Update global screen dimensions using the current window size.
        global SCREEN_WIDTH, SCREEN_HEIGHT
        SCREEN_WIDTH, SCREEN_HEIGHT = arcade.get_window().get_size()
        
        # Set a base FOV (in radians) as a starting point.
        player.Player.FOV = math.pi / 3
        
        # Calculate the aspect ratio from current screen dimensions.
        self.aspect_ratio = SCREEN_WIDTH / SCREEN_HEIGHT
        
        # Adjust the player's FOV according to the original FOV and aspect ratio.
        player.Player.FOV = player.Player.original_FOV * self.aspect_ratio
        
        # Update the camera plane to keep the FOV constant during rotation.
        # The plane is perpendicular to the player's direction.
        player.Player.plane_x = -player.Player.FOV * math.sin(player.Player.player_angle)
        player.Player.plane_y = player.Player.FOV * math.cos(player.Player.player_angle)
        
        # Update the player's directional vector based on the current angle.
        player.Player.dir_x = math.cos(player.Player.player_angle)
        player.Player.dir_y = math.sin(player.Player.player_angle)
    
    def on_render(self) -> None:
        """
        Renders the scene by drawing floor, walls, objects, and batched sprites.
    
        This method begins by resetting the z-buffer and clearing previous frame data.
        It then ensures shaders are loaded before calling the rendering methods for the
        floor, walls, and objects. Finally, the batched sprites are drawn using a nearest-
        neighbor filter, and the draw list is cleared for the next frame.
        """
        import arcade.gl
        
        # Reset rendering priority and clear the z-buffer for the new frame.
        self.priority = 0
        self.z_buffer.clear()
        
        # Load shaders if they haven't been loaded yet (e.g., floor texture must be initialized).
        if not hasattr(self, 'floor_tex'):
            self.load_shaders()
        
        # Clear any previously batched sprites.
        self.draw_list.clear()
        
        # Render floor and ceiling, walls, and in-game objects.
        self.draw_floor_ceiling()
        self.draw_walls()
        self.draw_objects()
        
        # Draw the batched sprites using NEAREST filter to avoid scaling artifacts.
        self.draw_list.draw(filter=arcade.gl.NEAREST)
        
        # Clear both the draw list and its internal sprite list to prepare for the next frame.
        self.draw_list.clear()
        self.draw_list.sprite_list.clear()

Render = Renderer()