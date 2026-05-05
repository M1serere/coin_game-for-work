import pygame
import random
import ctypes
import os
from paths import resource_path
from player import Player
from database import Database
from enemy import Enemy

pygame.init()
pygame.mixer.init()

db = Database()

MUSIC_DIR = "music"
ASSETS_DIR = "assets"

menu_music = resource_path(MUSIC_DIR, "menu_m.mp3")
play_music = resource_path(MUSIC_DIR, "play_m.mp3")
win_music = resource_path(MUSIC_DIR, "win_m.mp3")
lose_music = resource_path(MUSIC_DIR, "lose_m.mp3")
coin_sound = pygame.mixer.Sound(resource_path(MUSIC_DIR, "coin_m.mp3"))
time_sound = pygame.mixer.Sound(resource_path(MUSIC_DIR, "time_m.mp3"))
teleport_sound = pygame.mixer.Sound(resource_path(MUSIC_DIR, "teleport.mp3"))

current_music = None
music_volume = 0.6
player_speed = 5
enemy_base_speed = 4

PLAYER_SPEED_MIN = 2
PLAYER_SPEED_MAX = 9
ENEMY_SPEED_MIN = 1
ENEMY_SPEED_MAX = 8
MAX_SPEED_DIFFERENCE = 1
PLAYER_FLAME_GROWTH = 2

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
pygame.display.set_caption("Спасайся, огонёк!")

game_background = pygame.image.load(resource_path(ASSETS_DIR, "fon_g.jpg")).convert()
game_background = pygame.transform.scale(game_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
menu_background = pygame.image.load(resource_path(ASSETS_DIR, "fon_m.jpg")).convert()
menu_background = pygame.transform.scale(menu_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
circle_image = pygame.image.load(resource_path(ASSETS_DIR, "circle.png")).convert_alpha()
cloud_overlay = pygame.image.load(resource_path(ASSETS_DIR, "cloud.png")).convert_alpha()
cloud_overlay = pygame.transform.smoothscale(cloud_overlay, (SCREEN_WIDTH, SCREEN_HEIGHT))
cloud_overlay.set_alpha(155)

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
coin_sprite_size = int(coin_size * 0.75)
coin_animation_delay = 100
coin_frames = [
    pygame.transform.scale(
        pygame.image.load(resource_path(ASSETS_DIR, f"flame_{i}.png")).convert_alpha(),
        (coin_sprite_size, coin_sprite_size)
    )
    for i in range(1, 8)
]

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

victory_animation_active = False
victory_animation_start_time = 0
victory_teleport_played = False
VICTORY_FADE_IN_TIME = 3000
VICTORY_FADE_OUT_TIME = 3000
VICTORY_ANIMATION_TIME = VICTORY_FADE_IN_TIME + VICTORY_FADE_OUT_TIME

loss_animation_active = False
loss_animation_start_time = 0
LOSS_ANIMATION_TIME = 3000

input_name_screen = True
DEFAULT_NICKNAME = "Неизвестный Огонёчек"
nickname = ""

start_screen = True

game_over = False
result_text = ""
paused = False
exit_confirm_open = False
exit_game_confirm_open = False
settings_open = False
dragging_slider = None
top_reset_message = ""
top_reset_message_time = 0
focused_menu_index = 5

exit_menu_button = pygame.Rect(655, 60, 100, 35)
pause_button = pygame.Rect(620, 20, 75, 35)
continue_button = pygame.Rect(700, 20, 90, 35)
settings_button = pygame.Rect(SCREEN_WIDTH // 2 + 150, 535, 125, 35)
settings_close_button = pygame.Rect(SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 135, 140, 40)
exit_yes_button = pygame.Rect(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 + 45, 110, 40)
exit_no_button = pygame.Rect(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT // 2 + 45, 110, 40)
exit_game_yes_button = pygame.Rect(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 + 45, 110, 40)
exit_game_no_button = pygame.Rect(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT // 2 + 45, 110, 40)
music_slider = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 45, 300, 8)
player_speed_slider = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 25, 300, 8)
enemy_speed_slider = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 95, 300, 8)
reset_top_button = pygame.Rect(SCREEN_WIDTH // 2 - 110, 535, 220, 38)
exit_game_button = pygame.Rect(SCREEN_WIDTH // 2 - 275, 535, 125, 35)
name_continue_button = pygame.Rect(SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT // 2 + 80, 180, 40)
name_clear_button = pygame.Rect(SCREEN_WIDTH // 2 - 190, SCREEN_HEIGHT // 2 + 80, 180, 40)
name_skip_button = pygame.Rect(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 + 130, 260, 40)
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

def get_menu_buttons():
    buttons = []

    for row in get_menu_button_rows():
        buttons.extend(row)

    return buttons

def get_menu_button_rows():
    return [
        [("goal", goal, button) for goal, button in goal_buttons.items()],
        [("difficulty", mode, button) for mode, button in difficulty_buttons.items()],
        [("start", None, start_game_button)],
        [
            ("exit_game", None, exit_game_button),
            ("reset_top", None, reset_top_button),
            ("settings", None, settings_button)
        ]
    ]

def set_menu_focus_by_button(kind, value=None):
    global focused_menu_index

    for index, (button_kind, button_value, _) in enumerate(get_menu_buttons()):
        if button_kind == kind and button_value == value:
            focused_menu_index = index
            return

def set_menu_focus_by_pos(pos):
    global focused_menu_index

    for index, (_, _, rect) in enumerate(get_menu_buttons()):
        if rect.collidepoint(pos):
            focused_menu_index = index
            return

def is_menu_button_focused(kind, value=None):
    menu_buttons = get_menu_buttons()
    focused_kind, focused_value, _ = menu_buttons[focused_menu_index % len(menu_buttons)]
    return focused_kind == kind and focused_value == value

def move_menu_focus(direction):
    global focused_menu_index

    focused_menu_index = (focused_menu_index + direction) % len(get_menu_buttons())

def move_menu_focus_by_direction(dx, dy):
    global focused_menu_index

    rows = get_menu_button_rows()
    flat_index = 0
    current_row_index = 0
    current_column_index = 0

    for row_index, row in enumerate(rows):
        if focused_menu_index < flat_index + len(row):
            current_row_index = row_index
            current_column_index = focused_menu_index - flat_index
            break

        flat_index += len(row)

    current_rect = rows[current_row_index][current_column_index][2]

    if dx != 0:
        row = rows[current_row_index]
        next_column_index = current_column_index + dx

        if 0 <= next_column_index < len(row):
            focused_menu_index += dx

        return

    if dy != 0:
        next_row_index = current_row_index + dy

        if not 0 <= next_row_index < len(rows):
            return

        next_row_start_index = sum(len(row) for row in rows[:next_row_index])
        next_row = rows[next_row_index]
        next_column_index = min(
            range(len(next_row)),
            key=lambda index: abs(next_row[index][2].centerx - current_rect.centerx)
        )
        focused_menu_index = next_row_start_index + next_column_index

def activate_focused_menu_button(current_time):
    global settings_open, win_score, difficulty, top_reset_message, top_reset_message_time
    global exit_game_confirm_open

    kind, value, _ = get_menu_buttons()[focused_menu_index % len(get_menu_buttons())]

    if kind == "settings":
        settings_open = True
    elif kind == "goal":
        win_score = value
    elif kind == "difficulty":
        difficulty = value
    elif kind == "start":
        start_game(current_time)
    elif kind == "exit_game":
        exit_game_confirm_open = True
    elif kind == "reset_top":
        db.clear_top_players()
        top_reset_message = "\u0422\u043e\u043f \u0438\u0433\u0440\u043e\u043a\u043e\u0432 \u043e\u0447\u0438\u0449\u0435\u043d"
        top_reset_message_time = current_time

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

def start_victory_animation(current_time):
    global victory_animation_active, victory_animation_start_time, victory_teleport_played

    victory_animation_active = True
    victory_animation_start_time = current_time
    victory_teleport_played = False

    for enemy in enemies:
        enemy.freeze_animation()

    db.save_score(nickname, score)
    time_sound.stop()
    pygame.mixer.music.stop()

def finish_victory_animation():
    global victory_animation_active, game_over, result_text

    victory_animation_active = False
    game_over = True
    result_text = "Победа"
    play_background_music(win_music, loops=0)

def draw_victory_teleport(current_time):
    elapsed = current_time - victory_animation_start_time

    if elapsed < VICTORY_FADE_IN_TIME:
        circle_alpha = int(255 * (elapsed / VICTORY_FADE_IN_TIME))
        player_alpha = 255
    else:
        fade_out_progress = min(1, (elapsed - VICTORY_FADE_IN_TIME) / VICTORY_FADE_OUT_TIME)
        circle_alpha = int(255 * (1 - fade_out_progress))
        player_alpha = circle_alpha

    circle_size = int(max(player.flame_size * 2.5, player.size * 2.5))
    circle_width = int(circle_size * 1.25)
    scaled_circle = pygame.transform.smoothscale(circle_image, (circle_width, circle_size))
    scaled_circle.set_alpha(circle_alpha)
    circle_rect = scaled_circle.get_rect(center=player.get_rect().center)
    screen.blit(scaled_circle, circle_rect)
    player.draw(screen, alpha=player_alpha)

def start_loss_animation(current_time):
    global loss_animation_active, loss_animation_start_time

    loss_animation_active = True
    loss_animation_start_time = current_time

    for enemy in enemies:
        enemy.freeze_animation()

    db.save_score(nickname, score)
    time_sound.stop()
    play_background_music(lose_music, loops=0)

def finish_loss_animation():
    global loss_animation_active, game_over, result_text

    loss_animation_active = False
    game_over = True
    result_text = "Поражение"

def draw_loss_animation(current_time):
    elapsed = current_time - loss_animation_start_time
    fade_progress = min(1, elapsed / LOSS_ANIMATION_TIME)
    player_alpha = int(255 * (1 - fade_progress))
    player.draw(screen, alpha=player_alpha)

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
    draw_button(settings_close_button, "Закрыть", focused=True)

def draw_exit_confirm_panel():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2 - 100, 440, 200)
    pygame.draw.rect(screen, (255, 255, 255), panel)
    pygame.draw.rect(screen, (0, 0, 0), panel, 2)

    title = font.render("Выйти в главное меню?", True, (0, 0, 0))
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, panel.y + 55))
    screen.blit(title, title_rect)

    draw_button(exit_yes_button, "Да")
    draw_button(exit_no_button, "Нет")

def draw_exit_game_confirm_panel():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2 - 100, 440, 200)
    pygame.draw.rect(screen, (255, 255, 255), panel)
    pygame.draw.rect(screen, (0, 0, 0), panel, 2)

    title = font.render("Выйти из игры?", True, (0, 0, 0))
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, panel.y + 55))
    screen.blit(title, title_rect)

    draw_button(exit_game_yes_button, "Да")
    draw_button(exit_game_no_button, "Нет")

def draw_button(rect, text, selected=False, disabled=False, focused=False):
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

    if focused and not disabled:
        focus_rect = rect.inflate(8, 8)
        pygame.draw.rect(screen, (255, 170, 0), focus_rect, 3)

    text_surface = small_font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def draw_focus_rect(rect):
    pygame.draw.rect(screen, (255, 170, 0), rect.inflate(8, 8), 3)

def continue_from_name_screen(use_default=False):
    global input_name_screen, nickname

    if use_default:
        nickname = DEFAULT_NICKNAME
        input_name_screen = False
        return

    nickname = nickname.strip()

    if nickname != "":
        input_name_screen = False

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
    global paused, exit_confirm_open, time_warning_played
    global last_enemy_double_time, enemy_speed_bonus
    global victory_animation_active, victory_animation_start_time, victory_teleport_played
    global loss_animation_active, loss_animation_start_time

    last_enemy_double_time = 0
    enemy_speed_bonus = 0
    victory_animation_active = False
    victory_animation_start_time = 0
    victory_teleport_played = False
    loss_animation_active = False
    loss_animation_start_time = 0

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
    exit_confirm_open = False

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

                if exit_game_confirm_open:
                    if exit_game_yes_button.collidepoint(mouse_pos):
                        running = False
                    elif exit_game_no_button.collidepoint(mouse_pos):
                        exit_game_confirm_open = False

                    continue

                if not input_name_screen and start_screen and settings_button.collidepoint(mouse_pos):
                    set_menu_focus_by_button("settings")
                    settings_open = True
                    continue

            if event.button == 1 and input_name_screen:
                mouse_pos = event.pos

                if name_continue_button.collidepoint(mouse_pos):
                    continue_from_name_screen()

                if name_skip_button.collidepoint(mouse_pos):
                    continue_from_name_screen(use_default=True)

                if name_clear_button.collidepoint(mouse_pos):
                    nickname = ""

            if event.button == 1 and not input_name_screen and start_screen:
                mouse_pos = event.pos
                set_menu_focus_by_pos(mouse_pos)

                if reset_top_button.collidepoint(mouse_pos):
                    db.clear_top_players()
                    top_reset_message = "\u0422\u043e\u043f \u0438\u0433\u0440\u043e\u043a\u043e\u0432 \u043e\u0447\u0438\u0449\u0435\u043d"
                    top_reset_message_time = current_time

                for goal, button in goal_buttons.items():
                    if button.collidepoint(mouse_pos):
                        win_score = goal

                for mode, button in difficulty_buttons.items():
                    if button.collidepoint(mouse_pos):
                        difficulty = mode

                if start_game_button.collidepoint(mouse_pos):
                    start_game(current_time)

                if exit_game_button.collidepoint(mouse_pos):
                    exit_game_confirm_open = True
                    continue

            if event.button == 1 and exit_confirm_open:
                mouse_pos = event.pos

                if exit_yes_button.collidepoint(mouse_pos):
                    time_sound.stop()
                    restart_game()

                if exit_no_button.collidepoint(mouse_pos):
                    exit_confirm_open = False

                continue

            if event.button == 1 and not input_name_screen and not start_screen and not game_over and not victory_animation_active and not loss_animation_active:
                mouse_pos = event.pos

                if exit_menu_button.collidepoint(mouse_pos):
                    exit_confirm_open = True
                    continue

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
            if input_name_screen:
                if event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
                    nickname = nickname[:-1]
                    continue

            if settings_open:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    settings_open = False
                    dragging_slider = None
                    continue

            if exit_game_confirm_open:
                if event.key in (pygame.K_RETURN, pygame.K_y):
                    running = False
                    continue

                if event.key in (pygame.K_ESCAPE, pygame.K_n):
                    exit_game_confirm_open = False
                    continue

                continue

            if exit_confirm_open:
                if event.key in (pygame.K_RETURN, pygame.K_y):
                    time_sound.stop()
                    restart_game()
                    continue

                if event.key in (pygame.K_ESCAPE, pygame.K_n):
                    exit_confirm_open = False
                    continue

                continue

            if not input_name_screen and start_screen and not settings_open:
                if event.key == pygame.K_DOWN:
                    move_menu_focus_by_direction(0, 1)
                    continue

                if event.key == pygame.K_UP:
                    move_menu_focus_by_direction(0, -1)
                    continue

                if event.key == pygame.K_RIGHT:
                    move_menu_focus_by_direction(1, 0)
                    continue

                if event.key == pygame.K_LEFT:
                    move_menu_focus_by_direction(-1, 0)
                    continue

                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    activate_focused_menu_button(current_time)
                    continue

            if event.key == pygame.K_RETURN:
                if input_name_screen:
                    continue_from_name_screen()
                elif game_over:
                    start_new_game(current_time)

        if event.type == pygame.TEXTINPUT and input_name_screen:
            if event.text.isprintable() and len(nickname) < 15:
                nickname += event.text

    if not start_screen and not game_over and not paused and not settings_open and not exit_confirm_open and not victory_animation_active and not loss_animation_active:
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
            start_loss_animation(current_time)

        if difficulty == "hard" and not game_over and not loss_animation_active:
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

    if not start_screen and not game_over and not paused and not settings_open and not exit_confirm_open and not victory_animation_active and not loss_animation_active and player.get_rect().colliderect(coin_rect):
        score += 1
        player.grow_flame(PLAYER_FLAME_GROWTH)
        coin_sound.play()

        if score >= win_score:
            start_victory_animation(current_time)
        else:
            coin_x = random.randint(0, SCREEN_WIDTH - coin_size)
            coin_y = random.randint(100, SCREEN_HEIGHT - coin_size)

    if not start_screen and not game_over and not paused and not settings_open and not exit_confirm_open and not victory_animation_active and not loss_animation_active:
        for enemy in enemies:
            if player.get_rect().colliderect(enemy.get_rect()):
                start_loss_animation(current_time)
                break

    screen.blit(menu_background, (0, 0))

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
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        name_rect = name_text.get_rect(center=input_box.center)
        screen.blit(title_text, title_rect)
        screen.blit(name_text, name_rect)
        draw_button(name_clear_button, "Очистить", disabled=nickname == "")
        draw_button(name_continue_button, "Продолжить", disabled=nickname.strip() == "")

        draw_button(name_skip_button, "Остаться неизвестным")

        pygame.display.update()
        continue

    if start_screen:
        menu_panel = pygame.Rect(55, 35, 690, 550)
        pygame.draw.rect(screen, (255, 255, 255), menu_panel)
        pygame.draw.rect(screen, (0, 0, 0), menu_panel, 2)

        title_text = font.render("Спасайся, огонёк!", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 70))
        rules = [
            ("Правила игры:", (0, 0, 0)),
            ("Синий огонёчек хочет сбежать от злого волшебника. Повезло, на поляне туман.", (50, 50, 50)),
            ("Собирай частицы огонёчка, чтобы успешно создать заклинание побега.", (50, 50, 50)),
            (f"Надо собрать {win_score} монет, чтобы успешно сбежать.", (50, 50, 50)),
            ("Не попадайся злому волшебнику — он тебя схватит.", (50, 50, 50)),
            ("Удачи сбежать!", (50, 50, 50))
        ]
        mode_text = small_font.render(
            f"Режим: {'лёгкий' if difficulty == 'easy' else 'сложный'}",
            True,
            (0, 150, 0) if difficulty == "easy" else (200, 0, 0)
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
            draw_button(
                button,
                str(goal),
                selected=win_score == goal,
                focused=is_menu_button_focused("goal", goal)
            )

        draw_button(difficulty_buttons["easy"], "Легкий", selected=difficulty == "easy")
        draw_button(difficulty_buttons["hard"], "Сложный", selected=difficulty == "hard")
        screen.blit(mode_text, mode_text_rect)
        draw_button(start_game_button, "Старт")
        draw_button(settings_button, "Настройки")
        draw_button(exit_game_button, "Выход")

        pygame.draw.rect(screen, (255, 255, 255), reset_top_button)
        pygame.draw.rect(screen, (180, 0, 0), reset_top_button, 2)
        screen.blit(reset_top_text, reset_top_text_rect)
        draw_focus_rect(get_menu_buttons()[focused_menu_index % len(get_menu_buttons())][2])

        if top_reset_message and current_time - top_reset_message_time < 2000:
            reset_message = small_font.render(top_reset_message, True, (0, 120, 0))
            reset_message_rect = reset_message.get_rect(center=(SCREEN_WIDTH // 2, 585))
            screen.blit(reset_message, reset_message_rect)

        if settings_open:
            draw_settings_panel()

        if exit_game_confirm_open:
            draw_exit_game_confirm_panel()

        pygame.display.update()
        continue

    screen.blit(game_background, (0, 0))

    victory_finished = game_over and result_text == "Победа"
    loss_finished = game_over and result_text == "Поражение"

    if not victory_animation_active and not victory_finished and not loss_animation_active and not loss_finished:
        coin_frame_index = (pygame.time.get_ticks() // coin_animation_delay) % len(coin_frames)
        coin_draw_x = coin_x + (coin_size - coin_sprite_size) // 2
        coin_draw_y = coin_y + (coin_size - coin_sprite_size) // 2
        screen.blit(coin_frames[coin_frame_index], (coin_draw_x, coin_draw_y))

    for enemy in enemies:
        enemy.draw(screen, frozen=victory_animation_active or victory_finished or loss_animation_active or loss_finished)

    if victory_animation_active:
        if current_time - victory_animation_start_time >= VICTORY_FADE_IN_TIME and not victory_teleport_played:
            teleport_sound.play()
            victory_teleport_played = True

        draw_victory_teleport(current_time)

        if current_time - victory_animation_start_time >= VICTORY_ANIMATION_TIME:
            finish_victory_animation()
    elif loss_animation_active:
        draw_loss_animation(current_time)

        if current_time - loss_animation_start_time >= LOSS_ANIMATION_TIME:
            finish_loss_animation()
    elif not victory_finished and not loss_finished:
        player.draw(screen)

    screen.blit(cloud_overlay, (0, 0))

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

    if not game_over and not victory_animation_active and not loss_animation_active:
        draw_button(exit_menu_button, "Меню")

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

    if exit_confirm_open:
        draw_exit_confirm_panel()

    pygame.display.update()

pygame.quit()
