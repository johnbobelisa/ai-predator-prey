import pygame
import settings

def draw_game_over(screen, end_time, start_time, monsters_eaten, game_over_reason):
    overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    survival_time = (end_time - start_time) // 1000
    final_score = survival_time * (monsters_eaten + 1)
    font = pygame.font.SysFont(None, 72)
    text = font.render("Game Over!", True, (255, 0, 0))
    text_rect = text.get_rect(center=(settings.SCREEN_WIDTH//2, settings.SCREEN_HEIGHT//2 - 80))
    screen.blit(text, text_rect)
    reason_font = pygame.font.SysFont(None, 36)
    reason_text = reason_font.render(game_over_reason, True, (255, 255, 255))
    reason_rect = reason_text.get_rect(center=(settings.SCREEN_WIDTH//2, settings.SCREEN_HEIGHT//2 - 30))
    screen.blit(reason_text, reason_rect)
    score_font = pygame.font.SysFont(None, 48)
    score_text = score_font.render(f"Final Score: {final_score}", True, (255, 255, 0))
    score_rect = score_text.get_rect(center=(settings.SCREEN_WIDTH//2, settings.SCREEN_HEIGHT//2 + 20))
    screen.blit(score_text, score_rect)
    stats_font = pygame.font.SysFont(None, 30)
    time_text = stats_font.render(f"Survival Time: {survival_time} seconds", True, (255, 255, 255))
    time_rect = time_text.get_rect(center=(settings.SCREEN_WIDTH//2, settings.SCREEN_HEIGHT//2 + 60))
    screen.blit(time_text, time_rect)
    monsters_text = stats_font.render(f"Monsters Eaten: {monsters_eaten}", True, (255, 255, 255))
    monsters_rect = monsters_text.get_rect(center=(settings.SCREEN_WIDTH//2, settings.SCREEN_HEIGHT//2 + 90))
    screen.blit(monsters_text, monsters_rect)
    restart_font = pygame.font.SysFont(None, 36)
    restart_text = restart_font.render("Press R to restart", True, (255, 255, 255))
    restart_rect = restart_text.get_rect(center=(settings.SCREEN_WIDTH//2, settings.SCREEN_HEIGHT//2 + 140))
    screen.blit(restart_text, restart_rect)

def draw_cooldown_indicator(screen, hide_cooldown_start, hide_cooldown):
    current_time = pygame.time.get_ticks()
    if hide_cooldown:
        remaining = settings.HIDE_COOLDOWN_TIME - (current_time - hide_cooldown_start)
        if remaining > 0:
            bar_width = 100
            bar_height = 10
            bar_x = 10
            bar_y = 50
            pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            progress = remaining / settings.HIDE_COOLDOWN_TIME
            pygame.draw.rect(screen, settings.YELLOW, (bar_x, bar_y, bar_width * (1 - progress), bar_height))
            cooldown_font = pygame.font.SysFont(None, 20)
            cooldown_text = cooldown_font.render("Hide Cooldown", True, (255, 255, 255))
            screen.blit(cooldown_text, (bar_x, bar_y - 20))

def draw_score(screen, start_time, monsters_eaten, game_over, end_time):
    current_time = end_time if game_over else pygame.time.get_ticks()
    survival_time = (current_time - start_time) // 1000
    score = survival_time * (monsters_eaten + 1)
    score_font = pygame.font.SysFont(None, 36)
    score_text = score_font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (settings.SCREEN_WIDTH - score_text.get_width() - 10, 10))
    monsters_font = pygame.font.SysFont(None, 24)
    monsters_text = monsters_font.render(f"Monsters Eaten: {monsters_eaten}", True, (255, 255, 255))
    screen.blit(monsters_text, (settings.SCREEN_WIDTH - monsters_text.get_width() - 10, 50))
    time_text = monsters_font.render(f"Time: {survival_time}s", True, (255, 255, 255))
    screen.blit(time_text, (settings.SCREEN_WIDTH - time_text.get_width() - 10, 80))
