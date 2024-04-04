"""An alien-fighting, asteroid-blasting space game.

@author: Alex Gill
"""

import os
import random
import pygame as pg
from pygame.locals import *
from aliens_and_asteroids import spaceship, alien

SCREENRECT = pg.Rect(0, 0, 640, 480)
FPS = 60
SPAWN_RATE = 2 #s

def main():
    # Initialize pygame
    pg.init()
    pg.mixer.init()
    
    # Set up the game window
    screen = pg.display.set_mode(SCREENRECT.size)
    pg.display.set_caption('Aliens and Asteroids')
    
    # Load images and assign them to sprite classes
    spaceship.Spaceship.images = [load_image('spaceship.gif')]
    alien.AlienA.images = [load_image('alien_a1.gif')]
    alien.AlienB.images = [load_image('alien_b1.gif')]
    alien.AlienC.images = [load_image('alien_c1.gif')]
    
    # Create the background and tile the background image
    bgtile = load_image('background.gif')
    background = pg.surface.Surface(SCREENRECT.size)
    for x in range(0, SCREENRECT.width, bgtile.get_width()):
        for y in range(0, SCREENRECT.height, bgtile.get_height()):
            background.blit(bgtile, (x, y))
    screen.blit(background, (0, 0))
    
    # Initialize game groups
    sprites = pg.sprite.RenderUpdates()
    
    # Initialize some starting values
    screen_width, screen_height = SCREENRECT.size
    spaceship.Spaceship.area = screen;
    player = spaceship.Spaceship((screen_width / 2, screen_height / 2), -90.0, sprites)
    
    # Run the main loop
    clock = pg.time.Clock()
    next_spawn_time_left = 0
    running = True
    while running:
        for event in pg.event.get():
            if event.type == QUIT:
                running = False
                
        # Handle player movement
        keystate = pg.key.get_pressed()
        move_direction = keystate[K_UP] - keystate[K_DOWN]
        if move_direction > 0:
            player.forward()
        elif move_direction < 0:
            player.backward()
        direction = keystate[K_RIGHT] - keystate[K_LEFT]
        if direction != 0:
            player.rotate(direction)
            
        # If spawn timer is up, spawn next enemy/obstacle
        if next_spawn_time_left <= 0:
            obstacles = (alien.AlienA, alien.AlienB, alien.AlienC)
            random.choice(obstacles)(player, sprites)
            next_spawn_time_left = SPAWN_RATE
        
        # Update display and advance frame
        sprites.clear(screen, background)
        sprites.update()
        sprites.draw(screen)
        pg.display.update()
        clock.tick(FPS)
        
        # Count down the spawn timer
        next_spawn_time_left -= 1 / FPS
        
    # Quit pygame
    pg.mixer.quit()
    pg.quit()

def load_image(filename):
    """Loads an image."""
    main_dir = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
    file = os.path.join(main_dir, 'data', filename)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit(f'Could not load image "{file}" {pg.get_error()}')
    return surface.convert()

if __name__ == '__main__':
    main()