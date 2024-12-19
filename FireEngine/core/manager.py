registered_objects = []

from FireEngine.core.decorators import singleton

@singleton
class game_manager:
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

    def start(self):
        """Call 'on_start' on all registered objects."""
        self.call_function("on_start")

    def update(self, delta_time: float):
        """Call 'on_update' on all registered objects."""
        self.call_function("on_update", delta_time)

    def render(self):
        """
        Call 'on_render' on all registered objects.
        Priority determines when an object is rendered on the screen,
        lower priorities are rendered first.
        """
        # Filter objects that have an 'on_render' method
        renderable_objects = [
            obj for obj in registered_objects if hasattr(obj, "on_render")
        ]

        # Sort objects by their priority (default to 100 if no priority is set)
        sorted_objects = sorted(
            renderable_objects,
            key=lambda obj: getattr(obj, "priority", 100)  # Default priority is 100
        )

        # Call 'on_render' for each sorted object
        for obj in sorted_objects:
            obj.on_render()

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

    def shoot(self):
        """Calls 'on_shoot' on all registered objects."""
        self.call_function("on_shoot")

    def interact(self):
        """Calls 'on_interact' on all registered objects."""
        self.call_function("on_interact")

Game = game_manager()