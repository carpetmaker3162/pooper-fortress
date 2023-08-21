from entity.entity import Entity
from entity.bullet import Bullet
from utils.misc import find_nearest, get_angle, get_displacement
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
                 turret_aoe=0,
                 turret_knockback=0,
                 turret_speed=10,
                 turret_range=500,
                 turret_multishot=1,
                 turret_multishot_spread=0):
        
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
        
        self.turret_rate = turret_rate # ms between attack
        self.turret_dmg = turret_dmg
        self.turret_aoe = turret_aoe # splash range of each bullet, not the range of the tower (but do need to add that)
        self.turret_knockback = turret_knockback
        self.turret_speed = turret_speed # bullet speed (px/frame)
        self.turret_range = turret_range # range in px
        self.turret_multishot = turret_multishot # amount of bullets to add to multishot (on both sides)
        self.turret_multishot_spread = turret_multishot_spread # angle between each multishot bullet

    def shoot(self, entity, fps):
        if entity is None:
            return
        
        lifetime = 1000 * self.turret_range / self.turret_speed / fps # s = px / px/f / f/s
        x1, y1 = self.rect.center
        x2, y2 = entity.rect.center
        bullet_angle = get_angle((x1, y1), (x2, y2))
        self.turret.ang = bullet_angle

        for i in range(self.turret_multishot):
            angle_with_spread = bullet_angle + i*self.turret_multishot_spread
            dx, dy = get_displacement(angle_with_spread, 10)
            new_bullet = Bullet(
                image=self.bullet_image_path,
                spawn=(x1, y1),
                target=(x1+dx, y1+dy),
                speed=self.turret_speed,
                lifetime=lifetime,
                damage=self.turret_dmg,
                aoe_range=self.turret_aoe,
                knockback=self.turret_knockback,
                team=0,
            )
            self.bullets.add(new_bullet)
            new_bullet.ang = angle_with_spread
            if i != 0: # NOTE: rewrite this later this is getting long as hell
                angle_with_spread = bullet_angle - i*self.turret_multishot_spread
                dx, dy = get_displacement(angle_with_spread, 10)
                new_bullet = Bullet(
                    image=self.bullet_image_path,
                    spawn=(x1, y1),
                    target=(x1+dx, y1+dy),
                    speed=self.turret_speed,
                    lifetime=lifetime,
                    damage=self.turret_dmg,
                    aoe_range=self.turret_aoe,
                    knockback=self.turret_knockback,
                    team=0,
                )
                self.bullets.add(new_bullet)
                new_bullet.ang = angle_with_spread
    
    def draw(self, screen):
        super().draw(screen)
        for bullet in self.bullets:
            bullet.draw(screen)

    def update(self, enemies, game_fps):
        super().update()

        # shoot the nearest enemy
        nearest_enemy = find_nearest(self, enemies)
        if pygame.time.get_ticks() > self.last_fired + self.turret_rate:
            self.last_fired = pygame.time.get_ticks()
            self.shoot(nearest_enemy, game_fps)

        aoe_hits = []
        for bullet in self.bullets:
            bullet.update(enemies)
            if bullet.hit and bullet.aoe_range > 0:
                aoe_hits.append(bullet)
        return aoe_hits