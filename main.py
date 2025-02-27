import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Set up the display
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Advanced Terrain Game with Player & Monsters")

# Define colors
GREEN = (34, 139, 34)     # Forest Green (for grass)
BLUE = (65, 105, 225)     # Royal Blue (for river)
BROWN = (139, 69, 19)     # Saddle Brown (for trees)
GRAY = (128, 128, 128)    # Gray (for rocks)
RED = (255, 0, 0)         # Red (for player)
BLACK = (0, 0, 0)         # Black (for monsters)
YELLOW = (255, 255, 0)    # Yellow (for cooldown indicator)

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
player_normal_speed = 5
player_x = screen_width // 2
player_y = screen_height // 2
player_hiding = False
player_hide_start_time = 0
player_hide_cooldown = False
player_hide_cooldown_start_time = 0
HIDE_MAX_TIME = 2000      # 2 seconds in milliseconds
HIDE_COOLDOWN_TIME = 10000  # 10 seconds in milliseconds

# Monster settings
monster_size = 25
monster_normal_speed = 2
monster_sight_range = 200  # Distance at which monsters can see the player
num_monsters = 7
monsters = []

# Game state
game_over = False
game_over_reason = ""

# Initialize the grid to track terrain
terrain_grid = []

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
                pygame.draw.circle(screen, GRAY, (pos_x + TILE_SIZE//2, pos_y + TILE_SIZE//2), player_radius + 5)
            elif grid[y][x] == 'tree':
                # Draw grass with a tree on top
                pygame.draw.rect(screen, GREEN, (pos_x, pos_y, TILE_SIZE, TILE_SIZE))
                # Tree trunk
                pygame.draw.rect(screen, BROWN, (pos_x + TILE_SIZE//2 - 3, pos_y + TILE_SIZE//2, 6, TILE_SIZE//2))
                # Tree top (circle)
                pygame.draw.circle(screen, (0, 100, 0), (pos_x + TILE_SIZE//2, pos_y + TILE_SIZE//3), player_radius + 5)

def get_terrain_at_position(x, y):
    # Convert pixel coordinates to grid coordinates and ensure indices are integers
    grid_x = int(x // TILE_SIZE)
    grid_y = int(y // TILE_SIZE)
    
    # Check if the coordinates are within the grid
    if 0 <= grid_x < grid_width and 0 <= grid_y < grid_height:
        return terrain_grid[grid_y][grid_x]
    
    # Default to grass if out of bounds
    return 'grass'


def initialize_monsters():
    monsters = []
    for _ in range(num_monsters):
        # Place monsters at random positions
        monster_x = random.randint(0, screen_width - monster_size)
        monster_y = random.randint(0, screen_height - monster_size)
        
        # Random initial movement direction and angle
        angle = random.uniform(0, 2 * math.pi)
        dx = math.cos(angle) * monster_normal_speed
        dy = math.sin(angle) * monster_normal_speed
        
        monsters.append({
            'x': monster_x,
            'y': monster_y,
            'dx': dx,
            'dy': dy,
            'angle': angle,
            'state': 'random',  # 'random' or 'chase'
            'speed': monster_normal_speed
        })
    return monsters

def move_monsters():
    for monster in monsters:
        # Update monster speed based on terrain
        terrain = get_terrain_at_position(monster['x'], monster['y'])
        if terrain == 'river':
            monster['speed'] = monster_normal_speed * 0.75
        else:
            monster['speed'] = monster_normal_speed
        
        # Check if monster can see player
        can_see_player = False
        if not player_hiding:
            distance_to_player = math.sqrt((player_x - monster['x'])**2 + (player_y - monster['y'])**2)
            if distance_to_player < monster_sight_range:
                can_see_player = True
        
        # Set monster state
        if can_see_player:
            monster['state'] = 'chase'
        else:
            # If was chasing but lost sight, keep going in same direction for a bit
            if monster['state'] == 'chase' and random.random() < 0.1:
                monster['state'] = 'random'
        
        # Move monster based on state
        if monster['state'] == 'chase':
            # Calculate direction to player
            dx = player_x - monster['x']
            dy = player_y - monster['y']
            length = math.sqrt(dx**2 + dy**2)
            if length > 0:
                dx = (dx / length) * monster['speed']
                dy = (dy / length) * monster['speed']
                monster['dx'] = dx
                monster['dy'] = dy
                monster['angle'] = math.atan2(dy, dx)
        else:
            # Random movement
            if random.random() < 0.03:
                monster['angle'] = random.uniform(0, 2 * math.pi)
                monster['dx'] = math.cos(monster['angle']) * monster['speed']
                monster['dy'] = math.sin(monster['angle']) * monster['speed']
        
        # Move monster
        monster['x'] += monster['dx']
        monster['y'] += monster['dy']
        
        # Bounce off screen edges
        if monster['x'] < 0 or monster['x'] > screen_width - monster_size:
            monster['dx'] *= -1
            monster['angle'] = math.atan2(monster['dy'], -monster['dx'])
            monster['x'] = max(0, min(monster['x'], screen_width - monster_size))
        if monster['y'] < 0 or monster['y'] > screen_height - monster_size:
            monster['dy'] *= -1
            monster['angle'] = math.atan2(-monster['dy'], monster['dx'])
            monster['y'] = max(0, min(monster['y'], screen_height - monster_size))

def draw_monsters():
    for monster in monsters:
        # Draw monster as an arrow pointing in its direction
        center_x = monster['x'] + monster_size / 2
        center_y = monster['y'] + monster_size / 2
        
        # Calculate arrow points
        tip_x = center_x + math.cos(monster['angle']) * monster_size / 1.5
        tip_y = center_y + math.sin(monster['angle']) * monster_size / 1.5
        
        # Calculate perpendicular points for arrow base
        perp_angle = monster['angle'] + math.pi/2
        perp_x = math.cos(perp_angle) * monster_size / 3
        perp_y = math.sin(perp_angle) * monster_size / 3
        
        base1_x = center_x - math.cos(monster['angle']) * monster_size / 3 + perp_x
        base1_y = center_y - math.sin(monster['angle']) * monster_size / 3 + perp_y
        
        base2_x = center_x - math.cos(monster['angle']) * monster_size / 3 - perp_x
        base2_y = center_y - math.sin(monster['angle']) * monster_size / 3 - perp_y
        
        # Draw arrow as a triangle
        pygame.draw.polygon(screen, BLACK, [(tip_x, tip_y), (base1_x, base1_y), (base2_x, base2_y)])
        
        # Draw a small circle at the center for visibility
        pygame.draw.circle(screen, BLACK, (int(center_x), int(center_y)), monster_size // 4)
        
        # Draw a red outline if chasing the player
        if monster['state'] == 'chase':
            pygame.draw.circle(screen, RED, (int(center_x), int(center_y)), monster_size // 2, 1)

def check_collisions():
    # Check if player is hiding too long
    global player_hiding, player_hide_start_time, player_hide_cooldown, player_hide_cooldown_start_time, game_over_reason
    
    if player_hiding:
        current_time = pygame.time.get_ticks()
        if current_time - player_hide_start_time > HIDE_MAX_TIME:
            game_over_reason = "You hid for too long!"
            return True
    
    # Skip collision detection if player is hiding
    if player_hiding:
        return False
    
    # Normal monster collision
    player_rect = pygame.Rect(player_x - player_radius, player_y - player_radius, 
                              player_radius * 2, player_radius * 2)
    
    for monster in monsters:
        # Create a rectangle for each monster
        monster_center_x = monster['x'] + monster_size / 2
        monster_center_y = monster['y'] + monster_size / 2
        monster_rect = pygame.Rect(monster_center_x - monster_size/2, monster_center_y - monster_size/2, 
                                  monster_size, monster_size)
        
        if player_rect.colliderect(monster_rect):
            game_over_reason = "Caught by a monster!"
            return True
    
    return False

def draw_game_over():
    # Semi-transparent overlay
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    
    # Game over text
    font = pygame.font.SysFont(None, 72)
    text = font.render("Game Over!", True, (255, 0, 0))
    text_rect = text.get_rect(center=(screen_width//2, screen_height//2 - 50))
    screen.blit(text, text_rect)
    
    # Reason text
    reason_font = pygame.font.SysFont(None, 36)
    reason_text = reason_font.render(game_over_reason, True, (255, 255, 255))
    reason_rect = reason_text.get_rect(center=(screen_width//2, screen_height//2))
    screen.blit(reason_text, reason_rect)
    
    # Restart instructions
    restart_font = pygame.font.SysFont(None, 36)
    restart_text = restart_font.render("Press R to restart", True, (255, 255, 255))
    restart_rect = restart_text.get_rect(center=(screen_width//2, screen_height//2 + 50))
    screen.blit(restart_text, restart_rect)

def draw_cooldown_indicator():
    global player_hide_cooldown, player_hide_cooldown_start_time
    current_time = pygame.time.get_ticks()
    
    if player_hide_cooldown:
        remaining = HIDE_COOLDOWN_TIME - (current_time - player_hide_cooldown_start_time)
        if remaining <= 0:
            player_hide_cooldown = False
        else:
            # Draw cooldown progress bar
            bar_width = 100
            bar_height = 10
            bar_x = 10
            bar_y = 50
            
            # Draw background
            pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            
            # Draw progress
            progress = remaining / HIDE_COOLDOWN_TIME
            pygame.draw.rect(screen, YELLOW, (bar_x, bar_y, bar_width * (1 - progress), bar_height))
            
            # Draw text
            cooldown_font = pygame.font.SysFont(None, 20)
            cooldown_text = cooldown_font.render("Hide Cooldown", True, (255, 255, 255))
            screen.blit(cooldown_text, (bar_x, bar_y - 20))

def reset_game():
    global player_x, player_y, monsters, terrain_grid, game_over, player_hiding
    global player_hide_start_time, player_hide_cooldown, player_hide_cooldown_start_time, game_over_reason
    
    player_x = screen_width // 2
    player_y = screen_height // 2
    terrain_grid = generate_terrain()
    monsters = initialize_monsters()
    game_over = False
    game_over_reason = ""
    player_hiding = False
    player_hide_start_time = 0
    player_hide_cooldown = False
    player_hide_cooldown_start_time = 0

# Generate initial terrain
terrain_grid = generate_terrain()

# Initialize monsters
monsters = initialize_monsters()

# Font for instructions
font = pygame.font.SysFont(None, 20)
instruction_text = font.render("WASD to move, SPACE for new terrain, R to restart", True, (255, 255, 255))
hide_text = font.render("Go to trees/rocks to hide (max 2s, 10s cooldown)", True, (255, 255, 255))

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    current_time = pygame.time.get_ticks()
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                # Generate new terrain when SPACE is pressed
                terrain_grid = generate_terrain()
                monsters = initialize_monsters()
            if event.key == pygame.K_r and game_over:
                # Restart the game
                reset_game()
    
    if not game_over:
        # Get terrain at player position
        player_terrain = get_terrain_at_position(player_x, player_y)
        
        # Check if player can hide
        if (player_terrain in ['tree', 'rock']) and not player_hide_cooldown:
            player_hiding = True
            if player_hide_start_time == 0:  # Just started hiding
                player_hide_start_time = current_time
        else:
            if player_hiding:  # Was hiding but moved out or cooldown
                player_hiding = False
                player_hide_cooldown = True
                player_hide_cooldown_start_time = current_time
                player_hide_start_time = 0
        
        # Set player speed based on terrain
        if player_terrain == 'river':
            player_speed = player_normal_speed * 0.5
        else:
            player_speed = player_normal_speed
        
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
    draw_terrain(terrain_grid)
    
    # Draw monsters
    draw_monsters()
    
    # Draw player (red circle)
    if not player_hiding:
        pygame.draw.circle(screen, RED, (player_x, player_y), player_radius)
    else:
        # Draw a fainter player when hiding
        pygame.draw.circle(screen, (255, 200, 200), (player_x, player_y), player_radius)
        
        # Draw hide time indicator
        hide_time = current_time - player_hide_start_time
        progress = min(hide_time / HIDE_MAX_TIME, 1)
        
        pygame.draw.arc(screen, (255, 0, 0), 
                       (player_x - player_radius - 5, player_y - player_radius - 5, 
                        player_radius * 2 + 10, player_radius * 2 + 10),
                       0, progress * 2 * math.pi, 3)
    
    # Draw cooldown indicator
    draw_cooldown_indicator()
    
    # Draw instructions
    screen.blit(instruction_text, (10, 10))
    screen.blit(hide_text, (10, 30))
    
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