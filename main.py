import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up the display
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Random Terrain Generator")

# Define colors
GREEN = (34, 139, 34)  # Forest Green (for grass)
BLUE = (65, 105, 225)  # Royal Blue (for river)
BROWN = (139, 69, 19)  # Saddle Brown (for trees)
GRAY = (128, 128, 128)  # Gray (for rocks)

# Tile size
TILE_SIZE = 40

# Calculate grid dimensions
grid_width = screen_width // TILE_SIZE
grid_height = screen_height // TILE_SIZE

# Terrain generation parameters
RIVER_CHANCE = 0.1  # Chance of starting a river at any edge tile
ROCK_CHANCE = 0.05  # Chance of placing a rock on a grass tile
TREE_CHANCE = 0.15  # Chance of placing a tree on a grass tile

def generate_terrain():
    # Initialize grid with grass
    grid = [['grass' for _ in range(grid_width)] for _ in range(grid_height)]
    
    # Generate rivers (simple algorithm)
    for x in range(grid_width):
        # Check top and bottom edges for river starts
        if random.random() < RIVER_CHANCE:
            generate_river(grid, x, 0, 'down')
        if random.random() < RIVER_CHANCE:
            generate_river(grid, x, grid_height - 1, 'up')
    
    for y in range(grid_height):
        # Check left and right edges for river starts
        if random.random() < RIVER_CHANCE:
            generate_river(grid, 0, y, 'right')
        if random.random() < RIVER_CHANCE:
            generate_river(grid, grid_width - 1, y, 'left')
    
    # Add rocks and trees to grass tiles
    for y in range(grid_height):
        for x in range(grid_width):
            if grid[y][x] == 'grass':
                if random.random() < ROCK_CHANCE:
                    grid[y][x] = 'rock'
                elif random.random() < TREE_CHANCE:
                    grid[y][x] = 'tree'
    
    return grid

def generate_river(grid, x, y, direction):
    # River length
    river_length = random.randint(5, max(grid_width, grid_height))
    
    # Generate river path
    for _ in range(river_length):
        if 0 <= x < grid_width and 0 <= y < grid_height:
            grid[y][x] = 'river'
            
            # Randomly change direction occasionally
            if random.random() < 0.3:
                directions = ['up', 'down', 'left', 'right']
                directions.remove(get_opposite_direction(direction))
                direction = random.choice(directions)
            
            # Move in the current direction
            if direction == 'up':
                y -= 1
            elif direction == 'down':
                y += 1
            elif direction == 'left':
                x -= 1
            elif direction == 'right':
                x += 1
        else:
            break  # Stop if we go out of bounds

def get_opposite_direction(direction):
    if direction == 'up': return 'down'
    if direction == 'down': return 'up'
    if direction == 'left': return 'right'
    if direction == 'right': return 'left'
    return direction

def draw_terrain(grid):
    for y in range(grid_height):
        for x in range(grid_width):
            # Calculate position
            pos_x = x * TILE_SIZE
            pos_y = y * TILE_SIZE
            
            # Draw based on tile type
            if grid[y][x] == 'grass':
                pygame.draw.rect(screen, GREEN, (pos_x, pos_y, TILE_SIZE, TILE_SIZE))
            elif grid[y][x] == 'river':
                pygame.draw.rect(screen, BLUE, (pos_x, pos_y, TILE_SIZE, TILE_SIZE))
            elif grid[y][x] == 'rock':
                # Draw grass with a rock on top
                pygame.draw.rect(screen, GREEN, (pos_x, pos_y, TILE_SIZE, TILE_SIZE))
                pygame.draw.circle(screen, GRAY, (pos_x + TILE_SIZE//2, pos_y + TILE_SIZE//2), TILE_SIZE//3)
            elif grid[y][x] == 'tree':
                # Draw grass with a tree on top (simple representation)
                pygame.draw.rect(screen, GREEN, (pos_x, pos_y, TILE_SIZE, TILE_SIZE))
                # Tree trunk
                pygame.draw.rect(screen, BROWN, (pos_x + TILE_SIZE//2 - 2, pos_y + TILE_SIZE//2, 4, TILE_SIZE//2))
                # Tree top (circle)
                pygame.draw.circle(screen, (0, 100, 0), (pos_x + TILE_SIZE//2, pos_y + TILE_SIZE//3), TILE_SIZE//3)

# Generate initial terrain
terrain = generate_terrain()

# Font for instructions
font = pygame.font.SysFont(None, 24)
instruction_text = font.render("Press SPACE to generate new terrain", True, (255, 255, 255))

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Generate new terrain when SPACE is pressed
                terrain = generate_terrain()
    
    # Fill the screen
    screen.fill((0, 0, 0))  # Start with black
    
    # Draw the terrain
    draw_terrain(terrain)
    
    # Draw instructions
    screen.blit(instruction_text, (10, 10))
    
    # Update the display
    pygame.display.flip()
    
    # Control the game speed
    pygame.time.Clock().tick(60)  # 60 frames per second

# Quit Pygame
pygame.quit()
sys.exit()