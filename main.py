import pygame
from player import Player


pygame.init()

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

score = 0
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.move(keys, SCREEN_WIDTH, SCREEN_HEIGHT)

    screen.fill((240, 240, 240))

    player.draw(screen)

    score_text = font.render(f"Игрок: {nickname} | Очки: {score}", True, (0, 0, 0))
    help_text = small_font.render(
        "Управляй синим квадратом с помощью стрелок",
        True,
        (50, 50, 50)
    )

    screen.blit(score_text, (20, 20))
    screen.blit(help_text, (20, 60))

    pygame.display.update()

pygame.quit()