from entity.entity import Entity
from entity.bullet import Bullet
from utils.misc import find_nearest
import pygame
import math

# TODO: add different types of turrets


class Turret(Entity):
    def __init__(self,
                 image="assets/gun.png",
                 spawn=(0, 0),
                 size=(100, 100),
                 rate=500,
                 dmg=20):

        super().__init__(image, spawn, size)

        self.ang = 0
        self.rate = rate
        self.dmg = dmg


class Tower(Entity):
    def __init__(self,
                 image="assets/tower.png",
                 spawn=(0, 0),
                 size=(100, 100),
                 hp=100,
                 turret_rate=500,
                 turret_dmg=20):

        super().__init__(image, spawn, size, hp)

        # determine turret dimensions and location
        tw, th = int(self.width * 0.8), int(self.height * 0.8)
        tx, ty = self.rect.center[0] - tw//2, self.rect.center[1] - th//2

        self.last_fired = 0
        self.turret = Turret(
            spawn=(tx, ty),
            size=(tw, th),
            rate=turret_rate,
            dmg=turret_dmg
        )
        self.bullets = pygame.sprite.Group()

    def shoot(self, entity):
        if entity is not None:
            x1, y1 = self.rect.center
            x2, y2 = entity.rect.center
            self.bullets.add(Bullet(
                spawn=(x1, y1),
                target=(x2, y2),
                speed=10,
                lifetime=1500,
                team=0,
            ))
            self.turret.ang = 270 - math.degrees(math.atan2(y2-y1, x2-x1))

    def update(self, enemies):
        super().update([])

        # shoot the nearest enemy
        nearest_enemy = find_nearest(self, enemies)
        if pygame.time.get_ticks() > self.last_fired + self.turret.rate:
            self.last_fired = pygame.time.get_ticks()
            self.shoot(nearest_enemy)

        # kill bullets if their lifetime is over
        for bullet in self.bullets:
            bullet.update()
