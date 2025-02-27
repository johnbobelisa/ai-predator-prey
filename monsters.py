import random, math, pygame
import settings
from terrain import get_terrain_at_position

def initialize_monsters():
    monster_list = []
    for _ in range(settings.NUM_MONSTERS):
        edge = random.randint(0, 3)
        if edge == 0:  # Top
            x = random.randint(0, settings.SCREEN_WIDTH - settings.MONSTER_SIZE)
            y = random.randint(0, 50)
        elif edge == 1:  # Right
            x = random.randint(settings.SCREEN_WIDTH - 50, settings.SCREEN_WIDTH - settings.MONSTER_SIZE)
            y = random.randint(0, settings.SCREEN_HEIGHT - settings.MONSTER_SIZE)
        elif edge == 2:  # Bottom
            x = random.randint(0, settings.SCREEN_WIDTH - settings.MONSTER_SIZE)
            y = random.randint(settings.SCREEN_HEIGHT - 50, settings.SCREEN_HEIGHT - settings.MONSTER_SIZE)
        else:  # Left
            x = random.randint(0, 50)
            y = random.randint(0, settings.SCREEN_HEIGHT - settings.MONSTER_SIZE)
        angle = random.uniform(0, 2 * math.pi)
        dx = math.cos(angle) * settings.MONSTER_NORMAL_SPEED
        dy = math.sin(angle) * settings.MONSTER_NORMAL_SPEED
        monster_list.append({
            'x': x,
            'y': y,
            'dx': dx,
            'dy': dy,
            'angle': angle,
            'state': 'random',  # 'random', 'chase', or 'flee'
            'speed': settings.MONSTER_NORMAL_SPEED,
            'eaten': False
        })
    return monster_list

def move_monsters(monster_list, grid, player_x, player_y, player_hiding, player_powered):
    for monster in monster_list:
        if monster['eaten']:
            continue
        terrain_tile = get_terrain_at_position(grid, monster['x'], monster['y'])
        if terrain_tile == 'river':
            monster['speed'] = settings.MONSTER_NORMAL_SPEED * 0.75
        else:
            monster['speed'] = settings.MONSTER_NORMAL_SPEED
        can_see_player = False
        if not player_hiding:
            distance = math.hypot(player_x - monster['x'], player_y - monster['y'])
            if distance < settings.MONSTER_SIGHT_RANGE:
                can_see_player = True
        if player_powered:
            monster['state'] = 'flee'
        elif can_see_player:
            monster['state'] = 'chase'
        else:
            if monster['state'] != 'random' and random.random() < 0.1:
                monster['state'] = 'random'
        if monster['state'] == 'chase':
            dx = player_x - monster['x']
            dy = player_y - monster['y']
            length = math.hypot(dx, dy)
            if length > 0:
                dx, dy = (dx / length) * monster['speed'], (dy / length) * monster['speed']
                monster['dx'], monster['dy'] = dx, dy
                monster['angle'] = math.atan2(dy, dx)
        elif monster['state'] == 'flee':
            dx = monster['x'] - player_x
            dy = monster['y'] - player_y
            length = math.hypot(dx, dy)
            if length > 0:
                dx, dy = (dx / length) * monster['speed'] * 0.8, (dy / length) * monster['speed'] * 0.8
                monster['dx'], monster['dy'] = dx, dy
                monster['angle'] = math.atan2(dy, dx)
        else:
            if random.random() < 0.03:
                monster['angle'] = random.uniform(0, 2 * math.pi)
                monster['dx'] = math.cos(monster['angle']) * monster['speed']
                monster['dy'] = math.sin(monster['angle']) * monster['speed']
        new_x = monster['x'] + monster['dx']
        new_y = monster['y'] + monster['dy']
        if get_terrain_at_position(grid, new_x, new_y) != 'rock':
            monster['x'] = new_x
            monster['y'] = new_y
        else:
            monster['dx'] *= -1
            monster['dy'] *= -1
            monster['angle'] = math.atan2(monster['dy'], monster['dx'])
        if monster['x'] < 0 or monster['x'] > settings.SCREEN_WIDTH - settings.MONSTER_SIZE:
            monster['dx'] *= -1
            monster['angle'] = math.atan2(monster['dy'], -monster['dx'])
            monster['x'] = max(0, min(monster['x'], settings.SCREEN_WIDTH - settings.MONSTER_SIZE))
        if monster['y'] < 0 or monster['y'] > settings.SCREEN_HEIGHT - settings.MONSTER_SIZE:
            monster['dy'] *= -1
            monster['angle'] = math.atan2(-monster['dy'], monster['dx'])
            monster['y'] = max(0, min(monster['y'], settings.SCREEN_HEIGHT - settings.MONSTER_SIZE))

def draw_monsters(monster_list, screen):
    for monster in monster_list:
        if monster['eaten']:
            continue
        color = settings.BLACK
        if monster['state'] == 'flee':
            color = (0, 0, 255)
        center_x = monster['x'] + settings.MONSTER_SIZE / 2
        center_y = monster['y'] + settings.MONSTER_SIZE / 2
        tip_x = center_x + math.cos(monster['angle']) * settings.MONSTER_SIZE / 1.5
        tip_y = center_y + math.sin(monster['angle']) * settings.MONSTER_SIZE / 1.5
        perp_angle = monster['angle'] + math.pi / 2
        perp_x = math.cos(perp_angle) * settings.MONSTER_SIZE / 3
        perp_y = math.sin(perp_angle) * settings.MONSTER_SIZE / 3
        base1 = (center_x - math.cos(monster['angle']) * settings.MONSTER_SIZE / 3 + perp_x,
                 center_y - math.sin(monster['angle']) * settings.MONSTER_SIZE / 3 + perp_y)
        base2 = (center_x - math.cos(monster['angle']) * settings.MONSTER_SIZE / 3 - perp_x,
                 center_y - math.sin(monster['angle']) * settings.MONSTER_SIZE / 3 - perp_y)
        pygame.draw.polygon(screen, color, [(tip_x, tip_y), base1, base2])
        pygame.draw.circle(screen, color, (int(center_x), int(center_y)), settings.MONSTER_SIZE // 4)
        if monster['state'] == 'chase':
            pygame.draw.circle(screen, settings.RED, (int(center_x), int(center_y)), settings.MONSTER_SIZE // 2, 1)
