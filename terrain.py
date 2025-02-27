import random, math, pygame
import settings

def get_opposite_direction(direction):
    if direction == 'up':    return 'down'
    if direction == 'down':  return 'up'
    if direction == 'left':  return 'right'
    if direction == 'right': return 'left'
    return direction

def generate_river(grid, x, y, direction):
    river_length = random.randint(5, max(settings.GRID_WIDTH, settings.GRID_HEIGHT))
    for _ in range(river_length):
        if 0 <= x < settings.GRID_WIDTH and 0 <= y < settings.GRID_HEIGHT:
            grid[y][x] = 'river'
            if random.random() < 0.3:
                directions = ['up', 'down', 'left', 'right']
                directions.remove(get_opposite_direction(direction))
                direction = random.choice(directions)
            if direction == 'up':
                y -= 1
            elif direction == 'down':
                y += 1
            elif direction == 'left':
                x -= 1
            elif direction == 'right':
                x += 1
        else:
            break

def generate_terrain():
    grid = [['grass' for _ in range(settings.GRID_WIDTH)] for _ in range(settings.GRID_HEIGHT)]
    for x in range(settings.GRID_WIDTH):
        if random.random() < settings.RIVER_CHANCE:
            generate_river(grid, x, 0, 'down')
        if random.random() < settings.RIVER_CHANCE:
            generate_river(grid, x, settings.GRID_HEIGHT - 1, 'up')
    for y in range(settings.GRID_HEIGHT):
        if random.random() < settings.RIVER_CHANCE:
            generate_river(grid, 0, y, 'right')
        if random.random() < settings.RIVER_CHANCE:
            generate_river(grid, settings.GRID_WIDTH - 1, y, 'left')
    for y in range(settings.GRID_HEIGHT):
        for x in range(settings.GRID_WIDTH):
            if grid[y][x] == 'grass':
                if random.random() < settings.ROCK_CHANCE:
                    grid[y][x] = 'rock'
                elif random.random() < settings.TREE_CHANCE:
                    grid[y][x] = 'tree'
                elif random.random() < settings.BUSH_CHANCE:
                    grid[y][x] = 'bush'
    return grid

def draw_terrain(grid, screen):
    for y in range(settings.GRID_HEIGHT):
        for x in range(settings.GRID_WIDTH):
            pos_x = x * settings.TILE_SIZE
            pos_y = y * settings.TILE_SIZE
            tile = grid[y][x]
            if tile == 'grass':
                pygame.draw.rect(screen, settings.GREEN, (pos_x, pos_y, settings.TILE_SIZE, settings.TILE_SIZE))
            elif tile == 'river':
                pygame.draw.rect(screen, settings.BLUE, (pos_x, pos_y, settings.TILE_SIZE, settings.TILE_SIZE))
            elif tile == 'rock':
                pygame.draw.rect(screen, settings.GREEN, (pos_x, pos_y, settings.TILE_SIZE, settings.TILE_SIZE))
                pygame.draw.circle(screen, settings.GRAY,
                                   (pos_x + settings.TILE_SIZE // 2, pos_y + settings.TILE_SIZE // 2),
                                   settings.PLAYER_RADIUS + 5)
            elif tile == 'tree':
                pygame.draw.rect(screen, settings.GREEN, (pos_x, pos_y, settings.TILE_SIZE, settings.TILE_SIZE))
                pygame.draw.rect(screen, settings.BROWN,
                                 (pos_x + settings.TILE_SIZE // 2 - 3, pos_y + settings.TILE_SIZE // 2, 6, settings.TILE_SIZE // 2))
                pygame.draw.circle(screen, (0, 100, 0),
                                   (pos_x + settings.TILE_SIZE // 2, pos_y + settings.TILE_SIZE // 3),
                                   settings.PLAYER_RADIUS + 5)
            elif tile == 'bush':
                pygame.draw.rect(screen, settings.GREEN, (pos_x, pos_y, settings.TILE_SIZE, settings.TILE_SIZE))
                pygame.draw.circle(screen, settings.LIGHT_GREEN,
                                   (pos_x + settings.TILE_SIZE // 2, pos_y + settings.TILE_SIZE // 2),
                                   settings.PLAYER_RADIUS)

def get_terrain_at_position(grid, x, y):
    grid_x = int(x // settings.TILE_SIZE)
    grid_y = int(y // settings.TILE_SIZE)
    if 0 <= grid_x < settings.GRID_WIDTH and 0 <= grid_y < settings.GRID_HEIGHT:
        return grid[grid_y][grid_x]
    return 'grass'
