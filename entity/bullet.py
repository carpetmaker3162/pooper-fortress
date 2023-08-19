from entity.entity import Entity
from utils.misc import find_xy_speed, collide_aabb, distance
import pygame


class Bullet(Entity):
    def __init__(self,
                 image="assets/bullet.png",
                 spawn=(0, 0),
                 target=(0, 0),
                 speed=100,
                 lifetime=8000,
                 damage=10,
                 aoe_range=0,
                 team=0):

        super().__init__(image, spawn, (15, 15))

        self.x_speed, self.y_speed = find_xy_speed(speed, spawn, target)

        self.lifetime = lifetime
        self.life_begin = pygame.time.get_ticks()
        
        self.damage = damage
        self.aoe_range = aoe_range
        self.team = team

    def update(self, enemies):
        self.move(self.x_speed, self.y_speed, [])
        if pygame.time.get_ticks() - self.life_begin > self.lifetime:
            self.kill()
        
        hit = False
        do_direct_hit = False
        if pygame.sprite.spritecollide(self, enemies, False):
            hit = True
            do_direct_hit = True
            self.kill()
        
        for enemy in enemies:
            if do_direct_hit and collide_aabb(self, enemy):
                enemy.hp -= self.damage
                do_direct_hit = False
            elif hit:
                enemy.hp -= self.damage * self.aoe_dropoff(enemy)
    
    def aoe_dropoff(self, enemy):
        dist = distance((self.x + self.width/2, self.y + self.height/2), 
                        (enemy.x + enemy.width/2, enemy.y + enemy.height/2))
        
        if dist > self.aoe_range:
            return 0
        
        try:
            return (self.aoe_range - dist) / self.aoe_range
        except ZeroDivisionError:
            return 0

    def move(self, x, y, collidables):
        dx = x
        dy = y

        if self.colliding_at(dx, dy, collidables):
            self.kill()

        self.y += dy
        self.x += dx

        self.rect.move_ip((dx, dy))
