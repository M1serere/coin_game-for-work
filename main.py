import pygame
import random
from player import Player
from database import Database


pygame.init()
db = Database()

nickname = input("Введите ваш никнейм: ")

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Coin Game")

clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 28)
small_font = pygame.font.SysFont("Arial", 22)

player = Player(
    x=SCREEN_WIDTH // 2,
    y=SCREEN_HEIGHT // 2,
    size=40,
    speed=5
)

coin_size = 25

coin_x = random.randint(0, SCREEN_WIDTH - coin_size)
coin_y = random.randint(100, SCREEN_HEIGHT - coin_size)

enemy_size = 45

enemy_x = random.randint(0, SCREEN_WIDTH - enemy_size)
enemy_y = random.randint(100, SCREEN_HEIGHT - enemy_size)

score = 0
win_score = 10

game_over = False
result_text = ""

running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if not game_over:
        player.move(keys, SCREEN_WIDTH, SCREEN_HEIGHT)

    coin_rect = pygame.Rect(coin_x, coin_y, coin_size, coin_size)
    enemy_rect = pygame.Rect(enemy_x, enemy_y, enemy_size, enemy_size)

    if not game_over and player.get_rect().colliderect(coin_rect):
        score += 1

        if score >= win_score:
            game_over = True
            result_text = "Ты выиграл!"
            db.save_score(nickname, score)
        else:
            coin_x = random.randint(0, SCREEN_WIDTH - coin_size)
            coin_y = random.randint(100, SCREEN_HEIGHT - coin_size)

    if not game_over and player.get_rect().colliderect(enemy_rect):
        game_over = True
        result_text = "Ты проиграл!"
        db.save_score(nickname, score)

    screen.fill((240, 240, 240))

    pygame.draw.circle(
        screen,
        (255, 200, 0),
        (coin_x + coin_size // 2, coin_y + coin_size // 2),
        coin_size // 2
    )

    pygame.draw.rect(
        screen,
        (220, 0, 0),
        (enemy_x, enemy_y, enemy_size, enemy_size)
    )

    player.draw(screen)

    score_text = font.render(f"Игрок: {nickname} | Очки: {score}", True, (0, 0, 0))
    help_text = small_font.render(
        "Собери 10 монет, чтобы выиграть.",
        True,
        (50, 50, 50)
    )

    screen.blit(score_text, (20, 20))
    screen.blit(help_text, (20, 60))

    if game_over:
        top_players = db.get_top_players()

        if result_text == "Ты выиграл!":
            result_color = (0, 150, 0)
        else:
            result_color = (200, 0, 0)

        result_surface = font.render(result_text, True, result_color)
        restart_surface = small_font.render(
            "Собери 10 монет и не касайся красного врага.",
            True,
            (50, 50, 50)
        )

        screen.blit(result_surface, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 30))
        screen.blit(restart_surface, (SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT // 2 + 10))

        y_offset = SCREEN_HEIGHT // 2 + 60

        title = small_font.render("ТОП-5 игроков:", True, (0, 0, 0))
        screen.blit(title, (SCREEN_WIDTH // 2 - 100, y_offset))

        y_offset += 30

        for i, (name, sc) in enumerate(top_players):
            text = small_font.render(f"{i + 1}. {name} - {sc}", True, (0, 0, 0))
            screen.blit(text, (SCREEN_WIDTH // 2 - 100, y_offset))
            y_offset += 25

    pygame.display.update()

pygame.quit()
