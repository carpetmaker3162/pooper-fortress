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
        "enemy_count": 50,
        "freq": (100, 300),
    },
    {
        "enemy_count": 100,
        "freq": (50, 300),
    },
    {
        "enemy_count": 200,
        "freq": (50, 200),
    },
    {
        "enemy_count": 300,
        "freq": (50, 100),
    },
    {
        "enemy_count": 500,
        "freq": (25, 100),
    },
]

TOWERS = {
    "gun": {
        "type": "gun",
        "size": (50, 50),
        "hp": 100,
        "turret_rate": 500,
        "turret_dmg": 20,
    },
    "cannon": {
        "type": "cannon",
        "size": (50, 50),
        "hp": 100,
        "turret_rate": 1000,
        "turret_dmg": 45,
    }
}

# TODO: add waves, and preparation period in between to fix / modify base


class Game:
    def __init__(self, fps):
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT + TOOLBAR_HEIGHT), flags=pygame.SCALED, vsync=1)
        
        self.clock = pygame.time.Clock()
        self.framecap = fps
        self.event_ticker = 0
        self.mouse_pressed = False
        
        self.game_stopped = False
        self.player_died = False
        self.wave_in_progress = False
        self.wave = 1
        self.enemies_remaining = WAVES[self.wave - 1]["enemy_count"]
        self.freq = WAVES[self.wave - 1]["freq"]
        self.next_spawn = random.randint(1000, 3000)
        self.last_spawn = 0

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

        self.buttons.add(Button(image="assets/nextwave.png",
                                x=750, y=600, width=100, height=100,
                                id="nextwave"))
        
        self.current_tower = "gun"
        for i, tower_name in enumerate(TOWERS.keys()):
            self.buttons.add(Button(image=f"assets/turrets/{tower_name}.png",
                                x=25 + 100*i, y=625, width=50, height=50,
                                id=tower_name))

        # grid that mirrors current layout
        self.grid = [[0] * SCREEN_WIDTH for _ in range(SCREEN_HEIGHT)]

    def process_events(self):
        self.mouse_pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()
        self.event_ticker += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_stopped = True
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_pressed = True
            
            if event.type == pygame.MOUSEBUTTONUP:
                self.mouse_pressed = False
        
        #if self.event_ticker % 4 == 0:
        if self.mouse_pressed and pygame.mouse.get_pressed()[0]:
            self.process_mouse_events()

    # add tower on click
    def process_mouse_events(self):
        mouse_x, mouse_y = self.mouse_pos

        if mouse_y <= SCREEN_HEIGHT:
            # mouse click on game canvas
            rounded_x, rounded_y = floor_to_nearest(
                (mouse_x, mouse_y), (50, 50))
            self.add_tower(rounded_x, rounded_y)
        else:
            # mouse click on toolbar
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
            elif button.id in TOWERS.keys():
                self.current_tower = button.id

    def add_tower(self, x, y):
        if self.wave_in_progress:
            return

        grid_x = x//50
        grid_y = y//50

        if self.grid[grid_y][grid_x] == 1:
            return
        
        tower_data = TOWERS[self.current_tower]
        self.towers.add(Tower(
            spawn=(x, y),
            **tower_data
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
        self.enemies.update(self.player, self.towers, self.bullets)
        for enemy in self.enemies:
            enemy.draw(self.screen)  # have to loop to draw hp bars

        # update and draw player
        self.player.update([])
        if self.player.hp <= 0:
            self.player_died = True
        if not self.player_died:
            self.player.draw(self.screen)

        # spawn enemies if wave in progress
        if (current_time > self.last_spawn + self.next_spawn
                and self.wave_in_progress):
            self.last_spawn = current_time
            self.enemies_remaining -= 1
            self.next_spawn = random.randint(*self.freq)
            self.enemies.add(Enemy(
                spawn=(random.randint(0, 800), 100),
                size=(50, 50),
                hp=100,
                speed=2,
                target=(450, 300)
            ))

        self.buttons.draw(self.screen)
        self.clock.tick(self.framecap)

    def loop(self):
        while not self.game_stopped:
            self.process_events()
            pygame.event.pump()
            pygame.draw.rect(self.screen, (255, 255, 230),
                             pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(self.screen, (200, 200, 200),
                             pygame.Rect(0, SCREEN_HEIGHT, SCREEN_WIDTH, TOOLBAR_HEIGHT))
            self.update()
            pygame.display.flip()


if __name__ == "__main__":
    game = Game(fps=60)
    game.loop()
    pygame.quit()
