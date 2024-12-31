from FireEngine.core.decorators import register

# List of dropables in the game world
dropables = []
dropable_count = 0

@register
class dropable:
    def __init__(self, x, y, rotation, _dropable):
        from FireEngine.core.resources import resource_loading
        import arcade
        import os

        dropables.append(self)

        self._dropable = _dropable

        self.x = float(x + 0.5)
        self.y = float(y + 0.5)
        self.rotation = rotation
        self.animation_rotation = 0
        self.hitbox_x = _dropable.hitbox_x
        self.hitbox_y = _dropable.hitbox_y
        self.texture = _dropable.texture
        self.texture_path = _dropable.texture_path
        
        self.health = _dropable.health
        self.max_health = _dropable.max_health
        self.armor = _dropable.armor
        self.max_armor = _dropable.max_armor
        self.stamina = _dropable.stamina
        self.max_stamina = _dropable.max_stamina

        self.give_weapon_id = _dropable.give_weapon_id

        self.pistol_ammo = _dropable.pistol_ammo
        self.rifle_ammo = _dropable.rifle_ammo
        self.shotgun_ammo = _dropable.shotgun_ammo

        self.score = _dropable.score

        # Pickup info
        self.pickup_sfx = _dropable.pickup_sfx
        self.pickup_vfx = _dropable.pickup_vfx

        self.view_angles = []
        self.view_angles_path = []   

    ########################
    #   Update functions   #
    ########################

    def on_update(self, delta_time):
        from FireEngine.player import player
        from FireEngine.core import manager
        import arcade

        # Check if theirs an intersection with the player
        if abs(player.Player.player_x - self.x) <= self.hitbox_x:
            if abs(player.Player.player_y - self.y) <= self.hitbox_y:
                arcade.play_sound(self.pickup_sfx)

                # Health logic
                extra_hp = player.Player.max_health - player.Player.health
                
                if extra_hp < self.health:
                    additional_hp = extra_hp
                else:
                    additional_hp = self.health

                player.Player.max_health += self.max_health
                player.Player.health += additional_hp

                # Armor logic
                extra_ap = player.Player.max_armor - player.Player.armor
                
                if extra_ap < self.armor:
                    additional_ap = extra_ap
                else:
                    additional_ap = self.armor

                player.Player.max_armor += self.max_armor
                player.Player.armor += additional_ap

                # Stamina logic
                extra_st = player.Player.max_stamina - player.Player.stamia
                
                if extra_st < self.stamina:
                    additional_st = extra_st
                else:
                    additional_st = self.stamina

                player.Player.max_stamina += self.max_stamina
                player.Player.stamia += additional_st
                
                player.Player.score += self.score

                if self.give_weapon_id != -1:
                    player.Player.unlocked_weapons[self.give_weapon_id] = True

                player.Player.pistol_ammo += self.pistol_ammo
                player.Player.rifle_ammo += self.rifle_ammo
                player.Player.shotgun_ammo += self.shotgun_ammo

                dropables.remove(self)
                manager.Game.unregister(self)