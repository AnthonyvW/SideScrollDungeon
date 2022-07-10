
import random
import pygame
import ImageHandler
from Classes import Dungeon, World

pygame.init() # Initialize Pygame Modules

# Game Window
screen_Height = 1024
screen_Width = 1024+ 128
screen = pygame.display.set_mode((screen_Width, screen_Height))
# Set Window Name
pygame.display.set_caption('Pygame Boiler Plate')
# Set Game Clock
FPS = 6
clock = pygame.time.Clock()

'''WORLD PROPERTIES'''
world_Width = 512 + 128
world_Height = 512
Seed = int(random.random() * 100000)
#24159, Seed for bridges over tower
#78832, 22071 Seed for 3 towers
# Problem Seeds 0, 419, 15133
print(Seed)
random.seed(Seed)


'''OUTPUT IMAGE PROPERTIES'''
# Result will be what the final result is outputted to
Result = pygame.Surface((world_Width, world_Height))
# Set BG to white
Result.fill((255,255,255))
# Create Tile ID to Color Num Dict
Color_Key = {
    0 : (78, 207, 255), # Light Blue | Sky
    1 : (128, 128, 128), # Gray | Ground
    2 : (255, 0, 0), # Red | Tower
    3 : (0, 0, 255), # Blue | Tower Foundations
    4 : (255, 128, 0), # Orange | Arches
    5 : (0, 255, 128), # Teal | Walkway
    6 : (200, 0, 0), # Dark Red | Pillar Tops
    7 : (100, 0, 0), # Even Darker Red | Pillar Bottom
}


'''WORLD GENERATION BEGIN'''
# Create empty world
world = World(world_Width, world_Height, Seed)
# Give it Land
world.GenerateTerrain()
world.CreateDungeon(31,60,50 + 64,30)

'''PROCESS WORLD OUTPUT'''
Result = ImageHandler.process_World(Result, world, Color_Key)


print("Finished Generation")
run = True
key_press = False
while run:
    #Ensures the game runs no faster than FPS
    clock.tick(FPS)

    for event in pygame.event.get(): # Keypresses
        if event.type == pygame.QUIT: # If the exit button is pressed this will cause the game to quit
            run = False
        if event.type == pygame.KEYDOWN: # If a key is pressed down do stuff.
            if event.key == pygame.K_n and not key_press:
                key_press = True
            if event.key == pygame.K_e and not key_press:
                key_press = True
                ImageHandler.export_Image(Result, Seed)
        if event.type == pygame.KEYUP: # If a key is released do stuff.
            if event.key == pygame.K_n and key_press:
                key_press = False
            if event.key == pygame.K_e and key_press:
                key_press = False


    Output = ImageHandler.aspect_scale(Result, screen_Width, screen_Height)
    screen.blit(Output, (0,0))

    pygame.display.update() # Updates Screen

pygame.quit()