import math
import pygame as pg
from aliens_and_asteroids import geometry

FORWARD_ACCELERATION = 0.09
FORWARD_MAX_SPEED = 4.2
BACKWARD_ACCELERATION = 0.07
BACKWARD_MAX_SPEED = 1.8
ROTATE_SPEED = 0.7
AIR_RESISTANCE = 0.02
LASER_SPEED = 10

class Spaceship(pg.sprite.Sprite):
    """A spaceship that can move and shoot"""
    
    images = []
    
    def __init__(self, pos=(0, 0), direction=0.0, sprite_group=None, *groups):
        super().__init__(sprite_group, groups)
        self.area = pg.display.get_surface()
        
        self.pos = geometry.Position(pos[0], pos[1])
        self.velocity = geometry.Vector(0, direction)
        
        self.images = [pg.transform.rotate(image, -90.0) for image in self.images]
        self.image = pg.transform.rotate(self.images[0], -self.velocity.direction)
        self.rect = self.image.get_rect(center=self.pos.xy())
        
        self.exhaust = Exhaust(self, sprite_group)
        
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
        
    def shoot(self, *groups):
        """Shoots a laser from the front of she spaceship."""
        Laser(self, groups)
    
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
        
        # Update exhaust
        self.exhaust.update()
        
        
class Exhaust(pg.sprite.Sprite):
    """Sprite for the exhaust that comes out of the rocket"""
    
    images = []
    
    def __init__(self, spaceship, groups):
        super().__init__(groups)
        self.spaceship = spaceship
        self.image_index = 0
        self.images = [pg.transform.rotate(image, -90.0) for image in self.images]
        self.pos = geometry.Position(0, 0)
        self.update()
        
    def update(self):
        """Moves the exhaust with the spaceship"""
        
        # Change size depending on the velocity
        self.image = self.images[self.image_index]
        scale = max(self.spaceship.velocity.magnitude / FORWARD_MAX_SPEED, 0)
        self.image = pg.transform.scale_by(self.image, scale)
        
        # Change position
        angle = math.radians(self.spaceship.velocity.direction)
        self.pos.x = self.spaceship.pos.x - math.cos(angle) * \
                (Spaceship.images[0].get_height() / 2 +  self.image.get_width() / 2 + 1)
        self.pos.y = self.spaceship.pos.y - math.sin(angle) * \
                (Spaceship.images[0].get_height() / 2 +  self.image.get_width() / 2 + 1)
        
        # Change angle
        self.image = pg.transform.rotate(self.image, -self.spaceship.velocity.direction)
        
        # Position the exhaust's rectangle on the screen
        self.rect = self.image.get_rect(center=self.pos.xy())


class Laser(pg.sprite.Sprite):
    """Represents a projectile that can be fired at obstacles"""
    
    images = []
    
    def __init__(self, spaceship, *groups):
        super().__init__(groups)
        self.area = pg.display.get_surface()
        
        self.angle = math.radians(spaceship.velocity.direction)
        self.pos = geometry.Position(spaceship.pos.x, spaceship.pos.y)
        self.pos.x += math.cos(self.angle) * (spaceship.image.get_height() / 2)
        self.pos.y += math.sin(self.angle) * (spaceship.image.get_height() / 2)
        
        self.images = [pg.transform.rotate(image, -90.0) for image in self.images]
        self.image = pg.transform.rotate(self.images[0], -spaceship.velocity.direction)
        self.rect = self.image.get_rect(center=self.pos.xy())
        
    def update(self):
        """Moves the laser forward."""
        self.pos.x += math.cos(self.angle) * LASER_SPEED
        self.pos.y += math.sin(self.angle) * LASER_SPEED
        
        # Position the laser's rectangle on the screen
        self.rect.center = self.pos.xy()