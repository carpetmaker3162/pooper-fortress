from entity.entity import Entity
from entity.enemy import Enemy
from entity.tower import Tower
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
        "enemy_count": 20,
        "freq": (200, 600),
    },
    {
        "enemy_count": 40,
        "freq": (200, 600),
    },
    {
        "enemy_count": 50,
        "freq": (100, 300),
    },
    {
        "enemy_count": 100,
        "freq": (100, 300),
    },
    {
        "enemy_count": 200,
        "freq": (100, 300),
    },
]

TOWERS = {
    "gun": {
        "type": "gun",
        "size": (50, 50),
        "hp": 200,
        "turret_rate": 500,
        "turret_dmg": 10,
        "turret_aoe": 0,
        "turret_speed": 12,
        "turret_range": 400,
        "turret_knockback": 1,
        "turret_multishot": 1,
        "turret_multishot_spread": 0,
    },
    "cannon": {
        "type": "cannon",
        "size": (50, 50),
        "hp": 200,
        "turret_rate": 1000,
        "turret_dmg": 25,
        "turret_aoe": 100,
        "turret_speed": 8,
        "turret_range": 300,
        "turret_knockback": 2,
        "turret_multishot": 1,
        "turret_multishot_spread": 0,
    },
    "bomb": {
        "type": "bomb",
        "size": (50, 50),
        "hp": 200,
        "turret_rate": 1500,
        "turret_dmg": 40,
        "turret_aoe": 200,
        "turret_speed": 5,
        "turret_range": 400,
        "turret_knockback": 4,
        "turret_multishot": 1,
        "turret_multishot_spread": 0,
    },
    "shotgun": {
        "type": "shotgun",
        "size": (50, 50),
        "hp": 200,
        "turret_rate": 500,
        "turret_dmg": 4,
        "turret_aoe": 0,
        "turret_speed": 8,
        "turret_range": 150,
        "turret_knockback": 8,
        "turret_multishot": 2,
        "turret_multishot_spread": 10,
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
        self.fps = 0
        
        self.game_stopped = False
        self.player_died = False
        self.wave_in_progress = False
        self.wave = 0
        self.enemies_remaining = WAVES[self.wave - 1]["enemy_count"]
        self.freq = WAVES[self.wave - 1]["freq"]
        self.next_spawn = random.randint(1000, 3000)
        self.last_spawn = 0
        self.hits = [] # to record aoe hits for splash animations
        self.splash_animation_duration = 100
        self.delete_mode = False

        self.player = Entity(
            image="assets/player.png",
            spawn=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2),
            size=(50, 50),
            hp=2000
        )
        self.enemies = pygame.sprite.Group()
        self.towers = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group() # unused
        self.buttons = pygame.sprite.Group()

        self.buttons.add(Button(image="assets/nextwave.png",
                                x=750, y=600, width=100, height=100,
                                id="nextwave"))
        
        self.current_tower = "gun"
        for i, tower_name in enumerate(TOWERS.keys()):
            self.buttons.add(Button(image=f"assets/turrets/{tower_name}.png",
                             x=25 + 100*i, y=625, width=50, height=50,
                             id=tower_name))
        
        self.buttons.add(Button(image=f"assets/trash.png",
                         x=25 + 100*(i + 1), y=625, width=50, height=50,
                         id="delete"))

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
                self.delete_mode = False
                self.current_tower = button.id
            elif button.id == "delete":
                self.delete_mode = True

    def add_tower(self, x, y):
        if self.wave_in_progress:
            return

        tower_data = TOWERS[self.current_tower]
        tower = Tower(
            spawn=(x, y),
            **tower_data
        )

        grid_y = y//50
        grid_x = x//50
        grid_square = self.grid[grid_y][grid_x]
        
        if isinstance(grid_square, Tower):
            if self.delete_mode:
                grid_square.kill()
                self.grid[grid_y][grid_x] = 0
                return
            if grid_square.hp != grid_square.max_hp:
                grid_square.kill() # replace a broken tower, not sure if this will cause a bug
            else:
                return
        
        if not self.delete_mode:
            self.towers.add(tower)
            self.grid[grid_y][grid_x] = tower

    def update(self):
        current_time = pygame.time.get_ticks()

        if self.enemies_remaining == 0:
            self.wave_in_progress = False
            # reset grid
            self.grid = [[0] * SCREEN_WIDTH for _ in range(SCREEN_HEIGHT)]
        
        # draw splash animations (below everything else)
        for bullet, anim_start in self.hits:
            if anim_start + self.splash_animation_duration < current_time:
                self.hits.remove((bullet, anim_start))
            else:
                pygame.draw.circle(self.screen, (233, 233, 216), (bullet.x + bullet.width/2, bullet.y + bullet.height/2), bullet.aoe_range - 50)
        
        for y in range(0, 600, 50):
            for x in range(0, 900, 50):
                sq = pygame.Rect(x, y, 50, 50)
                pygame.draw.rect(self.screen, (200, 200, 180), sq, 1)

        # draw towers, bullets, and turrets
        for tower in self.towers:
            new_hits = tower.update(self.enemies, self.fps) # NOTE: passing self.fps to update is weird and sucks :(
            for hit in new_hits:
                self.hits.append((hit, current_time))

            tower.draw(self.screen)
            tower.turret.draw(self.screen)

            # re-add existing towers to grid
            grid_x = tower.x//50
            grid_y = tower.y//50
            self.grid[grid_y][grid_x] = tower

        # update and draw enemies
        self.enemies.update(self.player, self.towers)
        for enemy in self.enemies:
            enemy.draw(self.screen)  # have to loop to draw hp bars

        # update and draw player
        self.player.update()
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
            
            spawn_location = random.choice([
                (random.randint(-100, 900), -100),
                #(random.randint(-100, 900), 600),
                #(-100, random.randint(-100, 600)),
                #(900, random.randint(-100, 600)),
            ])

            self.enemies.add(Enemy(
                spawn=spawn_location,
                size=(50, 50),
                hp=200,
                attack_dmg=4,
                speed=1,
                target=(450, 300),
            ))

        pygame.draw.rect(self.screen, (200, 200, 200),
                         pygame.Rect(0, SCREEN_HEIGHT, SCREEN_WIDTH, TOOLBAR_HEIGHT))
        self.buttons.draw(self.screen)
        self.fps = 1000 / self.clock.tick(self.framecap)

    def loop(self):
        while not self.game_stopped:
            self.process_events()
            pygame.event.pump()
            pygame.draw.rect(self.screen, (255, 255, 230),
                             pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            self.update()
            pygame.display.flip()


if __name__ == "__main__":
    game = Game(fps=60)
    game.loop()
    pygame.quit()
