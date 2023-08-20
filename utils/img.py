import pygame
from PIL import Image

cache = {}

def get_image(imagepath: str, width=100, height=100):
    image_key = f"{imagepath.strip()} width={width} height={height}"
    if image_key not in cache:
        image = Image.open(imagepath).convert("RGBA")
        image = image.resize((width, height), resample=Image.LANCZOS)
        image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
        cache[image_key] = image
    return cache[image_key]