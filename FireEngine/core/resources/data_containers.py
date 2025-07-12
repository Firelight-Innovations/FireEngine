from typing import Any, Dict, Optional, Union
import os
import arcade

# It is assumed that resource_loading provides attributes like ASSETS and DefaultTexture,
# as well as helper functions (e.g., load_sprite_sheet) for asset management.
# Imports from FireEngine.core.resources are done inside __init__ for lazy loading and to avoid circular dependencies.

class Scene:
    """
    Container for scene data.

    Attributes:
        name (str): The name of the scene.
        difficulty (int): The difficulty level of the scene.
        order (int): The sequence order of the scene.
        description (str): A description of the scene.
        data (Any): Additional data associated with the scene.
    """
    def __init__(
        self, 
        name: str = "", 
        difficulty: int = 0, 
        order: int = 0, 
        description: str = "", 
        data: Optional[Dict[str, Any]] = []
    ) -> None:
        self.name: str = name
        self.difficulty: int = difficulty
        self.order: int = order
        self.description: str = description
        self.data: Any = data

class Texture:
    """
    Container for texture data and its associated sound effects.

    Attributes:
        name (str): The name of the texture.
        texture_path (str): Full path to the texture file.
        icon (str): Identifier used to represent the texture icon.
        hit_sfx (Union[arcade.Sound, str]): Loaded hit sound effect or fallback string.
        walk_sfx (Union[arcade.Sound, str]): Loaded walk sound effect or fallback string.
    """
    def __init__(
        self, 
        name: str = "", 
        location: str = "", 
        icon: str = "", 
        hit_sfx: str = "", 
        walk_sfx: str = ""
    ) -> None:
        from FireEngine.core.resources import resource_loading

        self.name: str = name
        # Build full file path for the texture; fallback to a default texture on error.
        try:
            self.texture_path: str = os.path.join(resource_loading.ASSETS, location)
        except Exception:
            self.texture_path = resource_loading.DEFAULT_TEXTURE

        self.icon: str = icon

        # Load hit sound effect; if the loading fails, return the provided identifier.
        try:
            self.hit_sfx: Union[arcade.Sound, str] = arcade.load_sound(
                os.path.join(resource_loading.ASSETS, hit_sfx)
            )
        except Exception:
            self.hit_sfx = hit_sfx

        # Load walking sound effect similarly.
        try:
            self.walk_sfx: Union[arcade.Sound, str] = arcade.load_sound(
                os.path.join(resource_loading.ASSETS, walk_sfx)
            )
        except Exception:
            self.walk_sfx = walk_sfx

class Door:
    """
    Container for door data including textures and sound effects.

    Attributes:
        name (str): The door's name.
        close_texture (str): Path to the texture when the door is closed.
        open_texture (str): Path to the texture when the door is open.
        wall_texture (str): Path to the wall texture behind the door.
        close_icon (str): Icon identifier for the closed door.
        open_icon (str): Icon identifier for the open door.
        render_open_door (bool): Flag indicating if the door should be rendered as open.
        hit_sfx (Any): Sound effect played when the door is hit.
    """
    def __init__(
        self, 
        name: str = "", 
        close_location: str = "",
        open_location: str = "", 
        wall_location: str = "",
        close_icon: str = "", 
        open_icon: str = "",
        render_open: bool = False,
        hit_sfx: Any = None
    ) -> None:
        from FireEngine.core.resources import resource_loading

        self.name: str = name

        try:
            self.close_texture: str = os.path.join(resource_loading.ASSETS, close_location)
        except Exception:
            self.close_texture = resource_loading.DEFAULT_TEXTURE

        try:
            self.open_texture: str = os.path.join(resource_loading.ASSETS, open_location)
        except Exception:
            self.open_texture = resource_loading.DEFAULT_TEXTURE

        try:
            self.wall_texture: str = os.path.join(resource_loading.ASSETS, wall_location)
        except Exception:
            self.wall_texture = resource_loading.DEFAULT_TEXTURE

        self.close_icon: str = close_icon
        self.open_icon: str = open_icon
        self.render_open_door: bool = render_open
        self.hit_sfx: Any = hit_sfx

class Entity:
    """
    Container for entity (e.g., enemy) data.

    Attributes:
        name (str): The entity's name.
        icon (str): Icon representing the entity.
        hitbox_x (float): Width of the entity's hitbox.
        hitbox_y (float): Height of the entity's hitbox.
        animation_sheet (str): File path to the entity's animation sprite sheet.
        speed (float): Movement speed.
        weapon (Any): Weapon data associated with the entity.
        health (float): Health points.
        armor (float): Armor points.
        damage_low (float): Minimum damage.
        damage_high (float): Maximum damage.
        fire_range (float): Effective firing range.
        hit_chance_close (float): Hit probability at close range.
        hit_chance_far (float): Hit probability at long range.
        fire_freq_low (float): Lower bound for firing frequency.
        fire_freq_high (float): Upper bound for firing frequency.
        view_range (float): Detection range.
        ai_system (Any): AI behavior system.
        patrol_wait (float): Wait time between patrol actions.
        death_sfx (str): Path to the death sound effect.
        gore_sfx (str): Path to the gore sound effect.
        scream_sfx (str): Path to the scream sound effect.
        pistol_sfx (str): Path to the pistol sound effect.
        shotgun_sfx (str): Path to the shotgun sound effect.
        rifle_sfx (str): Path to the rifle sound effect.
    """
    def __init__(
        self, 
        name: str = "", 
        icon: str = "",
        data: Dict[str, Any] = {}
    ) -> None:
        from FireEngine.core.resources import resource_loading

        self.name: str = name
        self.icon: str = icon

        # Initialize hitbox dimensions from the provided data dictionary.
        self.hitbox_x: float = float(data.get('hitbox_x', 0))
        self.hitbox_y: float = float(data.get('hitbox_y', 0))

        # Load the animation sheet path.
        self.animation_sheet: str = os.path.join(resource_loading.ASSETS, data.get('animation', ""))
        self.speed: float = float(data.get('speed', 0))
        self.weapon: Any = data.get('weapon', None)
        self.health: float = float(data.get('health', 0))
        self.armor: float = float(data.get('armor', 0))
        self.damage_low: float = float(data.get('damage_low', 0))
        self.damage_high: float = float(data.get('damage_high', 0))
        self.fire_range: float = float(data.get('fire_range', 0))
        self.hit_chance_close: float = float(data.get('hit_chance_close', 0))
        self.hit_chance_far: float = float(data.get('hit_chance_far', 0))
        self.fire_freq_low: float = float(data.get('fire_freq_low', 0))
        self.fire_freq_high: float = float(data.get('fire_freq_high', 0))

        # Enemy AI configuration.
        self.view_range: float = float(data.get('view_range', 0))
        self.ai_system: Any = data.get('ai_system', None)
        self.patrol_wait: float = float(data.get('patrol_wait', 0))

        # Load audio file paths for entity actions.
        self.death_sfx: str = os.path.join(resource_loading.ASSETS, data.get('death_sfx', ""))
        self.gore_sfx: str = os.path.join(resource_loading.ASSETS, data.get('gore_sfx', ""))
        self.scream_sfx: str = os.path.join(resource_loading.ASSETS, data.get('scream_sfx', ""))
        self.pistol_sfx: str = os.path.join(resource_loading.ASSETS, data.get('pistol_sfx', ""))
        self.shotgun_sfx: str = os.path.join(resource_loading.ASSETS, data.get('shotgun_sfx', ""))
        self.rifle_sfx: str = os.path.join(resource_loading.ASSETS, data.get('rifle_sfx', ""))

class Sprite:
    """
    Container for sprite data.

    Attributes:
        name (str): The name of the sprite.
        icon (str): Icon representing the sprite.
        hitbox_x (float): Hitbox width.
        hitbox_y (float): Hitbox height.
        transparent (bool): True if the sprite image has transparency.
        postional (bool): True if the sprite's position is significant for rendering.
        animation_sheet (str): Path to the sprite's animation sheet.
        hit_sfx (str): Path to the hit sound effect.
    """
    def __init__(
        self, 
        name: str = "", 
        icon: str = "",
        data: Dict[str, Any] = {}
    ) -> None:
        from FireEngine.core.resources import resource_loading

        self.name: str = name
        self.icon: str = icon
        self.hitbox_x: float = float(data.get('hitbox_x', 0))
        self.hitbox_y: float = float(data.get('hitbox_y', 0))
        self.transparent: bool = bool(data.get('transparent', False))
        self.postional: bool = bool(data.get('postional', False))
        self.animation_sheet: str = os.path.join(resource_loading.ASSETS, data.get('animation_sheet', ""))
        self.hit_sfx: str = os.path.join(resource_loading.ASSETS, data.get('hit_sfx', ""))

class Weapon:
    """
    Data container for weapon attributes and associated assets.
    
    Attributes:
        name (str): Name of the weapon.
        texture_size_x (int): Width of the weapon texture.
        texture_size_y (int): Height of the weapon texture.
        texture_buffer (int): Buffer size for texture slicing.
        weapon_x (int): X position for weapon placement.
        weapon_y (int): Y position for weapon placement.
        weapon_scale (float): Scaling factor for weapon rendering.
        damage_high (float): Maximum damage of the weapon.
        damage_low (float): Minimum damage of the weapon.
        range (float): Effective range of the weapon.
        max_ammo (int): Maximum ammunition capacity.
        start_ammo (int): Starting ammunition count.
        unlock_on_start (bool): Whether the weapon is unlocked at game start.
        is_automatic (bool): Whether the weapon fires automatically.
        loose_on_death (bool): Whether the weapon is lost on death.
        uses_ammo (bool): Whether the weapon consumes ammo.
        does_reload (bool): Whether the weapon supports reloading.
        does_jam (bool): Whether the weapon can jam.
        ammo_type (str): Type of ammunition used.
        weapon_id (Union[int, str]): Identifier for the weapon.
        reload_time (float): Time required to reload.
        fire_time (float): Delay between firing shots.
        fire_animation (Any): Sprite sheet data for firing animation.
        fire_sfx (arcade.Sound): Sound effect for firing.
        reload_animation (Optional[Any]): Sprite sheet for reload animation (if applicable).
        reload_sfx (Optional[arcade.Sound]): Sound effect for reloading (if applicable).
        jam_animation (Optional[Any]): Sprite sheet for jam animation (if applicable).
        jam_sfx (Optional[arcade.Sound]): Sound effect for jamming (if applicable).
        loudness (float): Loudness level of the weapon.
    """

    def __init__(self, name: str = "", data: Optional[Dict[str, Any]] = None) -> None:
        """
        Initializes a Weapon instance with attributes loaded from data and preloads assets.
        
        :param name: Name of the weapon.
        :param data: Dictionary containing weapon configuration.
        """
        from FireEngine.core.resources import resource_loading

        # Use an empty dictionary if no configuration is provided.
        if data is None:
            data = {}

        # Basic info
        self.name: str = name

        # Weapon configuration loaded from the data dictionary.
        self.texture_size_x: int = data.get('texture_size_x', 0)
        self.texture_size_y: int = data.get('texture_size_y', 0)
        self.texture_buffer: int = data.get('texture_buffer', 0)
        self.weapon_x: int = data.get('weapon_x', 0)
        self.weapon_y: int = data.get('weapon_y', 0)
        self.weapon_scale: float = data.get('weapon_scale', 1.0)
        self.damage_high: float = data.get('damage_high', 0.0)
        self.damage_low: float = data.get('damage_low', 0.0)
        self.range: float = data.get('range', 0.0)
        self.max_ammo: int = data.get('max_ammo', 0)
        self.start_ammo: int = data.get('start_ammo', 0)
        self.unlock_on_start: bool = data.get('unlock_on_start', False)
        self.is_automatic: bool = data.get('is_automatic', False)
        self.loose_on_death: bool = data.get('loose_on_death', False)
        self.uses_ammo: bool = data.get('uses_ammo', True)
        self.does_reload: bool = data.get('does_reload', False)
        self.does_jam: bool = data.get('does_jam', False)
        self.ammo_type: str = data.get('ammo_type', "")
        self.weapon_id: Union[int, str] = data.get('weapon_id', "")
        self.reload_time: float = data.get('reload_time', 0.0)
        self.fire_time: float = data.get('fire_time', 0.0)

        # Resolve asset paths using the resource_loading module.
        assets_path: str = resource_loading.ASSETS

        # Load fire animation and sound.
        fire_anim_path: str = os.path.join(assets_path, data.get('fire_animation', ""))
        self.fire_animation: Any = resource_loading.load_sprite_sheet(
            fire_anim_path, 
            self.texture_size_x, 
            self.texture_size_y, 
            self.texture_buffer
        )
        fire_sfx_path: str = os.path.join(assets_path, data.get('fire_sfx', ""))
        self.fire_sfx: arcade.Sound = arcade.load_sound(fire_sfx_path)

        # Load reload assets if reloading is supported.
        if self.does_reload:
            reload_anim_path: str = os.path.join(assets_path, data.get('reload_animation', ""))
            self.reload_animation: Optional[Any] = resource_loading.load_sprite_sheet(
                reload_anim_path,
                self.texture_size_x,
                self.texture_size_y,
                self.texture_buffer
            )
            reload_sfx_path: str = os.path.join(assets_path, data.get('reload_sfx', ""))
            self.reload_sfx: Optional[arcade.Sound] = arcade.load_sound(reload_sfx_path)
        else:
            self.reload_animation = None
            self.reload_sfx = None

        # Load jam assets if jamming is supported.
        if self.does_jam:
            jam_anim_path: str = os.path.join(assets_path, data.get('jam_animation', ""))
            self.jam_animation: Optional[Any] = resource_loading.load_sprite_sheet(
                jam_anim_path,
                self.texture_size_x,
                self.texture_size_y,
                self.texture_buffer
            )
            jam_sfx_path: str = os.path.join(assets_path, data.get('jam_sfx', ""))
            self.jam_sfx: Optional[arcade.Sound] = arcade.load_sound(jam_sfx_path)
        else:
            self.jam_animation = None
            self.jam_sfx = None

        # Additional audio info.
        self.loudness: float = data.get('loudness', 0.0)

class Droppable:
    """
    Container for droppable entity data representing in-game items that can be picked up.

    Attributes:
        name (str): The name of the droppable entity.
        icon (str): Icon representing the entity.
        hitbox_x (float): The width of the hitbox.
        hitbox_y (float): The height of the hitbox.
        health (Union[int, float]): The current health of the entity.
        max_health (Union[int, float]): The maximum health of the entity.
        armor (Union[int, float]): The current armor value.
        max_armor (Union[int, float]): The maximum armor value.
        stamina (Union[int, float]): The current stamina.
        max_stamina (Union[int, float]): The maximum stamina.
        score (Union[int, float]): The score awarded when the item is collected.
        give_weapon_id (Union[int, str]): The identifier of a weapon granted on pickup.
        pistol_ammo (int): The amount of pistol ammunition contained.
        shotgun_ammo (int): The amount of shotgun ammunition contained.
        rifle_ammo (int): The amount of rifle ammunition contained.
        pickup_vfx (Any): Visual effect data to be displayed upon pickup.
        texture (arcade.Texture): Loaded texture asset for the item.
        texture_path (str): Full path to the texture file.
        pickup_sfx (arcade.Sound): Sound effect played when the item is picked up.
    """

    def __init__(self, name: str = "", icon: str = "", data: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize a Droppable entity with configuration data and load its associated assets.

        Args:
            name (str): The name of the droppable entity.
            icon (str): Icon identifier for the entity.
            data (Optional[Dict[str, Any]]): A dictionary containing configuration keys:
                - "hitbox_x": Width of the hitbox (numeric).
                - "hitbox_y": Height of the hitbox (numeric).
                - "health": Current health value.
                - "max_health": Maximum health value.
                - "armor": Current armor value.
                - "max_armor": Maximum armor value.
                - "stamina": Current stamina.
                - "max_stamina": Maximum stamina.
                - "score": Score awarded on pickup.
                - "give_weapon_id": Weapon identifier granted on pickup.
                - "pistol_ammo": Amount of pistol ammunition.
                - "shotgun_ammo": Amount of shotgun ammunition.
                - "rifle_ammo": Amount of rifle ammunition.
                - "pickup_vfx": Visual effect data for pickup.
                - "texture": Relative path (from the assets directory) to the texture file.
                - "pickup_sfx": Relative path (from the assets directory) to the pickup sound effect.
        """
        # Avoid mutable default arguments by assigning an empty dict if none is provided.
        if data is None:
            data = {}

        # Basic entity information
        self.name: str = name
        self.icon: str = icon

        # Entity physical attributes converted to proper types
        self.hitbox_x: float = float(data.get('hitbox_x', 0))
        self.hitbox_y: float = float(data.get('hitbox_y', 0))
        self.health: Union[int, float] = data.get('health', 0)
        self.max_health: Union[int, float] = data.get('max_health', 0)
        self.armor: Union[int, float] = data.get('armor', 0)
        self.max_armor: Union[int, float] = data.get('max_armor', 0)
        self.stamina: Union[int, float] = data.get('stamina', 0)
        self.max_stamina: Union[int, float] = data.get('max_stamina', 0)
        self.score: Union[int, float] = data.get('score', 0)
        self.give_weapon_id: Union[int, str] = data.get('give_weapon_id', "")
        self.pistol_ammo: int = data.get('pistol_ammo', 0)
        self.shotgun_ammo: int = data.get('shotgun_ammo', 0)
        self.rifle_ammo: int = data.get('rifle_ammo', 0)
        self.pickup_vfx: Any = data.get('pickup_vfx', None)

        # Load asset files using the resource path information provided by resource_loading
        from FireEngine.core.resources import resource_loading

        # Build the full texture path and load the texture asset using arcade.
        texture_filename: str = data.get('texture', "")
        self.texture_path: str = os.path.join(resource_loading.ASSETS, texture_filename)
        self.texture: arcade.Texture = arcade.load_texture(self.texture_path)

        # Build the full path for the pickup sound effect and load it.
        pickup_sfx_filename: str = data.get('pickup_sfx', "")
        pickup_sfx_path: str = os.path.join(resource_loading.ASSETS, pickup_sfx_filename)
        self.pickup_sfx: arcade.Sound = arcade.load_sound(pickup_sfx_path)