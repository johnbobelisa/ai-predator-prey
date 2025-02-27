import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up the display
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Random Terrain Generator with Player & Monsters")

# Define colors
GREEN = (34, 139, 34)  # Forest Green (for grass)
BLUE = (65, 105, 225)  # Royal Blue (for river)
BROWN = (139, 69, 19)  # Saddle Brown (for trees)
GRAY = (128, 128, 128)  # Gray (for rocks)
RED = (255, 0, 0)      # Red (for player)
BLACK = (0, 0, 0)      # Black (for monsters)

# Tile size
TILE_SIZE = 40

# Calculate grid dimensions
grid_width = screen_width // TILE_SIZE
grid_height = screen_height // TILE_SIZE

# Terrain generation parameters
RIVER_CHANCE = 0.1  # Chance of starting a river at any edge tile
ROCK_CHANCE = 0.05  # Chance of placing a rock on a grass tile
TREE_CHANCE = 0.15  # Chance of placing a tree on a grass tile

# Player settings
player_radius = 15
player_speed = 5
player_x = screen_width // 2
player_y = screen_height // 2

# Monster settings
monster_size = 20
monster_speed = 2
num_monsters = 10
monsters = []

# Game state
game_over = False

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

def initialize_monsters():
    monsters = []
    for _ in range(num_monsters):
        # Place monsters at random positions
        monster_x = random.randint(0, screen_width - monster_size)
        monster_y = random.randint(0, screen_height - monster_size)
        
        # Random initial movement direction
        dx = random.choice([-1, 0, 1]) * monster_speed
        dy = random.choice([-1, 0, 1]) * monster_speed
        if dx == 0 and dy == 0:  # Ensure monster moves
            dx = monster_speed
        
        monsters.append({
            'x': monster_x,
            'y': monster_y,
            'dx': dx,
            'dy': dy
        })
    return monsters

def move_monsters():
    for monster in monsters:
        # Randomly change direction occasionally
        if random.random() < 0.05:
            monster['dx'] = random.choice([-1, 0, 1]) * monster_speed
            monster['dy'] = random.choice([-1, 0, 1]) * monster_speed
            if monster['dx'] == 0 and monster['dy'] == 0:
                monster['dx'] = monster_speed  # Ensure monster moves
        
        # Move monster
        monster['x'] += monster['dx']
        monster['y'] += monster['dy']
        
        # Bounce off screen edges
        if monster['x'] < 0 or monster['x'] > screen_width - monster_size:
            monster['dx'] *= -1
            monster['x'] = max(0, min(monster['x'], screen_width - monster_size))
        if monster['y'] < 0 or monster['y'] > screen_height - monster_size:
            monster['dy'] *= -1
            monster['y'] = max(0, min(monster['y'], screen_height - monster_size))

def draw_monsters():
    for monster in monsters:
        pygame.draw.rect(screen, BLACK, (monster['x'], monster['y'], monster_size, monster_size))

def check_collisions():
    player_rect = pygame.Rect(player_x - player_radius, player_y - player_radius, 
                              player_radius * 2, player_radius * 2)
    
    for monster in monsters:
        monster_rect = pygame.Rect(monster['x'], monster['y'], monster_size, monster_size)
        if player_rect.colliderect(monster_rect):
            return True
    
    return False

def draw_game_over():
    font = pygame.font.SysFont(None, 72)
    text = font.render("Game Over!", True, (255, 0, 0))
    text_rect = text.get_rect(center=(screen_width//2, screen_height//2))
    screen.blit(text, text_rect)
    
    # Additional instructions for restarting
    restart_font = pygame.font.SysFont(None, 36)
    restart_text = restart_font.render("Press R to restart", True, (255, 255, 255))
    restart_rect = restart_text.get_rect(center=(screen_width//2, screen_height//2 + 50))
    screen.blit(restart_text, restart_rect)

def reset_game():
    global player_x, player_y, monsters, terrain, game_over
    player_x = screen_width // 2
    player_y = screen_height // 2
    terrain = generate_terrain()
    monsters = initialize_monsters()
    game_over = False

# Generate initial terrain
terrain = generate_terrain()

# Initialize monsters
monsters = initialize_monsters()

# Font for instructions
font = pygame.font.SysFont(None, 24)
instruction_text = font.render("WASD to move, SPACE for new terrain, R to restart", True, (255, 255, 255))

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                # Generate new terrain when SPACE is pressed
                terrain = generate_terrain()
            if event.key == pygame.K_r and game_over:
                # Restart the game
                reset_game()
    
    if not game_over:
        # Player movement using WASD
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player_y -= player_speed
        if keys[pygame.K_s]:
            player_y += player_speed
        if keys[pygame.K_a]:
            player_x -= player_speed
        if keys[pygame.K_d]:
            player_x += player_speed
        
        # Keep player within screen bounds
        player_x = max(player_radius, min(player_x, screen_width - player_radius))
        player_y = max(player_radius, min(player_y, screen_height - player_radius))
        
        # Move monsters
        move_monsters()
        
        # Check for collisions
        if check_collisions():
            game_over = True
    
    # Fill the screen
    screen.fill((0, 0, 0))  # Start with black
    
    # Draw the terrain
    draw_terrain(terrain)
    
    # Draw monsters
    draw_monsters()
    
    # Draw player (red circle)
    pygame.draw.circle(screen, RED, (player_x, player_y), player_radius)
    
    # Draw instructions
    screen.blit(instruction_text, (10, 10))
    
    # Draw game over message if game is over
    if game_over:
        draw_game_over()
    
    # Update the display
    pygame.display.flip()
    
    # Control the game speed
    clock.tick(60)  # 60 frames per second

# Quit Pygame
pygame.quit()
sys.exit()