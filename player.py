import pygame


class Player:
    def __init__(self, x, y, size, speed):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed

    def move(self, keys, screen_width, screen_height):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed

        if keys[pygame.K_RIGHT] and self.x < screen_width - self.size:
            self.x += self.speed

        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed

        if keys[pygame.K_DOWN] and self.y < screen_height - self.size:
            self.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(
            screen,
            (0, 100, 255),
            (self.x, self.y, self.size, self.size)
        )

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)