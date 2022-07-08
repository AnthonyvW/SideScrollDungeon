import pygame
from PIL import Image

def aspect_scale(img,bx,by, smooth = False):
    #Source http://www.pygame.org/pcr/transform_scale/
    """ Scales 'img' to fit into box bx/by.
     This method will retain the original image's aspect ratio """
    ix,iy = img.get_size()
    if ix > iy:
        # fit to width
        scale_factor = bx/float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        # fit to height
        scale_factor = by/float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx/float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by
    if smooth:
        return pygame.transform.smoothscale(img, (int(sx), int(sy)))
    return pygame.transform.scale(img, (int(sx),int(sy)))

def process_World(Surface, World, Color_Key):
    # Process Colors
    for x in range(World.width):
        for y in range(World.height):
            Surface.set_at((x, y), Color_Key[World.worldData[x][y]])

    # Flip to orientate with screen
    return pygame.transform.flip(Surface, False, True)

def export_Image(sprite, filename):
    """Processes 2D array to RGB data."""
    global world_Width, world_Height
    print("Exporting Image")
    colors = []
    # Goes through 2D array and process it into RGB values.
    for Y in range(sprite.get_size()[1]):
        for X in range(sprite.get_size()[0]):
            color = sprite.get_at((X, Y))
            colors.extend([color[0], color[1], color[2]])
    # Converting RGB list into something pillow can use to save an image.
    colors = bytes(colors)
    img = Image.frombytes('RGB', (sprite.get_size()[0], sprite.get_size()[1]), colors)
    img.save(f'{filename}.png')
    # Letting user know the image is saved.
    print(f'{filename}.png Saved')