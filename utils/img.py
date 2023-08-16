import os
import pygame

cache = {}

# rotation ?
# `rot` param
def get_image(imagepath: str, width=100, height=100):
    image_key = f"{imagepath.strip()} width={width} height={height}"
    if image_key in cache:
        # logs.log(f"using cached '{imagepath}' (width={width} height={height})")
        pass
    else:
        # logs.log(f"loading '{imagepath}' (width={width} height={height})")
        image = pygame.image.load(imagepath).convert_alpha()
        image = pygame.transform.scale(image, (width, height))
        cache[image_key] = image
    return cache[image_key]
