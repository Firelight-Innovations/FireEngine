TILE_SIZE = 20  # Size of each tile on the map

# Wall: '█'
# Door: '░'
# Open door: '░'
# Empty Space: ' '
# Player Spawn:'*'
# Enemy Spawn: '$'

scene_data = []

def get_player_spawn():
    x = 0
    y = 0

    for row_index, row in enumerate(scene_data):
        for col_index, tile in enumerate(row):
            x = col_index
            y = row_index# Invert y-axis to match screencoordinates
            if tile == '*':  # Player Spawn
                scene_data[y] = scene_data[y][:x] + ' ' + scene_data[y][x+1:]
                return x + 0.5, y + 0.5