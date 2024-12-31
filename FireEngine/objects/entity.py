from FireEngine.core.decorators import register

# List of sprites in the game world
entities = []
entity_count = 0

@register
class entity:
    def __init__(self, x, y, rotation, _entity):
        from FireEngine.core.resources import resource_loading
        import arcade
        import random
        import os

        entities.append(self)

        self._entity = _entity

        self.x = float(x + 0.5)
        self.y = float(y + 0.5)
        self.rotation = rotation
        self.animation_rotation = 0
        self.hitbox_x = float(_entity.hitbox_x)
        self.hitbox_y = float(_entity.hitbox_y)
        self.health = _entity.health
        self.sprite_sheet_path = _entity.animation_sheet
        
        self.walk_ani_0, self.walk_ani_0_path, self.walk_ani_45, self.walk_ani_45_path, self.walk_ani_90, self.walk_ani_90_path, self.walk_ani_135, self.walk_ani_135_path, self.walk_ani_180, self.walk_ani_180_path, self.walk_ani_225, self.walk_ani_225_path, self.walk_ani_270, self.walk_ani_270_path, self.walk_ani_315, self.walk_ani_315_path, self.shoot_ani, self.shoot_ani_path, self.death_ani, self.death_ani_path = self.load_animations(self.sprite_sheet_path)

        # Death animation properties
        self.death_animation = self.death_ani or []
        self.is_dying = False
        self.current_death_frame = 0
        self.death_timer = 0
        self.death_frame_duration = 0.2  # Time (in seconds) per frame

        self.patrol_timer = random.uniform(1, 3)  # Time to move from current spot to the other
        self.patrol_wait = _entity.patrol_wait # Time to wait between movements
        self.target_x = None
        self.target_y = None

        self.max_detect_distance = _entity.fire_range

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
        self.no_fire_frame_duration = random.uniform(self._entity.fire_freq_low, self._entity.fire_freq_high)

        # Audio
        self.gun_shot = arcade.load_sound(os.path.join(resource_loading.Assets, _entity.pistol_sfx))

        # Textures
        self.texture = self.shoot_ani[1]
        self.texture_path = self.shoot_ani_path[1]

        # Load gore/scream sounds
        self.gore_sounds = resource_loading.load_folder_sounds(os.path.join(resource_loading.Assets, _entity.gore_sfx))

        # Load specific death sound
        self.scream_sounds = resource_loading.load_folder_sounds(os.path.join(resource_loading.Assets, _entity.scream_sfx))

        # Load specific death sound
        self.death_sound = resource_loading.load_folder_sounds(os.path.join(resource_loading.Assets, _entity.death_sfx))

    def load_animations(self, path):
        '''Loads all animations and textures from a sprite sheet'''
        from FireEngine.core.resources import resource_loading
        import arcade
        import random
        import os

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
        height = sheet.height
        width = sheet.width

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
                        output_folder = os.path.join(resource_loading.Cache)
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
        import math

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
        from FireEngine.core import scene
        import math
        import random

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
                    if self.can_see(target_x, target_y) and scene.scene_data[target_y][target_x] == ' ':
                        valid_tiles.append((target_x + 0.5, target_y + 0.5))
    
            if valid_tiles:
                self.target_x, self.target_y = random.choice(valid_tiles)
    
        # Move towards target position if set
        if self.target_x is not None and self.target_y is not None:
            speed = self._entity.speed * delta_time
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
        from FireEngine.core import scene
        from FireEngine.core.resources import resource_loading
        import math

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
            if map_x < 0 or map_x >= len(scene.scene_data[0]) or map_y < 0 or map_y >= len(scene.scene_data):
                return False

            # Check if we've reached the target tile
            if int(ray_x) == int(target_x) and int(ray_y) == int(target_y):
                return True

            tile = scene.scene_data[map_y][map_x]

            # Check for walls blocking the view
            if tile != ' ':
                for door in resource_loading.doors:
                    if tile != resource_loading.doors[door].open_icon:
                        return False

        return False  # Target is out of maximum range or blocked by walls

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
                    self.texture = self.shoot_ani[0]
                    self.texture_path = self.shoot_ani_path[0]
                elif self.current_shoot_frame == 1:
                    self.texture = self.shoot_ani[1]
                    self.texture_path = self.shoot_ani_path[1]

                if self.shoot_timer >= self.no_fire_frame_duration and self.current_shoot_frame == 0:
                    arcade.play_sound(self.gun_shot, 0.7) # type: ignore

                    if random.uniform(0, 100) <= ((distance) / self.max_detect_distance) * 100:
                        damage = self._entity.damage_low + (self._entity.damage_high - self._entity.damage_low) / distance
                        chance = self._entity.hit_chance_far + (self._entity.hit_chance_close - self._entity.hit_chance_far) / distance
                        
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
            if self.current_walk_frame + 2 >= len(self.walk_ani_0):
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