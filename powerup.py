import random, math, pygame
import settings
from terrain import get_terrain_at_position

def spawn_power_pellet(grid):
    while True:
        x = random.randint(settings.POWER_PELLET_RADIUS * 2, settings.SCREEN_WIDTH - settings.POWER_PELLET_RADIUS * 2)
        y = random.randint(settings.POWER_PELLET_RADIUS * 2, settings.SCREEN_HEIGHT - settings.POWER_PELLET_RADIUS * 2)
        if get_terrain_at_position(grid, x, y) not in ['rock', 'river']:
            return (x, y)

def draw_power_pellet(pellet, screen):
    if pellet is not None:
        x, y = pellet
        size_mod = math.sin(pygame.time.get_ticks() / 200) * 2
        pygame.draw.circle(screen, settings.PURPLE, (x, y), int(settings.POWER_PELLET_RADIUS + size_mod))
        pygame.draw.circle(screen, (255, 255, 255), (x, y), int((settings.POWER_PELLET_RADIUS + size_mod) * 0.6))

def draw_power_indicator(player_powered, power_start_time, screen):
    if player_powered:
        current_time = pygame.time.get_ticks()
        remaining = settings.POWER_DURATION - (current_time - power_start_time)
        bar_width = 100
        bar_height = 10
        bar_x = 10
        bar_y = 80
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        progress = remaining / settings.POWER_DURATION
        pygame.draw.rect(screen, settings.PURPLE, (bar_x, bar_y, bar_width * progress, bar_height))
        power_font = pygame.font.SysFont(None, 20)
        power_text = power_font.render("Power Mode!", True, settings.PURPLE)
        screen.blit(power_text, (bar_x, bar_y - 20))
