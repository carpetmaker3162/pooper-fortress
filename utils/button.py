from utils.img import get_image
import pygame


class Button(pygame.sprite.Sprite):
    def __init__(self,
                 image="assets/none.png",
                 x=0,
                 y=0,
                 width=100,
                 height=100,
                 id=""):

        super().__init__()

        self.image = get_image(image, width, height)
        self.rect = self.image.get_rect()
        self.rect.center = (x + width/2, y + height/2)

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.id = id

    def is_hovering(self, mousex, mousey):
        if (self.x < mousex < self.x + self.width and
                self.y < mousey < self.y + self.height):
            return True
        else:
            return False
