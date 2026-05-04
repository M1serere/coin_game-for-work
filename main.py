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
music_volume = 0.6
player_speed = 5
enemy_base_speed = 4

PLAYER_SPEED_MIN = 2
PLAYER_SPEED_MAX = 9
ENEMY_SPEED_MIN = 1
ENEMY_SPEED_MAX = 8
MAX_SPEED_DIFFERENCE = 1

def play_background_music(path, loops=-1):
    global current_music

    if current_music != path:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(loops)
        pygame.mixer.music.set_volume(music_volume)
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
    speed=player_speed
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
            speed_x=enemy_base_speed,
            speed_y=enemy_base_speed
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
settings_open = False
dragging_slider = None
top_reset_message = ""
top_reset_message_time = 0

pause_button = pygame.Rect(620, 20, 75, 35)
continue_button = pygame.Rect(700, 20, 90, 35)
settings_button = pygame.Rect(665, 20, 125, 35)
settings_close_button = pygame.Rect(SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 135, 140, 40)
music_slider = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 45, 300, 8)
player_speed_slider = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 25, 300, 8)
enemy_speed_slider = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 95, 300, 8)
reset_top_button = pygame.Rect(SCREEN_WIDTH // 2 - 110, 535, 220, 38)
name_continue_button = pygame.Rect(SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT // 2 + 80, 180, 40)
name_clear_button = pygame.Rect(SCREEN_WIDTH // 2 - 190, SCREEN_HEIGHT // 2 + 80, 180, 40)
start_game_button = pygame.Rect(SCREEN_WIDTH // 2 - 80, 485, 160, 40)
restart_button = pygame.Rect(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 115, 220, 40)
main_menu_button = pygame.Rect(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 160, 220, 40)

goal_buttons = {
    10: pygame.Rect(SCREEN_WIDTH // 2 - 210, 325, 120, 38),
    20: pygame.Rect(SCREEN_WIDTH // 2 - 60, 325, 120, 38),
    50: pygame.Rect(SCREEN_WIDTH // 2 + 90, 325, 120, 38)
}

difficulty_buttons = {
    "easy": pygame.Rect(SCREEN_WIDTH // 2 - 150, 405, 130, 38),
    "hard": pygame.Rect(SCREEN_WIDTH // 2 + 20, 405, 130, 38)
}

running = True

def slider_value_from_mouse(mouse_x, slider_rect, min_value, max_value):
    position = (mouse_x - slider_rect.x) / slider_rect.width
    position = max(0, min(1, position))
    return min_value + position * (max_value - min_value)

def draw_slider(slider_rect, value, min_value, max_value, label, suffix=""):
    label_text = small_font.render(f"{label}: {value:.1f}{suffix}", True, (0, 0, 0))
    screen.blit(label_text, (slider_rect.x, slider_rect.y - 32))

    pygame.draw.rect(screen, (190, 190, 190), slider_rect)

    position = (value - min_value) / (max_value - min_value)
    knob_x = slider_rect.x + int(position * slider_rect.width)
    knob_center = (knob_x, slider_rect.y + slider_rect.height // 2)

    pygame.draw.circle(screen, (0, 100, 200), knob_center, 12)
    pygame.draw.circle(screen, (0, 50, 120), knob_center, 12, 2)

def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))

def set_player_speed(value):
    global player_speed, enemy_base_speed

    player_speed = clamp(value, PLAYER_SPEED_MIN, PLAYER_SPEED_MAX)

    if abs(player_speed - enemy_base_speed) > MAX_SPEED_DIFFERENCE:
        if player_speed > enemy_base_speed:
            enemy_base_speed = player_speed - MAX_SPEED_DIFFERENCE
        else:
            enemy_base_speed = player_speed + MAX_SPEED_DIFFERENCE

    enemy_base_speed = clamp(enemy_base_speed, ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
    apply_player_speed()
    apply_enemy_speed()

def set_enemy_speed(value):
    global player_speed, enemy_base_speed

    enemy_base_speed = clamp(value, ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)

    if abs(player_speed - enemy_base_speed) > MAX_SPEED_DIFFERENCE:
        if enemy_base_speed > player_speed:
            player_speed = enemy_base_speed - MAX_SPEED_DIFFERENCE
        else:
            player_speed = enemy_base_speed + MAX_SPEED_DIFFERENCE

    player_speed = clamp(player_speed, PLAYER_SPEED_MIN, PLAYER_SPEED_MAX)
    apply_player_speed()
    apply_enemy_speed()

def apply_player_speed():
    player.speed = player_speed

def apply_enemy_speed():
    speed = enemy_base_speed + enemy_speed_bonus

    for enemy in enemies:
        enemy.speed_x = speed if enemy.speed_x >= 0 else -speed
        enemy.speed_y = speed if enemy.speed_y >= 0 else -speed

def draw_settings_panel():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 95))
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2 - 170, 440, 350)
    pygame.draw.rect(screen, (255, 255, 255), panel)
    pygame.draw.rect(screen, (0, 0, 0), panel, 2)

    title = font.render("Настройки", True, (0, 0, 0))
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, panel.y + 40))
    screen.blit(title, title_rect)

    draw_slider(music_slider, music_volume * 10, 0, 10, "Громкость музыки")
    draw_slider(player_speed_slider, player_speed, PLAYER_SPEED_MIN, PLAYER_SPEED_MAX, "Скорость игрока")
    draw_slider(enemy_speed_slider, enemy_base_speed, ENEMY_SPEED_MIN, ENEMY_SPEED_MAX, "Скорость врага")
    draw_button(settings_close_button, "Закрыть")

def draw_button(rect, text, selected=False, disabled=False):
    if disabled:
        fill_color = (220, 220, 220)
        border_color = (150, 150, 150)
        text_color = (110, 110, 110)
    elif selected:
        fill_color = (210, 235, 255)
        border_color = (0, 100, 200)
        text_color = (0, 60, 140)
    else:
        fill_color = (255, 255, 255)
        border_color = (0, 0, 0)
        text_color = (0, 0, 0)

    pygame.draw.rect(screen, fill_color, rect)
    pygame.draw.rect(screen, border_color, rect, 2)

    text_surface = small_font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def start_game(start_time):
    global start_screen, game_start_time, game_elapsed_time, last_frame_time
    global time_limit, time_warning_played, last_enemy_double_time, enemy_speed_bonus

    start_screen = False
    game_start_time = start_time
    game_elapsed_time = 0
    last_frame_time = game_start_time
    time_limit = get_time_limit()
    time_warning_played = False
    last_enemy_double_time = 0
    enemy_speed_bonus = 0
    play_background_music(play_music)

def reset_round():
    global player, coin_x, coin_y, enemies, score, game_over, result_text
    global game_start_time, game_elapsed_time, last_frame_time
    global paused, time_warning_played
    global last_enemy_double_time, enemy_speed_bonus

    last_enemy_double_time = 0
    enemy_speed_bonus = 0

    player = Player(
        x=SCREEN_WIDTH // 2 - 20,
        y=SCREEN_HEIGHT // 2 - 20,
        size=40,
        speed=player_speed
    )

    coin_x = random.randint(0, SCREEN_WIDTH - coin_size)
    coin_y = random.randint(100, SCREEN_HEIGHT - coin_size)

    enemies = [create_safe_enemy(player)]

    score = 0
    game_over = False
    result_text = ""
    game_start_time = 0
    game_elapsed_time = 0
    last_frame_time = pygame.time.get_ticks()

    paused = False

    time_warning_played = False

def start_new_game(start_time):
    reset_round()
    start_game(start_time)

def restart_game():
    global start_screen

    reset_round()
    start_screen = True
    play_background_music(menu_music)

while running:
    clock.tick(60)
    current_time = pygame.time.get_ticks()
    frame_time = current_time - last_frame_time
    last_frame_time = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos

                if settings_open:
                    if settings_close_button.collidepoint(mouse_pos):
                        settings_open = False
                        dragging_slider = None
                    elif music_slider.inflate(0, 28).collidepoint(mouse_pos):
                        dragging_slider = "music"
                        music_volume = slider_value_from_mouse(mouse_pos[0], music_slider, 0, 10) / 10
                        pygame.mixer.music.set_volume(music_volume)
                    elif player_speed_slider.inflate(0, 28).collidepoint(mouse_pos):
                        dragging_slider = "player"
                        set_player_speed(
                            slider_value_from_mouse(
                                mouse_pos[0],
                                player_speed_slider,
                                PLAYER_SPEED_MIN,
                                PLAYER_SPEED_MAX
                            )
                        )
                    elif enemy_speed_slider.inflate(0, 28).collidepoint(mouse_pos):
                        dragging_slider = "enemy"
                        set_enemy_speed(
                            slider_value_from_mouse(
                                mouse_pos[0],
                                enemy_speed_slider,
                                ENEMY_SPEED_MIN,
                                ENEMY_SPEED_MAX
                            )
                        )

                    continue

                if not input_name_screen and start_screen and settings_button.collidepoint(mouse_pos):
                    settings_open = True
                    continue

            if event.button == 1 and input_name_screen:
                mouse_pos = event.pos

                if name_continue_button.collidepoint(mouse_pos) and nickname.strip() != "":
                    input_name_screen = False

                if name_clear_button.collidepoint(mouse_pos):
                    nickname = ""

            if event.button == 1 and not input_name_screen and start_screen:
                mouse_pos = event.pos

                if reset_top_button.collidepoint(mouse_pos):
                    db.clear_top_players()
                    top_reset_message = "Топ игроков очищен"
                    top_reset_message_time = current_time

                for goal, button in goal_buttons.items():
                    if button.collidepoint(mouse_pos):
                        win_score = goal

                for mode, button in difficulty_buttons.items():
                    if button.collidepoint(mouse_pos):
                        difficulty = mode

                if start_game_button.collidepoint(mouse_pos):
                    start_game(current_time)

            if event.button == 1 and not input_name_screen and not start_screen and not game_over:
                mouse_pos = event.pos

                if pause_button.collidepoint(mouse_pos):
                    paused = True
                    pygame.mixer.music.pause()

                if continue_button.collidepoint(mouse_pos):
                    paused = False
                    pygame.mixer.music.unpause()

            if event.button == 1 and game_over:
                mouse_pos = event.pos

                if restart_button.collidepoint(mouse_pos):
                    start_new_game(current_time)

                if main_menu_button.collidepoint(mouse_pos):
                    restart_game()

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging_slider = None

        if event.type == pygame.MOUSEMOTION and settings_open and dragging_slider is not None:
            mouse_x = event.pos[0]

            if dragging_slider == "music":
                music_volume = slider_value_from_mouse(mouse_x, music_slider, 0, 10) / 10
                pygame.mixer.music.set_volume(music_volume)
            elif dragging_slider == "player":
                set_player_speed(
                    slider_value_from_mouse(
                        mouse_x,
                        player_speed_slider,
                        PLAYER_SPEED_MIN,
                        PLAYER_SPEED_MAX
                    )
                )
            elif dragging_slider == "enemy":
                set_enemy_speed(
                    slider_value_from_mouse(
                        mouse_x,
                        enemy_speed_slider,
                        ENEMY_SPEED_MIN,
                        ENEMY_SPEED_MAX
                    )
                )

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if input_name_screen and nickname.strip() != "":
                    input_name_screen = False
                elif not input_name_screen and start_screen and not settings_open:
                    start_game(current_time)
                elif game_over:
                    start_new_game(current_time)

        if event.type == pygame.TEXTINPUT and input_name_screen:
            if event.text.isprintable() and len(nickname) < 15:
                nickname += event.text

    if not start_screen and not game_over and not paused and not settings_open:
        game_elapsed_time += frame_time
        keys = pygame.key.get_pressed()
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
            result_text = "Поражение"
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

    if not start_screen and not game_over and not paused and not settings_open and player.get_rect().colliderect(coin_rect):
        score += 1
        coin_sound.play()

        if score >= win_score:
            game_over = True
            result_text = "Победа"
            db.save_score(nickname, score)
            time_sound.stop()
            play_background_music(win_music, loops=0)
        else:
            coin_x = random.randint(0, SCREEN_WIDTH - coin_size)
            coin_y = random.randint(100, SCREEN_HEIGHT - coin_size)

    if not start_screen and not game_over and not paused and not settings_open:
        for enemy in enemies:
            if player.get_rect().colliderect(enemy.get_rect()):
                game_over = True
                result_text = "Поражение"
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
        screen.blit(title_text, (SCREEN_WIDTH // 2 - 145, SCREEN_HEIGHT // 2 - 110))
        screen.blit(name_text, (input_box.x + 15, input_box.y + 15))
        draw_button(name_clear_button, "Очистить", disabled=nickname == "")
        draw_button(name_continue_button, "Продолжить", disabled=nickname.strip() == "")

        pygame.display.update()
        continue

    if start_screen:
        title_text = font.render("Coin Game", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 70))
        rules = [
            ("Правила игры:", (0, 0, 0)),
            ("1. Управляй синим квадратом стрелками.", (50, 50, 50)),
            ("2. Собирай жёлтые монеты, чтобы получать очки.", (50, 50, 50)),
            (f"3. Собери {win_score} монет, чтобы выиграть.", (50, 50, 50)),
            ("4. Не касайся красного врага — это проигрыш.", (50, 50, 50)),
            ("5. Враг начнёт двигаться через 2 секунды после старта.", (50, 50, 50))
        ]
        mode_text = small_font.render(
            f"Режим: {'лёгкий' if difficulty == 'easy' else 'сложный'}",
            True,
            (120, 0, 0)
        )
        reset_top_text = small_font.render("Сбросить топ игроков", True, (0, 0, 0))
        reset_top_text_rect = reset_top_text.get_rect(center=reset_top_button.center)

        screen.blit(title_text, title_rect)

        for i, (text, color) in enumerate(rules):
            rule_text = small_font.render(text, True, color)
            rule_rect = rule_text.get_rect(center=(SCREEN_WIDTH // 2, 125 + i * 30))
            screen.blit(rule_text, rule_rect)

        goal_label = small_font.render("Цель", True, (0, 0, 120))
        difficulty_label = small_font.render("Режим", True, (0, 0, 120))
        goal_label_rect = goal_label.get_rect(center=(SCREEN_WIDTH // 2, 305))
        difficulty_label_rect = difficulty_label.get_rect(center=(SCREEN_WIDTH // 2, 385))
        mode_text_rect = mode_text.get_rect(center=(SCREEN_WIDTH // 2, 460))
        screen.blit(goal_label, goal_label_rect)
        screen.blit(difficulty_label, difficulty_label_rect)

        for goal, button in goal_buttons.items():
            draw_button(button, str(goal), selected=win_score == goal)

        draw_button(difficulty_buttons["easy"], "Легкий", selected=difficulty == "easy")
        draw_button(difficulty_buttons["hard"], "Сложный", selected=difficulty == "hard")
        screen.blit(mode_text, mode_text_rect)
        draw_button(start_game_button, "Старт")
        draw_button(settings_button, "Настройки")

        pygame.draw.rect(screen, (255, 255, 255), reset_top_button)
        pygame.draw.rect(screen, (180, 0, 0), reset_top_button, 2)
        screen.blit(reset_top_text, reset_top_text_rect)

        if top_reset_message and current_time - top_reset_message_time < 2000:
            reset_message = small_font.render(top_reset_message, True, (0, 120, 0))
            reset_message_rect = reset_message.get_rect(center=(SCREEN_WIDTH // 2, 585))
            screen.blit(reset_message, reset_message_rect)

        if settings_open:
            draw_settings_panel()

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
        "Двигайтесь кнопками WASD или стрелками на клавиатуре",
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
        card_height = 410

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

        if result_text == "Победа":
            result_color = (0, 150, 0)
        else:
            result_color = (200, 0, 0)

        result_surface = font.render(result_text, True, result_color)
        result_rect = result_surface.get_rect(center=(SCREEN_WIDTH // 2, card_y + 40))
        screen.blit(result_surface, result_rect)

        title = small_font.render("ТОП-5 игроков:", True, (0, 0, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, card_y + 90))
        screen.blit(title, title_rect)

        y_offset = card_y + 125

        for i, (name, sc) in enumerate(top_players):
            text = small_font.render(f"{i + 1}. {name} — {sc}", True, (0, 0, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            screen.blit(text, text_rect)
            y_offset += 28

        draw_button(restart_button, "Новая игра")
        draw_button(main_menu_button, "Главное меню")

    pygame.display.update()

pygame.quit()
