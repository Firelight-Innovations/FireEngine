registered_objects = []

from singleton import singleton

@singleton
class GameManager:
    def __init__(self):
        return

    def register(self, obj: object):
        """Register an object to be managed."""
        registered_objects.append(obj)

    def unregister(self, obj: object):
        """Unregister an object from the manager."""
        if obj in registered_objects:
            registered_objects.remove(obj)

    def call_function(self, func_name: str, *args: object, **kwargs: object):
        """Call a specific function by name on all registered objects."""
        for obj in registered_objects:
            # Check if the object has the specified method
            if hasattr(obj, func_name) and callable(func := getattr(obj, func_name)):
                func(*args, **kwargs)

    ###############
    #   Updates   #
    ###############

    def update(self, delta_time: float):
        """Call 'on_update' on all registered objects."""
        self.call_function("on_update", delta_time)

        # import main
        # print(f'{main.Player.player_x}')

    def render(self):
        """Call 'on_render' on all registered objects. Priority determines when an object is rendered on the screen, lower priorites are rendered first."""
        self.call_function("on_render")

    ################
    #   MOVEMENT   #
    ################

    def move_up(self, pressed: bool):
        """Calls 'on_move_up' on all registered objects."""
        self.call_function("on_move_up", pressed)

    def move_down(self, pressed: bool):
        """Calls 'on_move_down' on all registered objects."""
        self.call_function("on_move_down", pressed)

    def move_right(self, pressed: bool):
        """Calls 'on_move_right' on all registered objects."""
        self.call_function("on_move_right", pressed)

    def move_left(self, pressed: bool):
        """Calls 'on_move_left' on all registered objects."""
        self.call_function("on_move_left", pressed)

    ####################
    #    CAMERA MOVE   #
    ####################

    def turn_right(self, pressed: bool):
        """Calls 'on_turn_right' on all registered objects."""
        self.call_function("on_turn_right", pressed)

    def turn_left(self, pressed: bool):
        """Calls 'on_turn_left' on all registered objects."""
        self.call_function("on_turn_left", pressed)

    ##########################
    #   WORLD INTERACTIONS   #
    ##########################
    
    def on_shoot(self):
        """Calls 'on_shoot' on all registered objects."""
        self.call_function("on_shoot")