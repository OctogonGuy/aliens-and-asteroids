import math
import pygame as pg

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
        
        self.pos = Position(pos[0], pos[1])
        self.velocity = Vector(0, direction)
        
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
        # If spaceship is going backwards, reverse the direction
        elif self.velocity.magnitude < 0: direction = -direction
        
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
        if self.area.get_rect().collidepoint(self.pos.xy()):
            self.rect.center = self.pos.xy()
        # Move the spaceship to the opposite side if out of bounds
        else:
            if self.pos.x > self.area.get_width(): self.pos.x = 0
            elif self.pos.x < 0: self.pos.x = self.area.get_width()
            if self.pos.y > self.area.get_height(): self.pos.y = 0
            elif self.pos.y < 0: self.pos.y = self.area.get_height()
        
class Vector():
    """A quantity that has a magnitude and direction"""
    
    def __init__(self, magnitude, direction):
        """Initializes a vector with a magnitude and position."""
        self.magnitude = magnitude
        self.direction = direction
        
    def ab(self, value=None):
        """Alters the terminal position if a parameter is passed.
        Otherwise, returns the terminal position"""
        if value is None:
            a = math.cos(math.radians(self.direction)) * self.magnitude
            b = math.sin(math.radians(self.direction)) * self.magnitude
            return a, b
        else:
            self.magnitude = math.sqrt(self.a**2 + self.b**2)
            self.direction = math.degrees(math.atan(self.b / self.a))
            
class Position():
    """An ordinal pair that represents the location of an object in space"""
    
    def __init__(self, x, y):
        """Initializes a position with an x- and y-coordinate."""
        self.x = x
        self.y = y
        
    def xy(self):
        """Returns the x- and y-coordinates as a tuple."""
        return self.x, self.y