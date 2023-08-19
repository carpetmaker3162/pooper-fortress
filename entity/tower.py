from entity.entity import Entity
from entity.bullet import Bullet
from utils.misc import find_nearest
import pygame
import math

class Tower(Entity):
    def __init__(self,
                 type="gun",
                 spawn=(0, 0),
                 size=(100, 100),
                 hp=100,
                 turret_rate=500,
                 turret_dmg=20,
                 turret_aoe=0):
        
        turret_image_path = f"assets/turrets/{type}.png"
        self.bullet_image_path = f"assets/bullets/{type}.png"

        super().__init__("assets/tower.png", spawn, size, hp)

        # determine turret dimensions and location
        tw, th = int(self.width * 0.8), int(self.height * 0.8)
        tx, ty = self.rect.center[0] - tw//2, self.rect.center[1] - th//2
        self.turret = Entity(
            image=turret_image_path,
            spawn=(tx, ty),
            size=(tw, th)
        )

        self.last_fired = 0
        self.bullets = pygame.sprite.Group()
        
        self.turret_rate = turret_rate
        self.turret_dmg = turret_dmg
        self.turret_aoe = turret_aoe # splash range of each bullet, not the range of the tower (but do need to add that)

    def shoot(self, entity):
        if entity is not None:
            x1, y1 = self.rect.center
            x2, y2 = entity.rect.center
            self.bullets.add(Bullet(
                image=self.bullet_image_path,
                spawn=(x1, y1),
                target=(x2, y2),
                speed=10,
                lifetime=1500,
                damage=self.turret_dmg,
                aoe_range=self.turret_aoe,
                team=0,
            ))
            
            self.turret.ang = 270 - math.degrees(math.atan2(y2-y1, x2-x1))

    def update(self, enemies):
        super().update()

        # shoot the nearest enemy
        nearest_enemy = find_nearest(self, enemies)
        if pygame.time.get_ticks() > self.last_fired + self.turret_rate:
            self.last_fired = pygame.time.get_ticks()
            self.shoot(nearest_enemy)

        # kill bullets if their lifetime is over
        for bullet in self.bullets:
            bullet.update(enemies)
