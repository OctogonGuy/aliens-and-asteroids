"""Contains classes for alien and asteroid objects in the game"""

import math
import random
import pygame as pg
from aliens_and_asteroids import geometry

# Alien constants
ALIEN_A_SPEED = 4.2
ALIEN_B_SPEED = 3.0
ALIEN_C_SPEED = 2.6
ALIEN_A_DESCEND_DISTANCE = 50
ALIEN_B_MIN_MOVE_DISTANCE = 40
ALIEN_B_MAX_MOVE_DISTANCE = 240

# Asteroid constants
ASTEROID_SPEED_RANGE = 1
ASTEROID_S_SPEED = 2.5
ASTEROID_M_SPEED = 2
ASTEROID_L_SPEED = 1.5
ASTEROID_MAX_ROTATE_ANGLE = 7.5

class Obstacle(pg.sprite.Sprite):
    """Abstract class for any obstacle"""
    
    images = []
    
    def __init__(self, *groups):
        super().__init__(groups)
        self.area = pg.display.get_surface()
        
        pos_x = self.images[0].get_rect().width / 2
        pos_y = self.images[0].get_rect().height / 2
        self.pos = geometry.Position(pos_x, pos_y)
        
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=self.pos.xy())
        

class Alien(Obstacle):
    """Abstract class for an enemy that moves around the screen"""

    def __init__(self, *groups):
        super().__init__(groups)
    
    def update(self):
        """Updates the position of the alien on the screen."""
        # Move according to subclass pattern
        self.move()
        # Move the alien to the opposite side if out of bounds
        if not self.area.get_rect().collidepoint(self.pos.xy()):
            if self.pos.x > self.area.get_width(): self.pos.x = 0
            elif self.pos.x < 0: self.pos.x = self.area.get_width()
            if self.pos.y > self.area.get_height(): self.pos.y = 0
            elif self.pos.y < 0: self.pos.y = self.area.get_height()
        # Position the alien's rectangle on the screen
        self.rect.center = self.pos.xy()
        
    def move(self):
        pass
    
class AlienA(Alien):
    """An alien that moves like an alien from Space Invaders"""
    
    to_end = True # Whether to move toward the end of the line
    to_descend = 0 # Distance to move to reach next line
    
    def __init__(self, *groups):
        super().__init__(groups)
        self.speed = ALIEN_A_SPEED
        
    def move(self):
        # If alien has to descend, descend
        if self.to_descend > 0:
            self.to_descend -= self.speed
            if self.to_descend < 0:
                displacement = abs(self.to_descend)
                self.to_descend = 0
            else:
                displacement = self.speed
            self.pos.y += displacement
        # If alien is moving to end, move toward end
        else:
            reached_end = False
            if self.to_end:
                self.pos.x += self.speed
                # If reached end, do not go past end
                if self.pos.x > self.area.get_width() - self.rect.width:
                    self.pos.x = self.area.get_width() - self.rect.width
                    reached_end = True
            else:
                self.pos.x -= self.speed
                # If reached start, do not go past start
                if self.pos.x < self.rect.width:
                    self.pos.x = self.rect.width
                    reached_end = True
            if reached_end:
                self.to_descend = ALIEN_A_DESCEND_DISTANCE
                self.to_end = not self.to_end
    
class AlienB(Alien):
    """An alien that moves with a random walk"""
    
    direction = None
    distance = 0
    
    def __init__(self, *groups):
        super().__init__(groups)
        self.speed = ALIEN_B_SPEED
    
    def move(self):
        # Select a target if no target exists
        if self.distance == 0:
            self.new_target()
        
        # Move toward target
        self.distance -= self.speed
        if self.distance < 0:
            displacement = abs(self.distance)
            self.distance = 0
        else:
            displacement = self.speed
        if self.direction == geometry.Direction.LEFT:
            self.pos.x -= displacement
            angle = 180
        elif self.direction == geometry.Direction.RIGHT:
            self.pos.x += displacement
            angle = 0
        elif self.direction == geometry.Direction.UP:
            self.pos.y -= displacement
            angle = 90
        else: # self.direction == geometry.Direction.DOWN:
            self.pos.y += displacement
            angle = 360
        
        # Rotate image in the direction of movement
        self.image = pg.transform.rotate(self.images[0], -angle - 90)
        self.rect = self.image.get_rect(center=self.rect.center)
    
    def new_target(self):
        """Determines a new position to which to move."""
        self.direction = random.choice(list(geometry.Direction))
        self.distance = random.randint(ALIEN_B_MIN_MOVE_DISTANCE, ALIEN_B_MAX_MOVE_DISTANCE)

class AlienC(Alien):
    """An alien that moves like a homing missile toward the player"""
    
    def __init__(self, player, *groups):
        super().__init__(groups)
        self.speed = ALIEN_C_SPEED
        self.player = player
    
    def move(self):
        # Calculate the horizontal and vertical distance between alien and player
        delta_x = self.player.pos.x - self.pos.x
        delta_y = self.player.pos.y - self.pos.y
        # If the alien and player on opposite sides of the screen,
        # account for moving to opposite side when calculating distance
        if delta_x > self.area.get_width() / 2:
            delta_x = -((self.area.get_width() - self.player.pos.x) + self.pos.x)
        elif delta_x < -(self.area.get_width() / 2):
            delta_x = self.player.pos.x + (self.area.get_width() - self.pos.x)
        if delta_y > self.area.get_height() / 2:
            delta_y = -((self.area.get_height() - self.player.pos.y) + self.pos.y)
        elif delta_y < -(self.area.get_height() / 2):
            delta_y = self.player.pos.y + (self.area.get_height() - self.pos.y)
        
        # Calculate the angle between alien and player
        if delta_x > 0:
            angle = math.atan(delta_y / delta_x)
        elif delta_x < 0:
            angle = math.atan(delta_y / delta_x) + math.pi
        elif delta_y > 0:
            angle = math.pi / 2
        else:
            angle = -math.pi / 2
        
        # Update alien's location
        self.pos.x += math.cos(angle) * self.speed
        self.pos.y += math.sin(angle) * self.speed
        
        # Rotate image in the direction of movement
        self.image = pg.transform.rotate(self.images[0], -math.degrees(angle) - 90)
        self.rect = self.image.get_rect(center=self.rect.center)
        

class Asteroid(Obstacle):
    """Abstract class for an obstacle that moves along a straight line and rotates"""

    def __init__(self, *groups):
        super().__init__(groups)
        self.angle = random.uniform(0, 2*math.pi)
        self.rotation_amt = random.uniform(-ASTEROID_MAX_ROTATE_ANGLE, ASTEROID_MAX_ROTATE_ANGLE)
        self.rotation = -90
    
    def update(self):
        """Updates the position and rotation of the asteroid on the screen."""
        # Move
        self.pos.x += math.cos(self.angle) * self.speed
        self.pos.y += math.sin(self.angle) * self.speed
        
        # Move the asteroid to the opposite side if out of bounds
        if not self.area.get_rect().collidepoint(self.pos.xy()):
            if self.pos.x > self.area.get_width(): self.pos.x = 0
            elif self.pos.x < 0: self.pos.x = self.area.get_width()
            if self.pos.y > self.area.get_height(): self.pos.y = 0
            elif self.pos.y < 0: self.pos.y = self.area.get_height()
        
        # Rotate
        self.rotation += self.rotation_amt
        self.image = pg.transform.rotate(self.images[0], self.rotation)
        
        # Position the asteroid's rectangle on the screen
        self.rect = self.image.get_rect(center=self.pos.xy())
    
class AsteroidS(Asteroid):
    """A small asteroid"""
    
    def __init__(self, *groups):
        super().__init__(groups)
        self.speed = random.uniform(ASTEROID_S_SPEED - ASTEROID_SPEED_RANGE, ASTEROID_S_SPEED + ASTEROID_SPEED_RANGE)
    
class AsteroidM(Asteroid):
    """A medium asteroid that splits into 3 small asteroids when shot"""
    
    def __init__(self, *groups):
        super().__init__(groups)
        self.speed = random.uniform(ASTEROID_M_SPEED - ASTEROID_SPEED_RANGE, ASTEROID_M_SPEED + ASTEROID_SPEED_RANGE)

class AsteroidL(Asteroid):
    """A large asteroid that splits into 3 medium asteroids when shot"""
    
    def __init__(self, *groups):
        super().__init__(groups)
        self.speed = random.uniform(ASTEROID_L_SPEED - ASTEROID_SPEED_RANGE, ASTEROID_M_SPEED + ASTEROID_SPEED_RANGE)