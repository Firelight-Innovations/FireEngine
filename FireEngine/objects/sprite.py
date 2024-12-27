from FireEngine.core.decorators import singleton
from FireEngine.core.decorators import register

# List of sprites in the game world
sprites = []
sprite_count = 0

@register
class sprite:
    def __init__(self, x, y, rotation, _sprite):
        from FireEngine.core.resources import resource_loading
        import os

        sprites.append(self)

        self._sprite = _sprite

        self.x = float(x + 0.5)
        self.y = float(y + 0.5)
        self.rotation = rotation
        self.animation_rotation = 0
        self.hitbox_x = float(_sprite.hitbox_x)
        self.hitbox_y = float(_sprite.hitbox_y)
        self.transparent = _sprite.transparent
        self.sprite_sheet_path = _sprite.animation_sheet
        self.postional = _sprite.postional
        
        self.view_angles = []
        self.view_angles_path = []

        self.load_animations()

        # Load specific death sound
        self.hit_sounds = resource_loading.load_folder_sounds(os.path.join(resource_loading.Assets, _sprite.hit_sfx))

    def load_animations(self):
        '''Loads all animations and textures from a sprite sheet'''
        from FireEngine.core.resources import resource_loading
        import arcade
        import random
        import os

        view_angles = []
        view_angles_path = []

        # Load sheet
        sheet = arcade.load_texture(self.sprite_sheet_path)
        height = sheet.height
        width = sheet.width

        # Splice sheet
        # Load all shoot_ani

        y = height - 64

        # Scans file from the very bottom to the very top
        # Loops through all rows in sprite sheet
        if self.postional:
            for i in range(0, round(height / 65)):
                # Loops through row
                loop = True

                x = 0 # x-val for sprite sheet
                j = 0 # index of sprite for that row, used to seperarate walk cycle angles

                while loop:
                    try:
                        texture = arcade.load_texture(
                            self.sprite_sheet_path,
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
                            output_folder = os.path.join(resource_loading.Cache)
                            output_file = f"{x}{y}{i}{j}-{height * random.randint(0, 100000)}.png"

                            # Ensure the folder exists
                            os.makedirs(output_folder, exist_ok=True)

                            # Save the image to the specified folder
                            output_path = os.path.join(output_folder, output_file)
                            image.save(output_path)

                            view_angles.append(texture)
                            view_angles_path.append(output_path)
                    except:
                        loop = False

                    j += 1

                y -= 65
            
            self.texture = view_angles[0]
            self.texture_path = view_angles_path[0]

            self.view_angles = view_angles[::-1]
            self.view_angles_path = view_angles_path[::-1]
        else:
            # Load sheet
            sheet = arcade.load_texture(self.sprite_sheet_path)
            height = sheet.height
            width = sheet.width

            texture = arcade.load_texture(
                self.sprite_sheet_path,
                x=0,
                y=0,
                width=64,
                height=64
            )

            image = texture.image

            output_folder = os.path.join(resource_loading.Cache)
            output_file = f"{height * random.randint(0, 100000)}.png"

            # Ensure the folder exists
            os.makedirs(output_folder, exist_ok=True)

            # Save the image to the specified folder
            output_path = os.path.join(output_folder, output_file)
            image.save(output_path)

            self.texture = image
            self.texture_path = output_path
    
    def update_texture(self, player_x, player_y):
        '''Updates the enemies texture based on a rotation, movement, and status.'''
        import math

        # Skip if postional
        if not self.postional:
            return

        # Step 1: Calculate direction vector from enemy to player
        dx = player_x - self.x
        dy = player_y - self.y

        # Step 2: Calculate angle from enemy to player
        angle_to_player = math.atan2(dy, dx)

        # Step 3: Calculate relative angle (difference between enemy rotation and angle_to_player)
        relative_angle = angle_to_player - self.rotation

        # Normalize relative_angle to range [0, 2π]
        relative_angle = (relative_angle + math.pi * 2) % (math.pi * 2)

        # Step 4: Determine which texture to use based on 45° segments
        if 0 <= relative_angle < math.pi / 8 or 15 * math.pi / 8 <= relative_angle < 2 * math.pi: # Correct
            # Front (0°)
            self.texture = self.view_angles[7]
            self.texture_path = self.view_angles_path[7]
        elif (9 * math.pi / 8) + (math.pi / 2) <= relative_angle < (11 * math.pi / 8) + (math.pi / 2): # Correct
            # Front-right (45°)
            self.texture = self.view_angles[6]
            self.texture_path = self.view_angles_path[6]
        elif 11 * math.pi / 8 <= relative_angle < 13 * math.pi / 8: # Correct
            # Right (90°)
            self.texture = self.view_angles[5]
            self.texture_path = self.view_angles_path[5]
        elif (5 * math.pi / 8) + (math.pi / 2) <= relative_angle < (7 * math.pi / 8) + (math.pi / 2): # Correct
            # Back-right (135°)
            self.texture = self.view_angles[4]
            self.texture_path = self.view_angles_path[4]
        elif 7 * math.pi / 8 <= relative_angle < 9 * math.pi / 8: # Correct
            # Back (180°)
            self.texture = self.view_angles[3]
            self.texture_path = self.view_angles_path[3]
        elif (math.pi / 8) + (math.pi / 2) <= relative_angle < (3 * math.pi / 8) + (math.pi / 2): # Correct
            # Back-left (225°)
            self.texture = self.view_angles[2]
            self.texture_path = self.view_angles_path[2]
        elif 3 * math.pi / 8 <= relative_angle < 5 * math.pi / 8: # Correct
            # Left (270°)
            self.texture = self.view_angles[1]
            self.texture_path = self.view_angles_path[1]
        else:
            # Front-left (315°)
            self.texture = self.view_angles[0]
            self.texture_path = self.view_angles_path[0]

    def hurt_sprite(self):
        """Remove a entity when it is hit."""
        import arcade
        import random
        
        random_hit_sfx = random.choice(self.hit_sounds)
        arcade.play_sound(random_hit_sfx, volume=1)

    ########################
    #   Update functions   #
    ########################

    def on_update(self, delta_time):
        from FireEngine.player import player

        self.update_texture(player_x=player.Player.player_x, player_y=player.Player.player_y)