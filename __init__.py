"""An alien-fighting, asteroid-blasting space game.

@author: Alex Gill
"""

import os
import random
import pygame as pg
from pygame.locals import *
import spaceship
import obstacle
#from click.decorators import group

ICON = 'alien_a1.gif'
SCREENRECT = pg.Rect(0, 0, 640, 480)
SCREEN_WIDTH, SCREEN_HEIGHT = SCREENRECT.size
FPS = 60
SPAWN_RATE = 3 #s
AMMO_CAP = 2
RELOAD_RATE = 1 #s
OBSTACLE_ANIMATION_RATE = 0.5 #s
EXHAUST_ANIMATION_RATE = 0.1 #s
OBSTACLE_CHOICE_WEIGHTS = { # Weighted likelihood of obstacles being chosen
    obstacle.AlienA: 3,
    obstacle.AlienB: 2,
    obstacle.AlienC: 1,
    obstacle.AsteroidS: 3,
    obstacle.AsteroidM: 2,
    obstacle.AsteroidL: 1,
    }
GAME_OVER_SCREEN_COLOR = '#26144d'
TEXT_COLOR = 'white'
GAME_OVER_TEXT = 'GAME OVER'
GAME_OVER_IMAGE = 'spaceship.gif'
PLAY_AGAIN_PROMPT_TEXT = 'Press SPACE to play again.'
SCORE_TEXT = 'Your score is {}'

def new_game():
    """Starts a new game."""
    global aliens, asteroids, lasers, sprites, playergroup, player, \
        ammo, spawn_time_left, reload_time_left, reloading, score
    
    # Initialize score
    score = 0
    
    # Initialize other variables
    spawn_time_left = 0
    reload_time_left = 0
    reloading = False
    
    # Initialize game groups
    aliens = pg.sprite.Group()
    asteroids = pg.sprite.Group()
    lasers = pg.sprite.Group()
    sprites = pg.sprite.RenderUpdates()
    playergroup = pg.sprite.GroupSingle()
    
    # Create player
    player = spaceship.Spaceship((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), -90.0, sprites, playergroup)
    ammo = AMMO_CAP
    
    # Show background
    screen.blit(background, (0, 0))
    

def main():
    global screen, background, ammo, spawn_time_left, reload_time_left, reloading, score
    # Initialize pygame
    pg.init()
    pg.mixer.init()
    
    # Set up the game window
    screen = pg.display.set_mode(SCREENRECT.size)
    pg.display.set_caption('Aliens and Asteroids')
    pg.display.set_icon(load_image(ICON))
    
    # Load images and assign them to sprite classes
    spaceship.Spaceship.images = [load_image('spaceship.gif')]
    spaceship.Exhaust.images = [load_image('exhaust1.gif'), load_image('exhaust2.gif')]
    spaceship.Laser.images = [load_image('laser.gif')]
    obstacle.AlienA.images = [load_image('alien_a1.gif'), load_image('alien_a2.gif')]
    obstacle.AlienB.images = [load_image('alien_b1.gif'), load_image('alien_b2.gif')]
    obstacle.AlienC.images = [load_image('alien_c1.gif'), load_image('alien_c2.gif')]
    obstacle.AsteroidS.images = [load_image('asteroid_s.gif')]
    obstacle.AsteroidM.images = [load_image('asteroid_m.gif')]
    obstacle.AsteroidL.images = [load_image('asteroid_l.gif')]
    
    # Load sounds
    laser_sound = load_sound('laser.wav')
    alien_kill_sound = load_sound('alien_kill.wav')
    asteroid_kill_sound = load_sound('asteroid_kill.wav')
    spaceship_kill_sound = load_sound('spaceship_kill.wav')
    load_music('maxstack - through space.ogg')
    pg.mixer.music.play(-1)
    
    # Create the background and tile the background image
    bgtile = load_image('background.gif')
    background = pg.surface.Surface(SCREENRECT.size)
    for x in range(0, SCREENRECT.width, bgtile.get_width()):
        for y in range(0, SCREENRECT.height, bgtile.get_height()):
            background.blit(bgtile, (x, y))
    
    # Initialize some starting values
    title_font = load_font('PixelifySans.ttf', 48)
    title_font.bold = True
    subtitle_font = load_font('PixelifySans.ttf', 26)
    score_font = load_font('PixelifySans.ttf', 24)
    gameover_message = title_font.render(GAME_OVER_TEXT, True, TEXT_COLOR)
    gameover_rect = gameover_message.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 5))
    spaceship_image = load_image(GAME_OVER_IMAGE)
    spaceship_image = pg.transform.scale_by(spaceship_image, 3)
    spaceship_rect = spaceship_image.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 9 / 16))
    playagain_message = subtitle_font.render(PLAY_AGAIN_PROMPT_TEXT, True, TEXT_COLOR)
    playagain_rect = playagain_message.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 4 / 5))
    
    # Create a list of obstacle choices with weighted probabilities of being chosen
    obstacle_choices = []
    for obs, weight in OBSTACLE_CHOICE_WEIGHTS.items():
        for _ in range(weight):
            obstacle_choices.append(obs)
    
    # Start first game
    new_game()
    
    # Run the main loop
    clock = pg.time.Clock()
    alien_animation_timer = pg.USEREVENT + 1
    exhaust_animation_timer = pg.USEREVENT + 2
    alien_image_index = 0
    exhaust_image_index = 0
    pg.time.set_timer(alien_animation_timer, int(OBSTACLE_ANIMATION_RATE * 1000))
    pg.time.set_timer(exhaust_animation_timer, int(EXHAUST_ANIMATION_RATE * 1000))
    running = True
    while running:
        # If the player is still alive, run the game
        if player.alive():
            for event in pg.event.get():
                if event.type == QUIT:
                    running = False
                
                # Handle shooting
                if event.type == KEYDOWN and event.key == K_SPACE and ammo > 0:
                    player.shoot(sprites, lasers)
                    laser_sound.play()
                    ammo -= 1
                    if not reloading:
                        reloading = True
                        reload_time_left = RELOAD_RATE
                
                # Handle animation
                if event.type == alien_animation_timer:
                    if alien_image_index == 0: alien_image_index = 1
                    else: alien_image_index = 0
                    for alien in aliens.spritedict:
                        alien.image_index = alien_image_index
                if event.type == exhaust_animation_timer:
                    if exhaust_image_index == 0: exhaust_image_index = 1
                    else: exhaust_image_index = 0
                    player.exhaust.image_index = exhaust_image_index
                    
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
            if spawn_time_left <= 0:
                clazz = random.choice(obstacle_choices)
                if issubclass(clazz, obstacle.AlienC):
                    clazz(player, sprites, aliens)
                elif issubclass(clazz, obstacle.Alien):
                    clazz(sprites, aliens)
                else:
                    clazz(sprites, asteroids)
                    
                spawn_time_left = SPAWN_RATE
            
            # If reload timer is up, reload
            if reloading and reload_time_left <= 0:
                ammo += 1
                if ammo == AMMO_CAP:
                    reloading = False
                
            # Display background
            screen.blit(background, (0, 0))
            
            # Update sprites
            sprites.clear(screen, background)
            sprites.update()
            sprites.draw(screen)
    
            # Display score
            score_message = score_font.render(str(score), True, TEXT_COLOR)
            score_rect = score_message.get_rect(center=(SCREEN_WIDTH / 2, score_message.get_height()))
            screen.blit(score_message, score_rect)
            
            # Detect collisions between aliens/asteroids and player
            # If collision is detected, kill player
            for _ in pg.sprite.groupcollide(aliens, playergroup, False, True):
                spaceship_kill_sound.play()
            for _ in pg.sprite.groupcollide(asteroids, playergroup, False, True):
                spaceship_kill_sound.play()
            
            # Detect collisions between aliens/asteroids and laser
            # If collision is detected, kill obstacle and remove laser
            for alien in pg.sprite.groupcollide(aliens, lasers, True, True):
                alien_kill_sound.play()
                score += alien.points
            for asteroid, laser_list in pg.sprite.groupcollide(asteroids, lasers, False, False).items():
                laser = laser_list[0]
                if issubclass(asteroid.__class__, obstacle.AsteroidM) or issubclass(asteroid.__class__, obstacle.AsteroidL):
                    asteroid.kill(laser.angle)
                else:
                    asteroid.kill()
                laser.kill()
                asteroid_kill_sound.play()
                score += asteroid.points
            
            # Count down the spawn timer
            spawn_time_left -= 1 / FPS
            # Count down the reload timer
            if reloading:
                reload_time_left -= 1 / FPS
            
        # If the player is not alive, display the game over screen
        else:
            score_message = subtitle_font.render(SCORE_TEXT.format(score), True, TEXT_COLOR)
            score_rect = score_message.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 5 / 16))
            
            screen.fill(GAME_OVER_SCREEN_COLOR)
            screen.blit(gameover_message, gameover_rect)
            screen.blit(playagain_message, playagain_rect)
            screen.blit(spaceship_image, spaceship_rect)
            screen.blit(score_message, score_rect)
            
            for event in pg.event.get():
                if event.type == QUIT:
                    running = False
                
                # Handle starting new game
                if event.type == KEYDOWN and event.key == K_SPACE:
                    new_game()
        
        # Update display and advance frame
        pg.display.update()
        clock.tick(FPS)
        
    # Quit pygame
    pg.mixer.quit()
    pg.quit()

def load_image(filename):
    """Loads an image."""
    #main_dir = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
    #file = os.path.join(main_dir, 'data', filename)
    file = 'data/' + filename
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit(f'Could not load image "{file}" {pg.get_error()}')
    return surface.convert()

def load_sound(filename):
    """Loads an audio file."""
    #main_dir = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
    #file = os.path.join(main_dir, 'data', filename)
    file = 'data/' + filename
    return pg.mixer.Sound(file)

def load_music(filename):
    """Loads an audio file."""
    #main_dir = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
    #file = os.path.join(main_dir, 'data', filename)
    file = 'data/' + filename
    pg.mixer.music.load(file)

def load_font(filename, size):
    """Loads a font file."""
    #main_dir = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
    #file = os.path.join(main_dir, 'data', filename)
    file = 'data/' + filename
    return pg.font.Font(file, size)

if __name__ == '__main__':
    main()