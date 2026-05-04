import pygame
import os


class Player:
    def __init__(self, x, y, size, speed):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.animation_delay = 100
        self.sprite_width = int(self.size * 0.75)
        self.sprite_height = int(self.size * 1.5)
        self.frames = [
            pygame.transform.scale(
                pygame.image.load(os.path.join("assets", f"flame_{i}.png")).convert_alpha(),
                (self.sprite_width, self.sprite_height)
            )
            for i in range(1, 7)
        ]

    def move(self, keys, screen_width, screen_height, top_limit=100):
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.x > 0:
            self.x -= self.speed

        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.x < screen_width - self.size:
            self.x += self.speed

        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.y > top_limit:
            self.y = max(top_limit, self.y - self.speed)

        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.y < screen_height - self.size:
            self.y += self.speed

    def draw(self, screen):
        frame_index = (pygame.time.get_ticks() // self.animation_delay) % len(self.frames)
        draw_x = self.x + (self.size - self.sprite_width) // 2
        draw_y = self.y - (self.sprite_height - self.size)
        screen.blit(self.frames[frame_index], (draw_x, draw_y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)
