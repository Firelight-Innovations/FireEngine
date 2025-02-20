from FireEngine.core.decorators import register, singleton
from FireEngine.player import player

@register
@singleton
class death():
    def on_update():
        if(player.Player.health <= 0):
            # player dies
            print("You died!")
