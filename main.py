import pygame
import random
import ctypes
import os
from player import Player
from database import Database
from enemy import Enemy

pygame.init()
pygame.mixer.init()

db = Database()

MUSIC_DIR = "music"

menu_music = os.path.join(MUSIC_DIR, "menu_m.mp3")
play_music = os.path.join(MUSIC_DIR, "play_m.mp3")
win_music = os.path.join(MUSIC_DIR, "win_m.mp3")
lose_music = os.path.join(MUSIC_DIR, "lose_m.mp3")
coin_sound = pygame.mixer.Sound(os.path.join(MUSIC_DIR, "coin_m.mp3"))
time_sound = pygame.mixer.Sound(os.path.join(MUSIC_DIR, "time_m.mp3"))

current_music = None

def play_background_music(path, loops=-1):
    global current_music

    if current_music != path:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(loops)
        current_music = path

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

play_background_music(menu_music)

player = Player(
    x=SCREEN_WIDTH // 2 - 20,
    y=SCREEN_HEIGHT // 2 - 20,
    size=40,
    speed=5
)

coin_size = 25

coin_x = random.randint(0, SCREEN_WIDTH - coin_size)
coin_y = random.randint(100, SCREEN_HEIGHT - coin_size)

def create_safe_enemy(player):
    enemy_size = 45

    while True:
        enemy = Enemy(
            x=random.randint(0, SCREEN_WIDTH - enemy_size),
            y=random.randint(100, SCREEN_HEIGHT - enemy_size),
            size=enemy_size,
            speed_x=3,
            speed_y=3
        )

        if not enemy.get_rect().colliderect(player.get_rect()):
            return enemy

def get_time_limit():
    easy_time_limits = {
        10: 5 * 60 * 1000,
        20: 10 * 60 * 1000,
        50: 25 * 60 * 1000
    }

    if difficulty == "hard":
        hard_time_limits = {
            10: 30 * 1000,
            20: 60 * 1000,
            50: 150 * 1000
        }

        return hard_time_limits.get(win_score, 30 * 1000)

    return easy_time_limits.get(win_score, 5 * 60 * 1000)

enemies = [create_safe_enemy(player)]

def format_time(milliseconds):
    total_seconds = max(0, milliseconds // 1000)
    minutes = total_seconds // 60
    seconds = total_seconds % 60

    return f"{minutes:02}:{seconds:02}"

score = 0
win_score = 10
difficulty = "easy"

enemy_start_delay = 2000
game_start_time = 0
game_elapsed_time = 0
last_frame_time = pygame.time.get_ticks()

time_limit = 5 * 60 * 1000
time_warning_played = False

last_enemy_double_time = 0
enemy_speed_bonus = 0

input_name_screen = True
nickname = ""

start_screen = True

game_over = False
result_text = ""
paused = False

pause_button = pygame.Rect(600, 20, 80, 35)
continue_button = pygame.Rect(690, 20, 90, 35)

running = True

def restart_game():
    global player, coin_x, coin_y, enemies, score, game_over, result_text
    global start_screen, game_start_time, game_elapsed_time, last_frame_time
    global paused, time_warning_played
    global last_enemy_double_time, enemy_speed_bonus    
    player = Player(
        x=SCREEN_WIDTH // 2 - 20,
        y=SCREEN_HEIGHT // 2 - 20,
        size=40,
        speed=5
    )

    coin_x = random.randint(0, SCREEN_WIDTH - coin_size)
    coin_y = random.randint(100, SCREEN_HEIGHT - coin_size)

    enemies = [create_safe_enemy(player)]

    score = 0
    game_over = False
    result_text = ""
    start_screen = True
    game_start_time = 0
    game_elapsed_time = 0
    last_frame_time = pygame.time.get_ticks()

    play_background_music(menu_music)
    paused = False

    time_warning_played = False
    last_enemy_double_time = 0
    enemy_speed_bonus = 0

while running:
    clock.tick(60)
    current_time = pygame.time.get_ticks()
    frame_time = current_time - last_frame_time
    last_frame_time = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not input_name_screen and not start_screen and not game_over:
                mouse_pos = event.pos

                if pause_button.collidepoint(mouse_pos):
                    paused = True
                    pygame.mixer.music.pause()

                if continue_button.collidepoint(mouse_pos):
                    paused = False
                    pygame.mixer.music.unpause()

        if event.type == pygame.KEYDOWN:
            if input_name_screen:
                if event.key == pygame.K_RETURN and nickname.strip() != "":
                    input_name_screen = False

                elif event.key == pygame.K_BACKSPACE:
                    nickname = nickname[:-1]

                else:
                    if len(nickname) < 15:
                        nickname += event.unicode

                continue

            if start_screen:
                if event.key == pygame.K_1:
                    win_score = 10

                if event.key == pygame.K_2:
                    win_score = 20

                if event.key == pygame.K_3:
                    win_score = 50

                if event.key == pygame.K_e:
                    difficulty = "easy"

                if event.key == pygame.K_h:
                    difficulty = "hard"

                if event.key == pygame.K_RETURN:
                    start_screen = False
                    game_start_time = current_time
                    game_elapsed_time = 0
                    last_frame_time = current_time
                    time_limit = get_time_limit()
                    time_warning_played = False
                    last_enemy_double_time = 0
                    enemy_speed_bonus = 0
                    play_background_music(play_music)

            if game_over and event.key == pygame.K_r:
                restart_game()

    keys = pygame.key.get_pressed()

    if not start_screen and not game_over and not paused:
        game_elapsed_time += frame_time
        player.move(keys, SCREEN_WIDTH, SCREEN_HEIGHT)

        if game_elapsed_time >= enemy_start_delay:
            for enemy in enemies:
                enemy.move(SCREEN_WIDTH, SCREEN_HEIGHT)


        elapsed_time = game_elapsed_time
        remaining_time = time_limit - elapsed_time

        if remaining_time <= 10000 and not time_warning_played:
            time_sound.play()
            time_warning_played = True

        if remaining_time <= 0:
            game_over = True
            result_text = "Ты проиграл!"
            db.save_score(nickname, score)
            time_sound.stop()
            play_background_music(lose_music, loops=0)

        if difficulty == "hard" and not game_over:
            half_time = time_limit // 2

            if elapsed_time >= half_time:
                if last_enemy_double_time == 0 or elapsed_time - last_enemy_double_time >= 10000:
                    current_enemy_count = len(enemies)

                    for _ in range(current_enemy_count):
                        new_enemy = create_safe_enemy(player)
                        new_enemy.speed_x += enemy_speed_bonus
                        new_enemy.speed_y += enemy_speed_bonus
                        enemies.append(new_enemy)

                    enemy_speed_bonus += 1

                    for enemy in enemies:
                        if enemy.speed_x > 0:
                            enemy.speed_x += 1
                        else:
                            enemy.speed_x -= 1

                        if enemy.speed_y > 0:
                            enemy.speed_y += 1
                        else:
                            enemy.speed_y -= 1

                    last_enemy_double_time = elapsed_time

    coin_rect = pygame.Rect(coin_x, coin_y, coin_size, coin_size)
    #enemy_rect = enemy.get_rect()

    if not start_screen and not game_over and not paused and player.get_rect().colliderect(coin_rect):
        score += 1
        coin_sound.play()

        if score >= win_score:
            game_over = True
            result_text = "Ты выиграл!"
            db.save_score(nickname, score)
            time_sound.stop()
            play_background_music(win_music, loops=0)
        else:
            coin_x = random.randint(0, SCREEN_WIDTH - coin_size)
            coin_y = random.randint(100, SCREEN_HEIGHT - coin_size)

    if not start_screen and not game_over and not paused:
        for enemy in enemies:
            if player.get_rect().colliderect(enemy.get_rect()):
                game_over = True
                result_text = "Ты проиграл!"
                db.save_score(nickname, score)
                time_sound.stop()
                play_background_music(lose_music, loops=0)
                break

    screen.fill((240, 240, 240))

    if input_name_screen:
        title_text = font.render("Введите ваш никнейм", True, (0, 0, 0))

        input_box = pygame.Rect(
            SCREEN_WIDTH // 2 - 150,
            SCREEN_HEIGHT // 2 - 30,
            300,
            60
        )

        pygame.draw.rect(screen, (255, 255, 255), input_box)
        pygame.draw.rect(screen, (0, 0, 0), input_box, 2)

        name_text = font.render(nickname, True, (0, 0, 0))
        hint_text = small_font.render("Нажмите ENTER, чтобы продолжить", True, (80, 80, 80))

        screen.blit(title_text, (SCREEN_WIDTH // 2 - 145, SCREEN_HEIGHT // 2 - 110))
        screen.blit(name_text, (input_box.x + 15, input_box.y + 15))
        screen.blit(hint_text, (SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2 + 50))

        pygame.display.update()
        continue

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

        mode_text = small_font.render(
            f"Режим: {'лёгкий' if difficulty == 'easy' else 'сложный'}",
            True,
            (120, 0, 0)
        )

        difficulty_text = small_font.render(
            "Выбери режим: E — лёгкий, H — сложный.",
            True,
            (0, 0, 120)
        )

        screen.blit(title_text, (SCREEN_WIDTH // 2 - 70, 120))
        screen.blit(rule_1, (SCREEN_WIDTH // 2 - 120, 190))
        screen.blit(rule_2, (SCREEN_WIDTH // 2 - 220, 230))
        screen.blit(rule_3, (SCREEN_WIDTH // 2 - 220, 260))
        screen.blit(rule_4, (SCREEN_WIDTH // 2 - 220, 290))
        screen.blit(rule_5, (SCREEN_WIDTH // 2 - 220, 320))
        screen.blit(rule_6, (SCREEN_WIDTH // 2 - 220, 350))
        screen.blit(choose_text, (SCREEN_WIDTH // 2 - 260, 390))
        screen.blit(mode_text, (SCREEN_WIDTH // 2 - 100, 430))
        screen.blit(difficulty_text, (SCREEN_WIDTH // 2 - 210, 465))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - 170, 515))

        pygame.display.update()
        continue

    pygame.draw.circle(
        screen,
        (255, 200, 0),
        (coin_x + coin_size // 2, coin_y + coin_size // 2),
        coin_size // 2
    )

    for enemy in enemies:
        enemy.draw(screen)

    player.draw(screen)

    if not start_screen and game_start_time > 0:
        elapsed_time = game_elapsed_time
        remaining_time = time_limit - elapsed_time
    else:
        remaining_time = time_limit

    score_text = font.render(
        f"Игрок: {nickname} | Очки: {score} | Время: {format_time(remaining_time)}",
        True,
        (0, 0, 0)
    )
    help_text = small_font.render(
        "WASD / arrows - move",
        True,
        (80, 80, 80)
    )

    pygame.draw.line(screen, (0, 0, 0), (0, 100), (SCREEN_WIDTH, 100), 2)

    screen.blit(score_text, (20, 20))
    screen.blit(help_text, (20, 60))

    pygame.draw.rect(screen, (255, 255, 255), pause_button)
    pygame.draw.rect(screen, (0, 0, 0), pause_button, 2)

    pause_text = small_font.render("Пауза", True, (0, 0, 0))
    pause_text_rect = pause_text.get_rect(center=pause_button.center)
    screen.blit(pause_text, pause_text_rect)

    pygame.draw.rect(screen, (255, 255, 255), continue_button)
    pygame.draw.rect(screen, (0, 0, 0), continue_button, 2)

    continue_text = small_font.render("Дальше", True, (0, 0, 0))
    continue_text_rect = continue_text.get_rect(center=continue_button.center)
    screen.blit(continue_text, continue_text_rect)

    if paused:
        pause_message = font.render("ПАУЗА", True, (0, 0, 0))
        pause_rect = pause_message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(pause_message, pause_rect)

    if game_over:
        top_players = db.get_top_players()

        card_width = 420
        card_height = 320

        card_x = SCREEN_WIDTH // 2 - card_width // 2
        card_y = SCREEN_HEIGHT // 2 - card_height // 2

        pygame.draw.rect(
            screen,
            (255, 255, 255),
            (card_x, card_y, card_width, card_height)
        )

        pygame.draw.rect(
            screen,
            (0, 0, 0),
            (card_x, card_y, card_width, card_height),
            2
        )

        if result_text == "Ты выиграл!":
            result_color = (0, 150, 0)
        else:
            result_color = (200, 0, 0)

        result_surface = font.render(result_text, True, result_color)
        result_rect = result_surface.get_rect(center=(SCREEN_WIDTH // 2, card_y + 40))
        screen.blit(result_surface, result_rect)

        restart_surface = small_font.render(
            "Нажми R, чтобы сыграть снова",
            True,
            (50, 50, 50)
        )
        restart_rect = restart_surface.get_rect(center=(SCREEN_WIDTH // 2, card_y + 80))
        screen.blit(restart_surface, restart_rect)

        title = small_font.render("ТОП-5 игроков:", True, (0, 0, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, card_y + 125))
        screen.blit(title, title_rect)

        y_offset = card_y + 160

        for i, (name, sc) in enumerate(top_players):
            text = small_font.render(f"{i + 1}. {name} — {sc}", True, (0, 0, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(text, text_rect)
            y_offset += 28

    pygame.display.update()

pygame.quit()
