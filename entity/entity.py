import pygame
import math
from utils.img import get_image
from utils.misc import sign, decrement


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
        # if self.hitbox:
        # pygame.draw.rect(screen, pygame.Color(
        #     255, 0, 0), self.rect, width=5)
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
        #while self.colliding_at(dx, dy, collidables) and (dx != 0 or dy != 0):
        #    if dx != 0:
        #        dx -= decrement(dx)
        #    elif dy != 0:
        #        dy -= decrement(dy)

        self.x += dx
        self.y += dy

        #self.rect.move_ip((dx, dy))
        #self.rect.topleft = (self.x, self.y)
        def r(val):
            if val >= 0:
                return math.floor(val)
            else:
                return math.ceil(val)
        self.rect.topleft = (r(self.x), r(self.y))

    def colliding_at(self, x, y, entities):
        # self.rect.move_ip((x, y))
        # colliding = pygame.sprite.spritecollideany(self, entities)
        # self.rect.move_ip((-x, -y))
        # return colliding
        left = self.x + x
        top = self.y + y
        right = left + self.width
        bottom = top + self.height
        
        for entity in entities:
            if (entity.rect.left < right and entity.rect.right > left
                    and entity.rect.top < bottom and entity.rect.bottom > top):
                return entity

    def update(self, bullets):
        if not self.invulnerable:
            for bullet in pygame.sprite.spritecollide(self, bullets, False):
                if bullet.team != self.team:
                    self.hp -= bullet.damage
                    bullet.kill()

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
