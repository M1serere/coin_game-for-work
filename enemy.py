import pygame
import os


class Enemy:
    def __init__(self, x, y, size, speed_x, speed_y):
        self.x = x
        self.y = y
        self.size = size
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.animation_delay = 100
        self.frames = {
            "left": self.load_frames("left"),
            "right": self.load_frames("right")
        }
        self.frozen_direction = None
        self.frozen_frame_index = 0

    def load_frames(self, direction):
        return [
            pygame.transform.scale(
                pygame.image.load(os.path.join("assets", f"enemy_{direction}_{i}.png")).convert_alpha(),
                (self.size, self.size)
            )
            for i in range(1, 9)
        ]

    def move(self, screen_width, screen_height):
        self.x += self.speed_x
        self.y += self.speed_y

        if self.x <= 0 or self.x >= screen_width - self.size:
            self.speed_x *= -1

        if self.y <= 100 or self.y >= screen_height - self.size:
            self.speed_y *= -1

    def freeze_animation(self):
        self.frozen_direction = "right" if self.speed_x >= 0 else "left"
        self.frozen_frame_index = (
            pygame.time.get_ticks() // self.animation_delay
        ) % len(self.frames[self.frozen_direction])

    def draw(self, screen, frozen=False):
        if frozen and self.frozen_direction is not None:
            direction = self.frozen_direction
            frame_index = self.frozen_frame_index
        else:
            direction = "right" if self.speed_x >= 0 else "left"
            frame_index = (pygame.time.get_ticks() // self.animation_delay) % len(self.frames[direction])

        screen.blit(self.frames[direction][frame_index], (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)
