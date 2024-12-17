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

def get_player_spawn_x():
    x = 0
    y = 0

    for row_index, row in enumerate(mapData):
        for col_index, tile in enumerate(row):
            x = col_index
            y = row_index# Invert y-axis to match screencoordinates
            if tile == '*':  # Player Spawn
                return x + 0.5

def get_player_spawn_y():
    x = 0
    y = 0

    for row_index, row in enumerate(mapData):
        for col_index, tile in enumerate(row):
            x = col_index
            y = row_index# Invert y-axis to match screencoordinates
            if tile == '*':  # Player Spawn
                return y + 0.5