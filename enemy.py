import pygame


class Enemy:
    def __init__(self, x, y, size, speed_x, speed_y):
        self.x = x
        self.y = y
        self.size = size
        self.speed_x = speed_x
        self.speed_y = speed_y

    def move(self, screen_width, screen_height):
        self.x += self.speed_x
        self.y += self.speed_y

        if self.x <= 0 or self.x >= screen_width - self.size:
            self.speed_x *= -1

        if self.y <= 100 or self.y >= screen_height - self.size:
            self.speed_y *= -1

    def draw(self, screen):
        pygame.draw.rect(
            screen,
            (220, 0, 0),
            (self.x, self.y, self.size, self.size)
        )

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)