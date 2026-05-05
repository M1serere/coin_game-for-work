import pygame
from paths import resource_path


class Player:
    def __init__(self, x, y, size, speed):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.animation_delay = 100
        self.flame_size = size
        self.source_frames = [
            pygame.image.load(resource_path("assets", f"flame_{i}.png")).convert_alpha()
            for i in range(1, 7)
        ]
        self.update_frames()

    def update_frames(self):
        self.sprite_width = int(self.flame_size * 0.75)
        self.sprite_height = int(self.flame_size * 1.5)
        self.frames = [
            pygame.transform.scale(frame, (self.sprite_width, self.sprite_height))
            for frame in self.source_frames
        ]

    def grow_flame(self, amount):
        self.flame_size += amount
        self.update_frames()

    def move(self, keys, screen_width, screen_height, top_limit=100):
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.x > 0:
            self.x -= self.speed

        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.x < screen_width - self.size:
            self.x += self.speed

        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.y > top_limit:
            self.y = max(top_limit, self.y - self.speed)

        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.y < screen_height - self.size:
            self.y += self.speed

    def draw(self, screen, alpha=255):
        frame_index = (pygame.time.get_ticks() // self.animation_delay) % len(self.frames)
        draw_x = self.x + (self.size - self.sprite_width) // 2
        draw_y = self.y - (self.sprite_height - self.size)
        frame = self.frames[frame_index]

        if alpha < 255:
            frame = frame.copy()
            frame.set_alpha(alpha)

        screen.blit(frame, (draw_x, draw_y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)
