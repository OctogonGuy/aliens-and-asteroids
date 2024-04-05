import math
import random
import pygame as pg
from aliens_and_asteroids import geometry

SPEED_RANGE = 1
S_SPEED = 2.5
M_SPEED = 2
L_SPEED = 1.5
MAX_ROTATE_AMT = 7.5

class Asteroid(pg.sprite.Sprite):
    """Abstract class for an obstacle that moves along a straight line and rotates"""
    
    images = []

    def __init__(self, *groups):
        super().__init__(groups)
        self.area = pg.display.get_surface()
        
        pos_x = self.images[0].get_rect().width / 2
        pos_y = self.images[0].get_rect().height / 2
        self.pos = geometry.Position(pos_x, pos_y)
        self.angle = random.uniform(0, 2*math.pi)
        self.rotation_amt = random.uniform(-MAX_ROTATE_AMT, MAX_ROTATE_AMT)
        self.rotation = -90
        
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=self.pos.xy())
    
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
        self.speed = random.uniform(S_SPEED - SPEED_RANGE, S_SPEED + SPEED_RANGE)
    
class AsteroidM(Asteroid):
    """A medium asteroid that splits into 3 small asteroids when shot"""
    
    def __init__(self, *groups):
        super().__init__(groups)
        self.speed = random.uniform(M_SPEED - SPEED_RANGE, M_SPEED + SPEED_RANGE)

class AsteroidL(Asteroid):
    """A large asteroid that splits into 3 medium asteroids when shot"""
    
    def __init__(self, *groups):
        super().__init__(groups)
        self.speed = random.uniform(L_SPEED - SPEED_RANGE, M_SPEED + SPEED_RANGE)