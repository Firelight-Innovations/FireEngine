from FireEngine.core.decorators import register
from FireEngine.core.resources import data_containers
from typing import Any, Dict, Optional, Union

# List of sprites in the game world
entities = []
entity_count = 0

@register
class Entity:
    def __init__(self, x: float, y: float, rotation: float, entity: data_containers.Entity):
        from FireEngine.core.resources import resource_loading
        import arcade
        import random
        import os

        entities.append(self)

        self.entity: data_containers.Entity = entity

        self.x: float = x + 0.5
        self.y: float = y + 0.5
        self.rotation:float = rotation
        self.animation_rotation: float = 0
        self.hitbox_x: float = entity.hitbox_x
        self.hitbox_y: float = entity.hitbox_y
        self.health: float = entity.health
        self.sprite_sheet_path: str = entity.animation_sheet
        # Define constants for frame dimensions and spacing.
        self.FRAME_SIZE: int = 64
        self.FRAME_SPACING: int = 1  # Extra pixels between frames (65 total per frame)
        
        self.animation: Dict[str, Any] = self.load_animations(entity.animation_sheet)

        # Death animation properties
        self.is_dying: bool = False
        self.current_death_frame: int = 0
        self.death_timer: float = 0
        self.death_frame_duration: float = 0.2  # Time (in seconds) per frame

        self.patrol_timer: float = random.uniform(1, 3)  # Time to move from current spot to the other
        self.patrol_wait: float = entity.patrol_wait # Time to wait between movements
        self.target_x: float = None
        self.target_y: float = None

        self.max_detect_distance: float = entity.fire_range

        # Walking animation
        self.is_walking: bool = False
        self.current_walk_frame: int = 0
        self.walk_timer: float = 0
        self.walk_frame_duration: float = 0.2

        # Shooting animation
        self.is_shooting: bool = False
        self.current_shoot_frame: int = 0
        self.shoot_timer: float = 0
        self.fire_frame_duration: float = 0.1
        self.no_fire_frame_duration: float = random.uniform(self.entity.fire_freq_low, self.entity.fire_freq_high)

        # Audio
        self.gun_shot: arcade.Sound = arcade.load_sound(os.path.join(resource_loading.ASSETS, entity.pistol_sfx))

        # Load gore/scream sounds
        self.gore_sounds: dict[arcade.Sound] = resource_loading.load_folder_sounds(os.path.join(resource_loading.ASSETS, entity.gore_sfx))

        # Load specific death sound
        self.scream_sounds: dict[arcade.Sound] = resource_loading.load_folder_sounds(os.path.join(resource_loading.ASSETS, entity.scream_sfx))

        # Load specific death sound
        self.death_sound: dict[arcade.Sound] = resource_loading.load_folder_sounds(os.path.join(resource_loading.ASSETS, entity.death_sfx))

    def load_animations(self: Any, path: str) -> Dict[str, Any]:
        """
        Loads all animations and textures from a sprite sheet.

        The sprite sheet is assumed to include:
          - A shoot animation on the first row.
          - A death animation on the second row.
          - Walk animations on subsequent rows; for each row, the frame index (j)
            is mapped to a specific angle using an angle mapping.

        Animations are stored in a dictionary with the following structure:
            {
                "shoot": {"textures": List[arcade.Texture], "paths": List[str]},
                "death": {"textures": List[arcade.Texture], "paths": List[str]},
                "walk": {
                    0: {"textures": List[arcade.Texture], "paths": List[str]},
                    45: {...},
                    90: {...},
                    135: {...},
                    180: {...},
                    225: {...},
                    270: {...},
                    315: {...}
                }
            }

        Additionally, the function reverses the order of walk animations for correct playback 
        and assigns the first walk texture (angle 0) to self.texture.

        Args:
            self: An instance that will receive the loaded texture.
            path (str): Path to the sprite sheet image.

        Returns:
            Dict[str, Any]: A dictionary containing shoot, death, and walk animation data.
        """
        import arcade
        from FireEngine.core.resources import resource_loading
        import os
        import random

        # Define the mapping for walk cycle frames based on their index.
        angle_map: Dict[int, int] = {
            0: 0, 1: 45, 2: 90, 3: 135, 4: 180, 5: 225, 6: 270, 7: 315
        }

        # Initialize dictionaries to store animations.
        animations: Dict[str, Any] = {
            "shoot": {"textures": [], "paths": []},
            "death": {"textures": [], "paths": []},
            "walk": {angle: {"textures": [], "paths": []} for angle in angle_map.values()},
        }

        # Load the complete sprite sheet to get overall dimensions.
        sheet: arcade.Texture = arcade.load_texture(path)
        sheet_height: int = sheet.height
        sheet_width: int = sheet.width

        # Start from the bottom row of the sheet.
        y: int = sheet_height

        # Calculate number of rows by dividing by frame height + spacing.
        # Using round here to mimic your original calculation.
        num_rows: int = round(sheet_height / (self.FRAME_SIZE + self.FRAME_SPACING))

        for i in range(num_rows):
            x: int = 0  # x-coordinate in the sprite sheet
            j: int = 0  # index within the row to decide which walk cycle angle (if applicable)
            while True:
                try:
                    # Load a frame from the sprite sheet.
                    texture: arcade.Texture = arcade.load_texture(
                        path,
                        x=x,
                        y=y,
                        width=self.FRAME_SIZE,
                        height=self.FRAME_SIZE
                    )
                    # Increment x to advance to the next frame in the row.
                    x += self.FRAME_SIZE + self.FRAME_SPACING

                    # Check transparency to determine if the frame is valid.
                    image = texture.image
                    is_valid: bool = not all(pixel == (0, 0, 0, 0) for pixel in image.getdata())
                    if not is_valid:
                        # Break out of the inner loop if a fully transparent frame is encountered.
                        break
                    
                    # Save the texture image to the cache folder.
                    output_folder: str = resource_loading.CACHE
                    os.makedirs(output_folder, exist_ok=True)
                    output_file: str = f"{x}{y}{i}{j}-{sheet_height * random.randint(0, 10)}.png"
                    output_path: str = os.path.join(output_folder, output_file)
                    image.save(output_path)

                    # Determine the animation type based on the current row.
                    if i == 0:
                        # First row: shoot animation.
                        animations["shoot"]["textures"].append(texture)
                        animations["shoot"]["paths"].append(output_path)
                    elif i == 1:
                        # Second row: death animation.
                        animations["death"]["textures"].append(texture)
                        animations["death"]["paths"].append(output_path)
                    else:
                        # Subsequent rows: walk animations (using the index j to assign angle).
                        angle: Union[int, None] = angle_map.get(j)
                        if angle is not None:
                            animations["walk"][angle]["textures"].append(texture)
                            animations["walk"][angle]["paths"].append(output_path)
                    j += 1
                except Exception:
                    # Break out of inner loop if frame loading fails.
                    break
                
            # Move one frame height up for the next row.
            y -= (self.FRAME_SIZE + self.FRAME_SPACING)

        # Reverse the walking animations for each angle to correct playback order.
        for angle in animations["walk"]:
            animations["walk"][angle]["textures"].reverse()
            animations["walk"][angle]["paths"].reverse()

        # Optionally assign a default texture (from walk angle 0) to self.texture.
        if animations["walk"][0]["textures"]:
            self.texture = animations["walk"][0]["textures"][0]

        return animations

    def update_texture(self, player_x: float, player_y: float) -> None:
        """
        Updates the enemy texture based on relative position, rotation, and animation state.
    
        The function calculates the angle from the enemy to the player, normalizes it, and
        then selects the appropriate walk (or death) animation frame from self.animations.
    
        Args:
            player_x (float): The player's x coordinate.
            player_y (float): The player's y coordinate.
        """
        import math

        # Compute vector from enemy to player.
        dx: float = player_x - self.x
        dy: float = player_y - self.y
    
        # Determine the angle to the player.
        angle_to_player: float = math.atan2(dy, dx)
    
        # Calculate relative angle (difference between aim and enemy rotation).
        relative_angle: float = (angle_to_player - self.rotation) % (2 * math.pi)
    
        # Choose the current walk frame index.
        frame: int = self.current_walk_frame if self.is_walking else 0
    
        # Determine the appropriate angle segment (each segment is 45°).
        if (0 <= relative_angle < math.pi / 8) or (15 * math.pi / 8 <= relative_angle < 2 * math.pi):
            key = 0
        elif math.pi / 8 <= relative_angle < 3 * math.pi / 8:
            key = 45
        elif 3 * math.pi / 8 <= relative_angle < 5 * math.pi / 8:
            key = 90
        elif 5 * math.pi / 8 <= relative_angle < 7 * math.pi / 8:
            key = 135
        elif 7 * math.pi / 8 <= relative_angle < 9 * math.pi / 8:
            key = 180
        elif 9 * math.pi / 8 <= relative_angle < 11 * math.pi / 8:
            key = 225
        elif 11 * math.pi / 8 <= relative_angle < 13 * math.pi / 8:
            key = 270
        else:
            key = 315
    
        # If the enemy is dying, override with the death animation.
        if self.is_dying:
            self.texture = self.animation["death"]["textures"][self.current_death_frame]
            self.texture_path = self.animation["death"]["paths"][self.current_death_frame]
        else:
            # Otherwise, update the walk animation based on the relative angle.
            self.texture = self.animation["walk"][key]["textures"][frame]
            self.texture_path = self.animation["walk"][key]["paths"][frame]
    
    def patrol(self, delta_time: float, player_x: float, player_y: float) -> None:
        """
        Moves the enemy randomly over valid tiles unless the player is visible.
        
        The enemy checks if the player is within detection range; if so, it stops patrolling.
        Otherwise, it randomly selects a valid target and moves toward it.
        
        Args:
            delta_time (float): Time elapsed since the last update.
            player_x (float): The player's x coordinate.
            player_y (float): The player's y coordinate.
        """
        import math

        from FireEngine.core import scene
        if self.is_dying:
            return

        # Decrease the waiting timer if applicable.
        if self.patrol_wait > 0:
            self.patrol_wait -= delta_time
            return

        # Check if the player is in view.
        dx: float = player_x - self.x
        dy: float = player_y - self.y
        if (dx ** 2 + dy ** 2 <= self.max_detect_distance ** 2) and self.can_see(player_x, player_y):
            self.target_x, self.target_y = None, None
            return

        self.patrol_timer -= delta_time
        if self.patrol_timer <= 0 or (self.target_x is None or self.target_y is None):
            import random
            self.patrol_timer = random.uniform(1, 3)
            valid_tiles = []
            for dy in range(-5, 6):
                for dx in range(-5, 6):
                    target_x = int(self.x + dx)
                    target_y = int(self.y + dy)
                    if self.can_see(target_x, target_y) and scene.scene_data[target_y][target_x] == ' ':
                        valid_tiles.append((target_x + 0.5, target_y + 0.5))
            if valid_tiles:
                self.target_x, self.target_y = random.choice(valid_tiles)
    
        # Move towards the target tile.
        if self.target_x is not None and self.target_y is not None:
            speed: float = 1.0 * delta_time  # Replace 1.0 with self.entity.speed if available.
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            self.rotation = math.atan2(dx, dy)
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance > speed:
                self.x += (dx / distance) * speed
                self.y += (dy / distance) * speed
                self.is_walking = True
            else:
                self.x, self.y = self.target_x, self.target_y
                self.target_x, self.target_y = None, None
                self.is_walking = False
                self.patrol_wait = random.uniform(1, 3)

    def can_see(self, target_x: float, target_y: float) -> bool:
        """
        Checks whether there is an unobstructed line of sight to a given tile.
        
        It casts a ray from the enemy's position toward the target and returns False if a wall is encountered.
        
        Args:
            target_x (float): The target tile's x coordinate.
            target_y (float): The target tile's y coordinate.
        
        Returns:
            bool: True if the target tile is visible; False otherwise.
        """
        import math
        from FireEngine.core.resources import resource_loading

        from FireEngine.core import scene
        ray_x, ray_y = self.x, self.y
        dir_x = target_x - ray_x
        dir_y = target_y - ray_y
        distance = math.hypot(dir_x, dir_y)
        if distance == 0:
            return True
        dir_x /= distance
        dir_y /= distance
        max_distance = self.max_detect_distance
        traveled = 0.0
        
        while traveled < max_distance:
            ray_x += dir_x * 0.1
            ray_y += dir_y * 0.1
            traveled += 0.1
            map_x, map_y = int(ray_x), int(ray_y)
            if map_x < 0 or map_y < 0 or map_y >= len(scene.scene_data) or map_x >= len(scene.scene_data[0]):
                return False
            if int(ray_x) == int(target_x) and int(ray_y) == int(target_y):
                return True
            try:
                tile = scene.scene_data[map_y][map_x]
            except Exception:
                return False
            if tile != ' ':
                # Check for doors that might be open.
                for door in resource_loading.doors:
                    if tile != resource_loading.doors[door].open_icon:
                        return False
        return False
    
    def shoot_at_player(self, delta_time, player):
        """Shoot at the player."""
        import math
        import random
        import arcade

        dx = player.player_x - self.x
        dy = player.player_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if self.is_dying:
            return

        # Increase shooting range (e.g., up to 5 tiles)
        if distance <= self.max_detect_distance:
            if self.can_see(player.player_x, player.player_y):
                if self.current_shoot_frame == 0: #When the enemy is not firing
                    print(self.animation)
                    self.texture = self.animation["shoot"]["textures"][0]
                    self.texture_path = self.animation["shoot"]["path"][0]
                elif self.current_shoot_frame == 1:
                    self.texture = self.animation["shoot"]["textures"][1]
                    self.texture_path = self.animation["shoot"]["path"][1]

                if self.shoot_timer >= self.no_fire_frame_duration and self.current_shoot_frame == 0:
                    arcade.play_sound(self.gun_shot, 0.7) # type: ignore

                    if random.uniform(0, 100) <= ((distance) / self.max_detect_distance) * 100:
                        damage = self.entity.damage_low + (self.entity.damage_high - self.entity.damage_low) / distance
                        chance = self.entity.hit_chance_far + (self.entity.hit_chance_close - self.entity.hit_chance_far) / distance
                        
                        if random.uniform(0.0, 1.0) <= chance:
                            player.hurt_player(random.uniform(0.8, 1) * damage)

                    self.shoot_timer = 0
                    self.current_shoot_frame = 1
                elif self.shoot_timer >= self.fire_frame_duration and self.current_shoot_frame == 1:
                    self.shoot_timer = 0
                    self.current_shoot_frame = 0

                self.shoot_timer += delta_time
                return
        else:
            self.shoot_timer = 0

    def hurt_entity(self, entity, damage, player):
        """Remove a entity when it is hit."""
        import arcade
        import random
        
        entity.health -= damage

        if entity.health <= 0 and not entity.is_dying:
            # Start death animation
            entity.is_dying = True
            entity.current_death_frame = 0
            entity.death_timer = 0
            random_death_sound = random.choice(self.death_sound)
            arcade.play_sound(random_death_sound, volume=1)
            player.max_health += 5
            player.health += 5
        elif entity.health <= 0 and entity.is_dying:
            random_gore_sound = random.choice(self.gore_sounds)
            arcade.play_sound(random_gore_sound, volume=1)
        else:
            random_gore_sound = random.choice(self.gore_sounds)
            random_scream_sound = random.choice(self.scream_sounds)
            arcade.play_sound(random_gore_sound, volume=1)
            arcade.play_sound(random_scream_sound, volume=1)

    ########################
    #   Update functions   #
    ########################

    def on_update(self, delta_time):
        from FireEngine.player import player
        from FireEngine.core import manager

        # Update death animation timer
        self.walk_timer += delta_time
        
        if self.walk_timer >= self.walk_frame_duration:
            if self.current_walk_frame + 2 >= len(self.animation):
                self.current_walk_frame = 1
                self.walk_timer = 0
            else:
                self.current_walk_frame += 1
                self.walk_timer = 0

        if self.is_dying:
            # Update death animation timer
            self.death_timer += delta_time
            if (self.death_timer + self.death_frame_duration >= self.current_death_frame * self.death_frame_duration) and (self.current_death_frame + 1 < len(self.death_animation)):
                self.current_death_frame += 1

            # Remove sprite once animation is complete
            if self.death_timer  >= (len(self.death_animation) * self.death_frame_duration) + 5:
                if self in entities:
                    entities.remove(self)
                    manager.Game.unregister(self)

        self.patrol(delta_time, player.Player.player_x, player.Player.player_y)

        self.update_texture(player_x=player.Player.player_x, player_y=player.Player.player_y)

        # Check if the enemy should shoot at the player
        self.shoot_at_player(delta_time, player.Player)