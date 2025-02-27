import math, pygame, random
import settings
from terrain import get_terrain_at_position

def check_collisions(player_x, player_y, player_radius, player_hiding, player_powered, monster_list, pellet):
    current_time = pygame.time.get_ticks()
    new_powered = player_powered
    new_power_start = None
    new_pellet = pellet
    if pellet is not None:
        pellet_x, pellet_y = pellet
        dist = math.hypot(player_x - pellet_x, player_y - pellet_y)
        if dist < player_radius + settings.POWER_PELLET_RADIUS:
            new_powered = True
            new_power_start = current_time
            new_pellet = None
    player_rect = pygame.Rect(player_x - player_radius, player_y - player_radius, player_radius * 2, player_radius * 2)
    for monster in monster_list:
        if monster['eaten']:
            continue
        center_x = monster['x'] + settings.MONSTER_SIZE / 2
        center_y = monster['y'] + settings.MONSTER_SIZE / 2
        monster_rect = pygame.Rect(center_x - settings.MONSTER_SIZE/2, center_y - settings.MONSTER_SIZE/2,
                                   settings.MONSTER_SIZE, settings.MONSTER_SIZE)
        if player_rect.colliderect(monster_rect):
            if new_powered:
                monster['eaten'] = True
            else:
                return True, "Caught by a monster!", new_powered, new_power_start, new_pellet
    return False, "", new_powered, new_power_start, new_pellet

def check_terrain_collision(player_x, player_y, grid, hide_start, hide_cooldown):
    terrain_type = get_terrain_at_position(grid, player_x, player_y)
    if terrain_type in ['tree', 'bush'] and not hide_cooldown:
        new_hiding = True
        new_hide_start = hide_start if hide_start != 0 else pygame.time.get_ticks()
    else:
        new_hiding = False
        new_hide_start = 0
    return terrain_type, new_hiding, new_hide_start
