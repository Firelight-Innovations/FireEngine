class GameManager:
    def __init__(self):
        # List to hold all registered objects
        self.registered_objects = []

    def register(self, obj):
        """Register an object to be managed."""
        self.registered_objects.append(obj)

    def unregister(self, obj):
        """Unregister an object from the manager."""
        if obj in self.registered_objects:
            self.registered_objects.remove(obj)

    def call_function(self, func_name, *args, **kwargs):
        """Call a specific function by name on all registered objects."""
        for obj in self.registered_objects:
            # Check if the object has the specified method
            if hasattr(obj, func_name) and callable(func := getattr(obj, func_name)):
                func(*args, **kwargs)

    ###############
    #   Updates   #
    ###############

    def update(self, delta_time):
        """Call 'on_update' on all registered objects."""
        self.call_function("on_update", delta_time)

    def render(self):
        """Call 'on_render' on all registered objects."""
        self.call_function("on_render")

    ################
    #   MOVEMENT   #
    ################

    def move_up(self, pressed):
        """Calls 'on_move_up' on all registered objects.'"""
        self.call_function("on_move_up", pressed)

    def move_down(self, pressed):
        """Calls 'on_move_down' on all registered objects.'"""
        self.call_function("on_move_down", pressed)

    def move_right(self, pressed):
        """Calls 'on_move_right' on all registered objects.'"""
        self.call_function("on_move_right", pressed)

    def move_left(self, pressed):
        """Calls 'on_move_left' on all registered objects.'"""
        self.call_function("on_move_left", pressed)