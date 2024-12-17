def singleton(cls):
    """A decorator to make a class a Singleton."""
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

def register(cls):
    """A decorator to tag classes for automatic registration with the GameManager."""
    import main
    original_init = cls.__init__

    def new_init(self, *args, **kwargs):
        # Call the original __init__ method
        original_init(self, *args, **kwargs)
        # Automatically register this instance with the GameManager
        main.Game.register(self)

    cls.__init__ = new_init
    return cls