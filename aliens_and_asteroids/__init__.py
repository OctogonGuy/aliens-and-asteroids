"""An alien-fighting, asteroid-blasting space game.

@author: Alex Gill
"""

import os
import random
import pygame as pg
from pygame.locals import *
from aliens_and_asteroids import spaceship, obstacle
#from click.decorators import group

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
    spaceship.Laser.images = [load_image('laser.gif')]
    obstacle.AlienA.images = [load_image('alien_a1.gif')]
    obstacle.AlienB.images = [load_image('alien_b1.gif')]
    obstacle.AlienC.images = [load_image('alien_c1.gif')]
    obstacle.AsteroidS.images = [load_image('asteroid_s.gif')]
    obstacle.AsteroidM.images = [load_image('asteroid_m.gif')]
    obstacle.AsteroidL.images = [load_image('asteroid_l.gif')]
    
    # Create the background and tile the background image
    bgtile = load_image('background.gif')
    background = pg.surface.Surface(SCREENRECT.size)
    for x in range(0, SCREENRECT.width, bgtile.get_width()):
        for y in range(0, SCREENRECT.height, bgtile.get_height()):
            background.blit(bgtile, (x, y))
    screen.blit(background, (0, 0))
    
    # Initialize game groups
    aliens = pg.sprite.Group()
    asteroids = pg.sprite.Group()
    lasers = pg.sprite.Group()
    sprites = pg.sprite.RenderUpdates()
    playergroup = pg.sprite.GroupSingle()
    
    # Initialize some starting values
    screen_width, screen_height = SCREENRECT.size
    spaceship.Spaceship.area = screen;
    player = spaceship.Spaceship((screen_width / 2, screen_height / 2), -90.0, sprites, playergroup)
    
    # Run the main loop
    clock = pg.time.Clock()
    next_spawn_time_left = 0
    running = True
    while running and player.alive():
        for event in pg.event.get():
            if event.type == QUIT:
                running = False
            
            # Handle shooting
            if event.type == KEYDOWN and event.key == K_SPACE:
                player.shoot(sprites, lasers)
                
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
            obstacles = (
                #obstacle.AlienA, obstacle.AlienB, obstacle.AlienC,
                obstacle.AsteroidL,
            )
            clazz = random.choice(obstacles)
            if issubclass(clazz, obstacle.AlienC):
                clazz(player, sprites, aliens)
            elif issubclass(clazz, obstacle.Alien):
                clazz(sprites, aliens)
            else:
                clazz(sprites, asteroids)
                
            next_spawn_time_left = SPAWN_RATE
        
        # Update display and advance frame
        sprites.clear(screen, background)
        sprites.update()
        sprites.draw(screen)
        pg.display.update()
        clock.tick(FPS)
        
        # Detect collisions between aliens/asteroids and player
        # If collision is detected, kill player
        pg.sprite.groupcollide(aliens, playergroup, False, True)
        pg.sprite.groupcollide(asteroids, playergroup, False, True)
        
        # Detect collisions between aliens/asteroids and laser
        # If collision is detected, kill obstacle and remove laser
        pg.sprite.groupcollide(aliens, lasers, True, True)
        for asteroid, laser_list in pg.sprite.groupcollide(asteroids, lasers, False, False).items():
            laser = laser_list[0]
            if issubclass(asteroid.__class__, obstacle.AsteroidM) or issubclass(asteroid.__class__, obstacle.AsteroidL):
                asteroid.kill(laser.angle)
            else:
                asteroid.kill()
            laser.kill()
        
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