from entity.entity import Entity
from utils.misc import find_xy_speed, distance
import pygame


class Enemy(Entity):
    def __init__(self,
                 image="assets/enemy.png",
                 spawn=(100, 100),
                 size=(50, 50),
                 hp=100,
                 attack_freq=1000,
                 attack_dmg=40,
                 speed=2,
                 target=(450, 300)):

        super().__init__(image, spawn, size, hp)

        self.speed = speed
        self.target = target
        self.attack_freq = attack_freq
        self.attack_dmg = attack_dmg
        self.last_attack = 0
        self.team = 1

    def update(self, player, towers, bullets):
        super().update(bullets)

        # move diagonally towards self.target
        # TODO: add pathfinding for enemies in case there is a path to the player
        self.x_speed, self.y_speed = find_xy_speed(
            self.speed, (self.x, self.y), self.target)

        # if in proximity move the enemy direclty over target to prevent oscillation
        # might be unnecessary later because i plan on having
        # enemies NOT overlap the player and just bump into it
        dist = distance((self.x, self.y), self.target)
        if dist <= self.speed:
            self.x, self.y = self.target
            self.rect.topleft = self.target
        else:
            self.move(self.x_speed, self.y_speed, towers)

        # attack nearby towers or the player. prioritize the player
        print(player.rect, self.rect)
        if self.rect.colliderect(player.rect):
            self.attack(player)
        else:
            nearby_tower = self.colliding_at(
                self.x_speed, self.y_speed, towers)
            if nearby_tower is not None:
                self.attack(nearby_tower)

    def attack(self, entity):
        if pygame.time.get_ticks() > self.last_attack + self.attack_freq:
            self.last_attack = pygame.time.get_ticks()
            entity.hp -= self.attack_dmg
