from entity.entity import Entity
from utils.misc import find_xy_speed
import pygame

class Bullet(Entity):
    def __init__(self,
            image="assets/bullet.png",
            spawn=(0, 0),
            target=(0, 0),
            speed=100,
            lifetime=8000,
            damage=10,
            team=0):

        super().__init__(image, spawn, (15, 15))
        
        self.x_speed, self.y_speed = find_xy_speed(speed, spawn, target)

        self.lifetime = lifetime
        self.life_begin = pygame.time.get_ticks()
        self.damage = damage
        self.team = team
    
    def update(self):
        self.move(self.x_speed, self.y_speed, [])
        if pygame.time.get_ticks() - self.life_begin > self.lifetime:
            self.kill()

    def move(self, x, y, collidables):
        dx = x
        dy = y

        if self.colliding_at(dx, dy, collidables):
            self.kill()

        self.y += dy
        self.x += dx

        self.rect.move_ip((dx, dy))