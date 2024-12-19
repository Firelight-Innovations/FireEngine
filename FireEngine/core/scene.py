TILE_SIZE = 20  # Size of each tile on the map

# Wall: '█'
# Door: '░'
# Open door: '░'
# Empty Space: ' '
# Player Spawn:'*'
# Enemy Spawn: '$'

scene_data = []

def get_player_spawn_x():
    x = 0

    for row_index, row in enumerate(scene_data):
        for col_index, tile in enumerate(row):
            x = col_index
            y = row_index# Invert y-axis to match screencoordinates
            if tile == '*':  # Player Spawn
                return x + 0.5

def get_player_spawn_y():
    x = 0
    y = 0

    for row_index, row in enumerate(scene_data):
        for col_index, tile in enumerate(row):
            x = col_index
            y = row_index# Invert y-axis to match screencoordinates
            if tile == '*':  # Player Spawn
                return y + 0.5