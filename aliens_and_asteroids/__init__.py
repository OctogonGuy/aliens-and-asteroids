"""An alien-fighting, asteroid-blasting space game.

@author: Alex Gill
"""

import os
import pygame as pg
from pygame.locals import *
from aliens_and_asteroids import spaceship

SCREENRECT = pg.Rect(0, 0, 640, 480)
FPS = 60

main_dir = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]

def main():
    # Initialize pygame
    pg.init()
    pg.mixer.init()
    
    # Set up the game window
    screen = pg.display.set_mode(SCREENRECT.size)
    pg.display.set_caption('Aliens and Asteroids')
    
    # Load images and assign them to sprite classes
    spaceship.Spaceship.images = [load_image('spaceship.gif')]
    
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
    running = True
    while running:
        for event in pg.event.get():
            if event.type == QUIT:
                running = False
                
        keystate = pg.key.get_pressed()
        
        move_direction = keystate[K_UP] - keystate[K_DOWN]
        if move_direction > 0:
            player.forward()
        elif move_direction < 0:
            player.backward()
        
        direction = keystate[K_RIGHT] - keystate[K_LEFT]
        if direction != 0:
            player.rotate(direction)
        
        sprites.clear(screen, background)
        sprites.update()
        sprites.draw(screen)
        
        pg.display.update()
        clock.tick(FPS)
        
    # Quit pygame
    pg.mixer.quit()
    pg.quit()

def load_image(filename):
    """Loads an image."""
    file = os.path.join(main_dir, 'data', filename)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit(f'Could not load image "{file}" {pg.get_error()}')
    return surface.convert()

if __name__ == '__main__':
    main()