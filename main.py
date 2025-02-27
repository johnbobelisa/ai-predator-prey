import sys, random, pygame
import settings, terrain, monsters, powerup, collisions, ui

pygame.init()
screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
pygame.display.set_caption("Advanced Terrain Game with Player & Monsters")

# Global game state variables
game_over = False
game_over_reason = ""
player_x = settings.SCREEN_WIDTH // 2
player_y = settings.SCREEN_HEIGHT // 2
terrain_grid = terrain.generate_terrain()
monster_list = monsters.initialize_monsters()
power_pellet = None
player_powered = False
player_power_start_time = 0
monsters_eaten = 0
game_start_time = pygame.time.get_ticks()
game_end_time = 0
player_hiding = False
player_hide_start_time = 0
player_hide_cooldown = False
# This variable will track when the cooldown started
player_hide_cooldown_start = 0
power_pellet_next_spawn = pygame.time.get_ticks() + random.randint(settings.POWER_PELLET_SPAWN_MIN // 2, settings.POWER_PELLET_SPAWN_MAX // 2)

# Instruction texts
instruction_font = pygame.font.SysFont(None, 20)
instruction_text = instruction_font.render("WASD to move, SPACE for new terrain, R to restart", True, (255, 255, 255))
hide_text = instruction_font.render("Hide in trees/bushes (max 2s, 10s cooldown), eat power pellets to hunt monsters", True, (255, 255, 255))

def reset_game():
    global player_x, player_y, terrain_grid, monster_list, power_pellet, player_powered
    global player_power_start_time, monsters_eaten, game_start_time, game_end_time
    global player_hiding, player_hide_start_time, player_hide_cooldown, player_hide_cooldown_start, power_pellet_next_spawn, game_over, game_over_reason
    player_x = settings.SCREEN_WIDTH // 2
    player_y = settings.SCREEN_HEIGHT // 2
    terrain_grid = terrain.generate_terrain()
    monster_list = monsters.initialize_monsters()
    power_pellet = None
    player_powered = False
    player_power_start_time = 0
    monsters_eaten = 0
    game_start_time = pygame.time.get_ticks()
    game_end_time = 0
    player_hiding = False
    player_hide_start_time = 0
    player_hide_cooldown = False
    player_hide_cooldown_start = 0
    power_pellet_next_spawn = pygame.time.get_ticks() + random.randint(settings.POWER_PELLET_SPAWN_MIN // 2, settings.POWER_PELLET_SPAWN_MAX // 2)
    game_over = False
    game_over_reason = ""

clock = pygame.time.Clock()
running = True

while running:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                terrain_grid = terrain.generate_terrain()
                monster_list = monsters.initialize_monsters()
            if event.key == pygame.K_r and game_over:
                reset_game()

    if not game_over:
        if power_pellet is None and current_time >= power_pellet_next_spawn:
            power_pellet = powerup.spawn_power_pellet(terrain_grid)
        
        # Check terrain for hiding opportunities
        terrain_type, new_hiding, new_hide_start = collisions.check_terrain_collision(
            player_x, player_y, terrain_grid, player_hide_start_time, player_hide_cooldown)
        # If we were hiding but now are not, start the cooldown
        if not new_hiding and player_hiding:
            player_hide_cooldown = True
            player_hide_cooldown_start = current_time
        player_hiding = new_hiding
        player_hide_start_time = new_hide_start

        player_speed = settings.PLAYER_NORMAL_SPEED
        if terrain_type == 'river':
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

        player_x = max(settings.PLAYER_RADIUS, min(player_x, settings.SCREEN_WIDTH - settings.PLAYER_RADIUS))
        player_y = max(settings.PLAYER_RADIUS, min(player_y, settings.SCREEN_HEIGHT - settings.PLAYER_RADIUS))
        if moved and terrain.get_terrain_at_position(terrain_grid, player_x, player_y) == 'rock':
            player_x, player_y = prev_x, prev_y

        monsters.move_monsters(monster_list, terrain_grid, player_x, player_y, player_hiding, player_powered)
        
        collision, reason, new_powered, new_power_start, new_pellet = collisions.check_collisions(
            player_x, player_y, settings.PLAYER_RADIUS, player_hiding, player_powered, monster_list, power_pellet)
        if collision:
            game_over = True
            if game_end_time == 0:
                game_end_time = current_time
            game_over_reason = reason
        player_powered = new_powered
        if new_power_start is not None:
            player_power_start_time = new_power_start
        if new_pellet is not None:
            power_pellet = new_pellet

    screen.fill((0, 0, 0))
    terrain.draw_terrain(terrain_grid, screen)
    if power_pellet is not None:
        powerup.draw_power_pellet(power_pellet, screen)
    monsters.draw_monsters(monster_list, screen)
    
    # Draw player
    if not player_hiding:
        if player_powered:
            size_mod = math.sin(pygame.time.get_ticks() / 150) * 3
            pygame.draw.circle(screen, (255, 255, 0), (player_x, player_y), int(settings.PLAYER_RADIUS + size_mod))
            pygame.draw.circle(screen, settings.RED, (player_x, player_y), int(settings.PLAYER_RADIUS * 0.7))
        else:
            pygame.draw.circle(screen, settings.RED, (player_x, player_y), settings.PLAYER_RADIUS)
    else:
        pygame.draw.circle(screen, (255, 200, 200), (player_x, player_y), settings.PLAYER_RADIUS)
        hide_time = current_time - player_hide_start_time
        progress = min(hide_time / settings.HIDE_MAX_TIME, 1)
        pygame.draw.arc(screen, (255, 0, 0),
                        (player_x - settings.PLAYER_RADIUS - 5, player_y - settings.PLAYER_RADIUS - 5,
                         settings.PLAYER_RADIUS * 2 + 10, settings.PLAYER_RADIUS * 2 + 10),
                        0, progress * 2 * 3.14159, 3)
    
    ui.draw_cooldown_indicator(screen, player_hide_cooldown_start, player_hide_cooldown)
    powerup.draw_power_indicator(player_powered, player_power_start_time, screen)
    ui.draw_score(screen, game_start_time, monsters_eaten, game_over, game_end_time)
    screen.blit(instruction_text, (10, 10))
    screen.blit(hide_text, (10, 30))
    
    if game_over:
        ui.draw_game_over(screen, game_end_time, game_start_time, monsters_eaten, game_over_reason)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
