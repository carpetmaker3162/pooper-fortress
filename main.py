from entity.entity import Entity
from entity.enemy import Enemy
from entity.tower import Tower, Turret
from utils.misc import floor_to_nearest
import random
import pygame

pygame.init()

class Game:
    def __init__(self, fps):
        self.screen_width = 900
        self.screen_height = 600
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height), flags=pygame.SCALED, vsync=1)
        self.game_stopped = False
        self.player_died = False

        self.player = Entity(
            image="assets/player.png",
            spawn=(self.screen_width//2, self.screen_height//2),
            size=(50, 50),
            hp=200
        )
        self.enemies = pygame.sprite.Group()
        self.towers = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
    
    def process_events(self):
        pygame.event.pump()
        self.mouse_pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_stopped = True
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.process_mouse_events()
    
    def process_mouse_events(self):
        mx, my = floor_to_nearest(self.mouse_pos, (50, 50))
        self.towers.add(Tower(
            spawn=(mx, my),
            size=(100, 100),
            hp=100,
            turret_rate=500,
            turret_dmg=20
        ))
    
    def update(self):
        self.towers.update(self.enemies)

        # draw towers, bullets, and turrets
        for tower in self.towers:
            tower.draw(self.screen)
            for bullet in tower.bullets:
                self.bullets.add(bullet)
            tower.turret.draw(self.screen)
        self.bullets.draw(self.screen)

        self.enemies.update(self.player, self.towers, self.bullets)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        self.player.update([])
        if self.player.hp <= 0:
            self.player_died = True
        if not self.player_died:
            self.player.draw(self.screen)
        
        if random.random() < 0.05:
            self.enemies.add(Enemy(
                spawn=(random.randint(0, 800), 100),
                size=(50, 50),
                hp=100,
                speed=2,
                target=(450, 300)
            ))
    
    def loop(self):
        while not self.game_stopped:
            self.process_events()
            pygame.event.pump()

            self.screen.fill((255, 255, 255))
            self.update()
            
            pygame.display.flip()

if __name__ == "__main__":
    game = Game(fps=60)
    game.loop()
    pygame.quit()