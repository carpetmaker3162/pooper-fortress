from entity.entity import Entity
from entity.enemy import Enemy
from entity.tower import Tower, Turret
from utils.misc import floor_to_nearest
from utils.button import Button
import random
import pygame

pygame.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
TOOLBAR_HEIGHT = 100

WAVES = [
    {
        "enemy_count": 5,
        "freq": (1000, 3000),
    },
    {
        "enemy_count": 10,
        "freq": (500, 3000),
    },
    {
        "enemy_count": 20,
        "freq": (500, 2000),
    },
    {
        "enemy_count": 30,
        "freq": (500, 1000),
    },
    {
        "enemy_count": 50,
        "freq": (250, 1000),
    },
]

# TODO: add waves, and preparation period in between to fix / modify base
class Game:
    def __init__(self, fps):
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT + TOOLBAR_HEIGHT), flags=pygame.SCALED, vsync=1)
        self.game_stopped = False
        self.player_died = False
        self.wave_in_progress = False
        self.wave = 1
        
        self.enemies_remaining = WAVES[self.wave - 1]["enemy_count"]
        self.freq = WAVES[self.wave - 1]["freq"]
        self.next_spawn = random.randint(1000, 3000)
        self.last_spawn = 0

        self.clock = pygame.time.Clock()
        self.framecap = fps

        self.player = Entity(
            image="assets/player.png",
            spawn=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2),
            size=(50, 50),
            hp=200
        )
        self.enemies = pygame.sprite.Group()
        self.towers = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.buttons = pygame.sprite.Group()

        self.buttons.add(Button(image="assets/none.png",
                        x=825, y=625, width=50, height=50,
                        id="nextwave"))
        
        self.enemies.add(Enemy(
                spawn=(random.randint(0, 800), 100),
                size=(50, 50),
                hp=100,
                speed=2,
                target=(450, 300)
            ))
        
        # grid that mirrors current layout
        self.grid = [[0] * SCREEN_WIDTH for _ in range(SCREEN_HEIGHT)]
    
    def process_events(self):
        self.mouse_pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_stopped = True
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.process_mouse_events()
    
    # add tower on click, change later
    def process_mouse_events(self):
        mouse_x, mouse_y = self.mouse_pos
        
        if mouse_y <= SCREEN_HEIGHT:
            rounded_x, rounded_y = floor_to_nearest((mouse_x, mouse_y), (50, 50))
            self.add_tower(rounded_x, rounded_y)
        else:
            self.process_button_presses(mouse_x, mouse_y)
    
    def process_button_presses(self, x, y):
        for button in self.buttons:
            if not button.is_hovering(x, y):
                continue

            if button.id == "nextwave" and self.wave_in_progress == False:
                self.wave += 1
                self.wave_in_progress = True
                self.enemies_remaining = WAVES[self.wave - 1]["enemy_count"]
                self.freq = WAVES[self.wave - 1]["freq"]
    
    def add_tower(self, x, y):
        if self.wave_in_progress:
            return

        grid_x = x//50
        grid_y = y//50

        if self.grid[grid_y][grid_x] == 1:
            return

        self.towers.add(Tower(
            spawn=(x, y),
            size=(50, 50),
            hp=100,
            turret_rate=500,
            turret_dmg=20
        ))
        self.grid[grid_y][grid_x] = 1
    
    def update(self):
        current_time = pygame.time.get_ticks()
        self.towers.update(self.enemies)

        if self.enemies_remaining == 0:
            self.wave_in_progress = False
            # reset grid
            self.grid = [[0] * SCREEN_WIDTH for _ in range(SCREEN_HEIGHT)]

        # draw towers, bullets, and turrets
        for tower in self.towers:
            tower.draw(self.screen)
            for bullet in tower.bullets:
                self.bullets.add(bullet)
            tower.turret.draw(self.screen)

            # re-add existing towers to grid
            grid_x = tower.x//50
            grid_y = tower.y//50
            self.grid[grid_y][grid_x] = 1

        self.bullets.draw(self.screen)

        # update and draw enemies
        self.enemies.update(self.player, [], self.bullets)
        for enemy in self.enemies:
            enemy.draw(self.screen) # have to loop to draw hp bars
        
        # update and draw player
        self.player.update([])
        if self.player.hp <= 0:
            self.player_died = True
        if not self.player_died:
            self.player.draw(self.screen)
        
        # if (current_time > self.last_spawn + self.next_spawn 
        #         and self.wave_in_progress):
        #     self.last_spawn = current_time
        #     self.enemies_remaining -= 1
        #     self.next_spawn = random.randint(*self.freq)
        #     self.enemies.add(Enemy(
        #         spawn=(random.randint(0, 800), 100),
        #         size=(50, 50),
        #         hp=100,
        #         speed=2,
        #         target=(450, 300)
        #     ))
        
        self.buttons.draw(self.screen)
        self.clock.tick(self.framecap)
    
    def loop(self):
        while not self.game_stopped:
            self.process_events()
            pygame.event.pump()

            pygame.draw.rect(self.screen, (255, 255, 230), pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            self.update()
            
            pygame.display.flip()

if __name__ == "__main__":
    game = Game(fps=60)
    game.loop()
    pygame.quit()