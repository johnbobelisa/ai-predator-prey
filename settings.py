import pygame

# Screen and tile settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

# Colors
GREEN = (34, 139, 34)       # Grass
BLUE = (65, 105, 225)       # River
BROWN = (139, 69, 19)       # Tree trunk
GRAY = (128, 128, 128)      # Rock
RED = (255, 0, 0)           # Player
BLACK = (0, 0, 0)           # Monsters
YELLOW = (255, 255, 0)      # Cooldown indicator
LIGHT_GREEN = (144, 238, 144)  # Bush
PURPLE = (128, 0, 128)      # Power pellet / Power mode

# Terrain generation probabilities
RIVER_CHANCE = 0.1
ROCK_CHANCE = 0.03
TREE_CHANCE = 0.08
BUSH_CHANCE = 0.04

# Player settings
PLAYER_RADIUS = 15
PLAYER_NORMAL_SPEED = 5
HIDE_MAX_TIME = 2000       # milliseconds
HIDE_COOLDOWN_TIME = 10000 # milliseconds
POWER_DURATION = 5000      # milliseconds

# Monster settings
MONSTER_SIZE = 25
MONSTER_NORMAL_SPEED = 2
MONSTER_SIGHT_RANGE = 200
NUM_MONSTERS = 7

# Power pellet settings
POWER_PELLET_RADIUS = 10
POWER_PELLET_SPAWN_MIN = 10000  # milliseconds
POWER_PELLET_SPAWN_MAX = 30000  # milliseconds
