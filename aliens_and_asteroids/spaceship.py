import math
import pygame as pg
from aliens_and_asteroids import geometry

FORWARD_ACCELERATION = 0.08
FORWARD_MAX_SPEED = 4.1
BACKWARD_ACCELERATION = 0.06
BACKWARD_MAX_SPEED = 1.6
ROTATE_SPEED = 0.6
AIR_RESISTANCE = 0.02

class Spaceship(pg.sprite.Sprite):
    """A spaceship that can move and shoot"""
    
    images = []
    
    def __init__(self, pos=(0, 0), direction=0.0, *groups):
        super().__init__(groups)
        self.area = pg.display.get_surface()
        
        self.pos = geometry.Position(pos[0], pos[1])
        self.velocity = geometry.Vector(0, direction)
        
        self.images = [pg.transform.rotate(image, -90.0) for image in self.images]
        self.image = pg.transform.rotate(self.images[0], -self.velocity.direction)
        self.rect = self.image.get_rect(center=self.pos.xy())
        
    def forward(self):
        """Moves the spaceship forward."""
        self.velocity.magnitude = min(self.velocity.magnitude + FORWARD_ACCELERATION, FORWARD_MAX_SPEED)
        
    def backward(self):
        """Moves the spaceship backward."""
        self.velocity.magnitude = max(self.velocity.magnitude - BACKWARD_ACCELERATION, -BACKWARD_MAX_SPEED)
    
    def rotate(self, direction):
        """Rotates the spaceship in the given direction (- for left, + for right)."""
        direction = math.copysign(1, direction)
        # If the spaceship is not moving, do nothing
        if self.velocity.magnitude == 0: return
        
        # Rotate the object to an amount corresponding with its speed
        self.velocity.direction += direction * self.velocity.magnitude * ROTATE_SPEED
        
        # Rotate the image
        self.image = pg.transform.rotate(self.images[0], -self.velocity.direction)
        self.rect = self.image.get_rect(center=self.rect.center)
    
    def update(self):
        """Updates the position of the spaceship."""
        # Decelerate the spaceship due to air resistance
        speed = abs(self.velocity.magnitude) - AIR_RESISTANCE
        if self.velocity.magnitude > 0:
            self.velocity.magnitude = max(speed, 0)
        if self.velocity.magnitude < 0:
            self.velocity.magnitude = min(-speed, 0)
        
        # Update the spaceship's location
        a, b = self.velocity.ab()
        self.pos.x += a
        self.pos.y += b
        # Move the spaceship to the opposite side if out of bounds
        if not self.area.get_rect().collidepoint(self.pos.xy()):
            if self.pos.x > self.area.get_width(): self.pos.x = 0
            elif self.pos.x < 0: self.pos.x = self.area.get_width()
            if self.pos.y > self.area.get_height(): self.pos.y = 0
            elif self.pos.y < 0: self.pos.y = self.area.get_height()
        
        # Position the spaceship's rectangle on the screen
        self.rect.center = self.pos.xy()
