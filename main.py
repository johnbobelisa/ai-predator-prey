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
LIGHT_GREEN = (144, 238, 144)  # Light Green (for bushes)
PURPLE = (128, 0, 128)    # Purple (for power pellet)

# Tile size
TILE_SIZE = 40

# Calculate grid dimensions
grid_width = screen_width // TILE_SIZE
grid_height = screen_height // TILE_SIZE

# Terrain generation parameters (reduced trees and rocks)
RIVER_CHANCE = 0.1  # Chance of starting a river at any edge tile
ROCK_CHANCE = 0.03  # Reduced chance of placing a rock (was 0.05)
TREE_CHANCE = 0.08  # Reduced chance of placing a tree (was 0.15)
BUSH_CHANCE = 0.04  # Chance of placing a bush

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
player_powered = False
player_power_start_time = 0
POWER_DURATION = 5000     # 5 seconds in milliseconds

# Monster settings
monster_size = 25
monster_normal_speed = 2
monster_sight_range = 200  # Distance at which monsters can see the player
num_monsters = 7
monsters = []
monsters_eaten = 0

# Power pellet settings
power_pellet_active = False
power_pellet_x = 0
power_pellet_y = 0
power_pellet_radius = 10
power_pellet_spawn_min = 10000  # 10 seconds minimum
power_pellet_spawn_max = 30000  # 30 seconds maximum
power_pellet_next_spawn = 0

# Game state
game_over = False
game_over_reason = ""
game_start_time = 0
game_end_time = 0
current_score = 0

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
    
    # Add rocks, trees and bushes to grass tiles
    for y in range(grid_height):
        for x in range(grid_width):
            if grid[y][x] == 'grass':
                if random.random() < ROCK_CHANCE:
                    grid[y][x] = 'rock'
                elif random.random() < TREE_CHANCE:
                    grid[y][x] = 'tree'
                elif random.random() < BUSH_CHANCE:
                    grid[y][x] = 'bush'
    
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
            elif grid[y][x] == 'bush':
                # Draw grass with a bush on top
                pygame.draw.rect(screen, GREEN, (pos_x, pos_y, TILE_SIZE, TILE_SIZE))
                pygame.draw.circle(screen, LIGHT_GREEN, (pos_x + TILE_SIZE//2, pos_y + TILE_SIZE//2), player_radius)

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
        # Place monsters at the edge of the map
        edge = random.randint(0, 3)  # 0: top, 1: right, 2: bottom, 3: left
        
        if edge == 0:  # Top
            monster_x = random.randint(0, screen_width - monster_size)
            monster_y = random.randint(0, 50)
        elif edge == 1:  # Right
            monster_x = random.randint(screen_width - 50, screen_width - monster_size)
            monster_y = random.randint(0, screen_height - monster_size)
        elif edge == 2:  # Bottom
            monster_x = random.randint(0, screen_width - monster_size)
            monster_y = random.randint(screen_height - 50, screen_height - monster_size)
        else:  # Left
            monster_x = random.randint(0, 50)
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
            'state': 'random',  # 'random', 'chase', or 'flee'
            'speed': monster_normal_speed,
            'eaten': False
        })
    return monsters

def move_monsters():
    for monster in monsters:
        if monster['eaten']:
            continue
            
        # Update monster speed based on terrain
        terrain = get_terrain_at_position(monster['x'], monster['y'])
        if terrain == 'river':
            monster['speed'] = monster_normal_speed * 0.75
        else:
            monster['speed'] = monster_normal_speed
        
        # Check if monster can see player or player is powered up
        can_see_player = False
        if not player_hiding:
            distance_to_player = math.sqrt((player_x - monster['x'])**2 + (player_y - monster['y'])**2)
            if distance_to_player < monster_sight_range:
                can_see_player = True
        
        # Set monster state
        if player_powered:
            monster['state'] = 'flee'
        elif can_see_player:
            monster['state'] = 'chase'
        else:
            # If was chasing/fleeing but lost sight, keep going in same direction for a bit
            if monster['state'] != 'random' and random.random() < 0.1:
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
        elif monster['state'] == 'flee':
            # Calculate direction away from player
            dx = monster['x'] - player_x
            dy = monster['y'] - player_y
            length = math.sqrt(dx**2 + dy**2)
            if length > 0:
                dx = (dx / length) * monster['speed'] * 0.8  # Flee slightly slower
                dy = (dy / length) * monster['speed'] * 0.8
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
        new_x = monster['x'] + monster['dx']
        new_y = monster['y'] + monster['dy']
        
        # Check if new position is in a rock
        new_terrain = get_terrain_at_position(new_x, new_y)
        if new_terrain != 'rock':
            monster['x'] = new_x
            monster['y'] = new_y
        else:
            # Bounce off the rock
            monster['dx'] *= -1
            monster['dy'] *= -1
            monster['angle'] = math.atan2(monster['dy'], monster['dx'])
        
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
        if monster['eaten']:
            continue
            
        # Monster color based on state
        monster_color = BLACK
        if monster['state'] == 'flee':
            monster_color = (0, 0, 255)  # Blue when fleeing
        
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
        pygame.draw.polygon(screen, monster_color, [(tip_x, tip_y), (base1_x, base1_y), (base2_x, base2_y)])
        
        # Draw a small circle at the center for visibility
        pygame.draw.circle(screen, monster_color, (int(center_x), int(center_y)), monster_size // 4)
        
        # Draw a red outline if chasing the player
        if monster['state'] == 'chase':
            pygame.draw.circle(screen, RED, (int(center_x), int(center_y)), monster_size // 2, 1)

def check_collisions():
    global player_hiding, player_hide_start_time, player_hide_cooldown, player_hide_cooldown_start_time
    global game_over_reason, player_powered, monsters_eaten, power_pellet_active, power_pellet_next_spawn, player_power_start_time

    # Check if player power mode has expired
    if player_powered:
        current_time = pygame.time.get_ticks()
        if current_time - player_power_start_time > POWER_DURATION:
            player_powered = False

    # Check if player is hiding too long
    if player_hiding:
        current_time = pygame.time.get_ticks()
        if current_time - player_hide_start_time > HIDE_MAX_TIME:
            game_over_reason = "You hid for too long!"
            return True

    # Skip monster collision detection if player is hiding
    if player_hiding:
        return False

    # Check collision with power pellet
    if power_pellet_active:
        distance_to_pellet = math.sqrt((player_x - power_pellet_x)**2 + (player_y - power_pellet_y)**2)
        if distance_to_pellet < player_radius + power_pellet_radius:
            power_pellet_active = False
            player_powered = True
            player_power_start_time = pygame.time.get_ticks()
            # Schedule next pellet spawn
            power_pellet_next_spawn = pygame.time.get_ticks() + random.randint(power_pellet_spawn_min, power_pellet_spawn_max)

    # Monster collisions
    player_rect = pygame.Rect(player_x - player_radius, player_y - player_radius, 
                              player_radius * 2, player_radius * 2)
    
    for monster in monsters:
        if monster['eaten']:
            continue
        
        monster_center_x = monster['x'] + monster_size / 2
        monster_center_y = monster['y'] + monster_size / 2
        monster_rect = pygame.Rect(monster_center_x - monster_size/2, monster_center_y - monster_size/2, 
                                  monster_size, monster_size)
        
        if player_rect.colliderect(monster_rect):
            if player_powered:
                monster['eaten'] = True
                monsters_eaten += 1
            else:
                game_over_reason = "Caught by a monster!"
                return True

    return False

def check_terrain_collision():
    global player_hiding, player_hide_start_time, player_hide_cooldown, player_hide_cooldown_start_time
    terrain = get_terrain_at_position(player_x, player_y)
    
    # Player can hide only in trees and bushes now, not rocks
    if terrain in ['tree', 'bush'] and not player_hide_cooldown:
        player_hiding = True
        if player_hide_start_time == 0:  # Just started hiding
            player_hide_start_time = pygame.time.get_ticks()
    else:
        if player_hiding:  # Was hiding but moved out or cooldown
            player_hiding = False
            player_hide_cooldown = True
            player_hide_cooldown_start_time = pygame.time.get_ticks()
            player_hide_start_time = 0
    
    return terrain

def draw_game_over():
    # Semi-transparent overlay
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    
    # Use the frozen game_end_time instead of the current time
    survival_time = (game_end_time - game_start_time) // 1000  # in seconds
    final_score = survival_time * (monsters_eaten + 1)
    
    # Game over text
    font = pygame.font.SysFont(None, 72)
    text = font.render("Game Over!", True, (255, 0, 0))
    text_rect = text.get_rect(center=(screen_width//2, screen_height//2 - 80))
    screen.blit(text, text_rect)
    
    # Reason text
    reason_font = pygame.font.SysFont(None, 36)
    reason_text = reason_font.render(game_over_reason, True, (255, 255, 255))
    reason_rect = reason_text.get_rect(center=(screen_width//2, screen_height//2 - 30))
    screen.blit(reason_text, reason_rect)
    
    # Score text
    score_font = pygame.font.SysFont(None, 48)
    score_text = score_font.render(f"Final Score: {final_score}", True, (255, 255, 0))
    score_rect = score_text.get_rect(center=(screen_width//2, screen_height//2 + 20))
    screen.blit(score_text, score_rect)
    
    # Stats text
    stats_font = pygame.font.SysFont(None, 30)
    time_text = stats_font.render(f"Survival Time: {survival_time} seconds", True, (255, 255, 255))
    time_rect = time_text.get_rect(center=(screen_width//2, screen_height//2 + 60))
    screen.blit(time_text, time_rect)
    
    monsters_text = stats_font.render(f"Monsters Eaten: {monsters_eaten}", True, (255, 255, 255))
    monsters_rect = monsters_text.get_rect(center=(screen_width//2, screen_height//2 + 90))
    screen.blit(monsters_text, monsters_rect)
    
    # Restart instructions
    restart_font = pygame.font.SysFont(None, 36)
    restart_text = restart_font.render("Press R to restart", True, (255, 255, 255))
    restart_rect = restart_text.get_rect(center=(screen_width//2, screen_height//2 + 140))
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
            
            pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            progress = remaining / HIDE_COOLDOWN_TIME
            pygame.draw.rect(screen, YELLOW, (bar_x, bar_y, bar_width * (1 - progress), bar_height))
            
            cooldown_font = pygame.font.SysFont(None, 20)
            cooldown_text = cooldown_font.render("Hide Cooldown", True, (255, 255, 255))
            screen.blit(cooldown_text, (bar_x, bar_y - 20))

def draw_power_indicator():
    if player_powered:
        current_time = pygame.time.get_ticks()
        remaining = POWER_DURATION - (current_time - player_power_start_time)
        
        bar_width = 100
        bar_height = 10
        bar_x = 10
        bar_y = 80
        
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        progress = remaining / POWER_DURATION
        pygame.draw.rect(screen, PURPLE, (bar_x, bar_y, bar_width * progress, bar_height))
        
        power_font = pygame.font.SysFont(None, 20)
        power_text = power_font.render("Power Mode!", True, PURPLE)
        screen.blit(power_text, (bar_x, bar_y - 20))

def spawn_power_pellet():
    global power_pellet_active, power_pellet_x, power_pellet_y
    valid_position = False
    while not valid_position:
        x = random.randint(power_pellet_radius * 2, screen_width - power_pellet_radius * 2)
        y = random.randint(power_pellet_radius * 2, screen_height - power_pellet_radius * 2)
        terrain = get_terrain_at_position(x, y)
        if terrain not in ['rock', 'river']:
            valid_position = True
            power_pellet_x = x
            power_pellet_y = y
            power_pellet_active = True

def draw_power_pellet():
    if power_pellet_active:
        size_mod = math.sin(pygame.time.get_ticks() / 200) * 2
        pygame.draw.circle(screen, PURPLE, (power_pellet_x, power_pellet_y), 
                           power_pellet_radius + size_mod)
        pygame.draw.circle(screen, (255, 255, 255), (power_pellet_x, power_pellet_y), 
                           (power_pellet_radius + size_mod) * 0.6)

def draw_score():
    # Use game_end_time if game is over, otherwise use the current time
    current_time = game_end_time if game_over else pygame.time.get_ticks()
    survival_time = (current_time - game_start_time) // 1000  # in seconds
    score = survival_time * (monsters_eaten + 1)
    
    score_font = pygame.font.SysFont(None, 36)
    score_text = score_font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (screen_width - score_text.get_width() - 10, 10))
    
    monsters_font = pygame.font.SysFont(None, 24)
    monsters_text = monsters_font.render(f"Monsters Eaten: {monsters_eaten}", True, (255, 255, 255))
    screen.blit(monsters_text, (screen_width - monsters_text.get_width() - 10, 50))
    
    time_text = monsters_font.render(f"Time: {survival_time}s", True, (255, 255, 255))
    screen.blit(time_text, (screen_width - time_text.get_width() - 10, 80))


def reset_game():
    global player_x, player_y, monsters, terrain_grid, game_over, player_hiding
    global player_hide_start_time, player_hide_cooldown, player_hide_cooldown_start_time, game_over_reason
    global power_pellet_active, power_pellet_next_spawn, player_powered, monsters_eaten, game_start_time, game_end_time
    
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
    power_pellet_active = False
    power_pellet_next_spawn = pygame.time.get_ticks() + random.randint(power_pellet_spawn_min // 2, power_pellet_spawn_max // 2)
    player_powered = False
    monsters_eaten = 0
    game_start_time = pygame.time.get_ticks()
    game_end_time = 0  # Reset the end time

# Generate initial terrain
terrain_grid = generate_terrain()

# Initialize monsters
monsters = initialize_monsters()

# Setup initial power pellet spawn time
power_pellet_next_spawn = pygame.time.get_ticks() + random.randint(power_pellet_spawn_min // 2, power_pellet_spawn_max // 2)

# Set game start time
game_start_time = pygame.time.get_ticks()

# Font for instructions
font = pygame.font.SysFont(None, 20)
instruction_text = font.render("WASD to move, SPACE for new terrain, R to restart", True, (255, 255, 255))
hide_text = font.render("Hide in trees/bushes (max 2s, 10s cooldown), eat power pellets to hunt monsters", True, (255, 255, 255))

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                terrain_grid = generate_terrain()
                monsters = initialize_monsters()
            if event.key == pygame.K_r and game_over:
                reset_game()
    
    if not game_over:
        if not power_pellet_active and current_time >= power_pellet_next_spawn:
            spawn_power_pellet()
        
        terrain = check_terrain_collision()
        
        player_speed = player_normal_speed
        if terrain == 'river':
            player_speed *= 0.5
        
        prev_x, prev_y = player_x, player_y
        keys = pygame.key.get_pressed()
        moved = False
        
        if keys[pygame.K_w]:
            player_y -= player_speed
            moved = True
        if keys[pygame.K_s]:
            player_y += player_speed
            moved = True
        if keys[pygame.K_a]:
            player_x -= player_speed
            moved = True
        if keys[pygame.K_d]:
            player_x += player_speed
            moved = True
        
        player_x = max(player_radius, min(player_x, screen_width - player_radius))
        player_y = max(player_radius, min(player_y, screen_height - player_radius))
        
        if moved and get_terrain_at_position(player_x, player_y) == 'rock':
            player_x, player_y = prev_x, prev_y
        
        move_monsters()
        
        if check_collisions():
            game_over = True
            if game_end_time == 0:
                game_end_time = current_time
    
    screen.fill((0, 0, 0))
    
    draw_terrain(terrain_grid)
    
    if power_pellet_active:
        draw_power_pellet()
    
    draw_monsters()
    
    if not player_hiding:
        if player_powered:
            size_mod = math.sin(pygame.time.get_ticks() / 150) * 3
            pygame.draw.circle(screen, (255, 255, 0), (player_x, player_y), player_radius + size_mod)
            pygame.draw.circle(screen, RED, (player_x, player_y), int(player_radius * 0.7))
        else:
            pygame.draw.circle(screen, RED, (player_x, player_y), player_radius)
    else:
        pygame.draw.circle(screen, (255, 200, 200), (player_x, player_y), player_radius)
        hide_time = current_time - player_hide_start_time
        progress = min(hide_time / HIDE_MAX_TIME, 1)
        pygame.draw.arc(screen, (255, 0, 0), 
                       (player_x - player_radius - 5, player_y - player_radius - 5, 
                        player_radius * 2 + 10, player_radius * 2 + 10),
                       0, progress * 2 * math.pi, 3)
    
    draw_cooldown_indicator()
    draw_power_indicator()
    draw_score()
    
    screen.blit(instruction_text, (10, 10))
    screen.blit(hide_text, (10, 30))
    
    if game_over:
        draw_game_over()
    
    pygame.display.flip()
    
    clock.tick(60)

pygame.quit()
sys.exit()
