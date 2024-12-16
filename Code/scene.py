# Importing other scripts
from Code import scene

# Wall: '█'
# Door: '░'
# Open door: '░'
# Empty Space: ' '
# Player Spawn:'*'
# Enemy Spawn: '$'

'''
mapData = ['██████████',
           '█   █    █',
           '█*  ▓  $ █',
           '█   █    █',
           '██████████']

'''
mapData = ['██████████████▓██████████████████████',
           '█   █   $█  ██  █   $    █ █        █',
           '█*  ▓  $ ▓   $  █        ▓ ▓   $    █',
           '█   █    █  ██ $██████████ █     $  █',
           '██▓███████████▓███████████ ██████████',
           '█      $ █ $    █   $    ▓$▓     $  █',
           '█    $   █     $█        █ █  $     █',
           '█▓█████████████▓██████████▓██████████',
           '█    $            $           $     █',
           '████▓████▓███████▓███▓████▓██████████',
           '█  $   █       █   █   $█  $      $ █',
           '█  █   █  $█   █   █    █         $ █',
           '█  █   █   █   █ $ █    █   $       █',
           '█ $█ $     █$ $█   █ $  █       $   █',
           '█████████████████████████████████████']
           
def get_player_spawn():
    x = 0
    y = 0

    for row_index, row in enumerate(scene.mapData):
        for col_index, tile in enumerate(row):
            x = col_index
            y = row_index# Invert y-axis to match screencoordinates
            if tile == '*':  # Player Spawn
                return x + 0.5, y + 0.5
