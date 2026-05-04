import pygame
import random
import ctypes
from player import Player
from database import Database
from enemy import Enemy


pygame.init()
db = Database()

nickname = input("Введите ваш никнейм: ")

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Coin Game")

try:
    hwnd = pygame.display.get_wm_info()["window"]
    ctypes.windll.user32.SetForegroundWindow(hwnd)
except Exception:
    pass

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

enemy = Enemy(
    x=random.randint(0, SCREEN_WIDTH - 45),
    y=random.randint(100, SCREEN_HEIGHT - 45),
    size=45,
    speed_x=3,
    speed_y=3
)
score = 0
win_score = 10
enemy_start_delay = 2000
game_start_time = 0

start_screen = True

game_over = False
result_text = ""

running = True

def restart_game():
    global player, coin_x, coin_y, enemy, score, game_over, result_text, start_screen, game_start_time
    player = Player(
        x=SCREEN_WIDTH // 2,
        y=SCREEN_HEIGHT // 2,
        size=40,
        speed=5
    )

    coin_x = random.randint(0, SCREEN_WIDTH - coin_size)
    coin_y = random.randint(100, SCREEN_HEIGHT - coin_size)

    enemy = Enemy(
        x=random.randint(0, SCREEN_WIDTH - 45),
        y=random.randint(100, SCREEN_HEIGHT - 45),
        size=45,
        speed_x=3,
        speed_y=3
    )

    score = 0
    game_over = False
    result_text = ""
    start_screen = True
    game_start_time = 0

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if start_screen:
                if event.key == pygame.K_1:
                    win_score = 10

                if event.key == pygame.K_2:
                    win_score = 20

                if event.key == pygame.K_3:
                    win_score = 50

                if event.key == pygame.K_RETURN:
                    start_screen = False
                    game_start_time = pygame.time.get_ticks()

            if game_over and event.key == pygame.K_r:
                restart_game()

    keys = pygame.key.get_pressed()

    if not start_screen and not game_over:
        player.move(keys, SCREEN_WIDTH, SCREEN_HEIGHT)

        current_time = pygame.time.get_ticks()

        if current_time - game_start_time >= enemy_start_delay:
            enemy.move(SCREEN_WIDTH, SCREEN_HEIGHT)

    coin_rect = pygame.Rect(coin_x, coin_y, coin_size, coin_size)
    enemy_rect = enemy.get_rect()

    if not start_screen and not game_over and player.get_rect().colliderect(coin_rect):
        score += 1

        if score >= win_score:
            game_over = True
            result_text = "Ты выиграл!"
            db.save_score(nickname, score)
        else:
            coin_x = random.randint(0, SCREEN_WIDTH - coin_size)
            coin_y = random.randint(100, SCREEN_HEIGHT - coin_size)

    if not start_screen and not game_over and player.get_rect().colliderect(enemy_rect):
        game_over = True
        result_text = "Ты проиграл!"
        db.save_score(nickname, score)

    screen.fill((240, 240, 240))

    if start_screen:
        title_text = font.render("Coin Game", True, (0, 0, 0))
        rule_1 = small_font.render("Правила игры:", True, (0, 0, 0))
        rule_2 = small_font.render("1. Управляй синим квадратом стрелками.", True, (50, 50, 50))
        rule_3 = small_font.render("2. Собирай жёлтые монеты, чтобы получать очки.", True, (50, 50, 50))
        rule_4 = small_font.render(f"3. Собери {win_score} монет, чтобы выиграть.", True, (50, 50, 50))
        rule_5 = small_font.render("4. Не касайся красного врага — это проигрыш.", True, (50, 50, 50))
        rule_6 = small_font.render("5. Враг начнёт двигаться через 2 секунды после старта.", True, (50, 50, 50))
        choose_text = small_font.render("Выбери цель: 1 — 10 очков, 2 — 20 очков, 3 — 50 очков.", True, (0, 0, 120))
        start_text = small_font.render("Нажми ENTER, чтобы начать игру.", True, (0, 100, 0))

        screen.blit(title_text, (SCREEN_WIDTH // 2 - 70, 120))
        screen.blit(rule_1, (SCREEN_WIDTH // 2 - 120, 190))
        screen.blit(rule_2, (SCREEN_WIDTH // 2 - 220, 230))
        screen.blit(rule_3, (SCREEN_WIDTH // 2 - 220, 260))
        screen.blit(rule_4, (SCREEN_WIDTH // 2 - 220, 290))
        screen.blit(rule_5, (SCREEN_WIDTH // 2 - 220, 320))
        screen.blit(rule_6, (SCREEN_WIDTH // 2 - 220, 350))
        screen.blit(choose_text, (SCREEN_WIDTH // 2 - 260, 390))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - 170, 430))

        pygame.display.update()
        continue

    pygame.draw.circle(
        screen,
        (255, 200, 0),
        (coin_x + coin_size // 2, coin_y + coin_size // 2),
        coin_size // 2
    )

    enemy.draw(screen)

    player.draw(screen)

    score_text = font.render(f"Игрок: {nickname} | Очки: {score}", True, (0, 0, 0))
    help_text = small_font.render(
        f"Собери {win_score} монет и не касайся красного врага.",
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
            "Нажми R, чтобы сыграть снова, или закрой окно.",
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
