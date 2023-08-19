import pygame
import math
from utils.img import get_image
from utils.misc import distance, decrement, collide_aabb


class Entity(pygame.sprite.Sprite):
    def __init__(self,
                 image="assets/none.png",
                 spawn=(0, 0),
                 size=(100, 100),
                 hp=-1):

        super().__init__()
        self.width, self.height = size
        self.x, self.y = spawn
        self.ang = 0

        self.image = get_image(image, self.width, self.height)
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)

        self.hp_bar_size = self.width

        self.x_speed = 0
        self.y_speed = 0
        self.invulnerable = False

        self.hp = hp
        self.max_hp = self.hp

        if hp < 0:  # invulnerable if negative
            self.invulnerable = True

    def draw(self, screen):
        # rotate if needed
        rotated_image = pygame.transform.rotate(self.image, self.ang)
        current_center = (self.x + self.width//2, self.y + self.height//2)
        new_rect = rotated_image.get_rect(center=current_center)

        screen.blit(rotated_image, new_rect.topleft)

        if self.hp != self.max_hp and not self.invulnerable:
            self.draw_hp_bar(screen)

    def move(self, x, y, collidables):
        dx = x
        dy = y

        while self.colliding_at(dx, 0, collidables) and dx != 0:
            dx -= decrement(dx)
        while self.colliding_at(0, dy, collidables) and dy != 0:
            dy -= decrement(dy)

        self.x += dx
        self.y += dy

        self.rect.topleft = (round(self.x), round(self.y))

    # return an entity currently collided with, if any
    def colliding_at(self, x, y, entities):
        for entity in entities:
            if collide_aabb(self, entity, x, y):
                return entity

    # self kill & dmg handling
    def update(self):
        if self.hp <= 0 and not self.invulnerable:
            self.kill()
            # remove own bullets
            if hasattr(self, "bullets"):
                for bullet in self.bullets:
                    bullet.kill()

    def draw_hp_bar(self, screen: pygame.Surface, x_offset=0):
        pos = (self.x - x_offset - ((self.hp_bar_size - self.width)), self.y - 15)
        size = (self.hp_bar_size, 10)
        pygame.draw.rect(screen, (0, 0, 0), (pos, size), 1)
        bar_pos = (pos[0] + 3, pos[1] + 3)
        bar_size = ((size[0] - 6) * (self.hp / self.max_hp), size[1] - 6)
        pygame.draw.rect(screen, (0, 255, 0), (*bar_pos, *bar_size))

    # return whether or not a point lies on the entity
    def lies_on(self, x, y):
        if (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height):
            return True
        else:
            return False
