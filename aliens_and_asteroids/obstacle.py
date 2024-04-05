"""Contains classes for alien and asteroid objects in the game"""

import math
import random
import pygame as pg
from aliens_and_asteroids.locals import *

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
        
        # Initial position is random position just off screen
        screen_width = self.area.get_width()
        screen_height = self.area.get_height()
        img_half_width = self.images[0].get_width()
        img_half_height = self.images[0].get_height()
        side = random.choice(list(geometry.Direction))
        if side == geometry.Direction.UP:
            pos_x = random.randint(-img_half_width, screen_width + img_half_width)
            pos_y = -img_half_height
        elif side == geometry.Direction.DOWN:
            pos_x = random.randint(-img_half_width, screen_width + img_half_width)
            pos_y = screen_height + img_half_height
        elif side == geometry.Direction.LEFT:
            pos_x = -img_half_height
            pos_y = random.randint(-img_half_height, screen_height + img_half_height)
        else: # side == geometry.Direction.RIGHT
            pos_x = screen_width + img_half_width
            pos_y = random.randint(-img_half_height, screen_height + img_half_height)
        self.pos = geometry.Position(pos_x, pos_y)
        self.offscreen_position = side
        
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=self.pos.xy())
        
    def move_to_opposite_side(self):
        """Moves the obstacle to the opposite side of the screen if out of bounds."""
        # Indicate whether the obstacle has come on screen yet
        if not self.offscreen_position is None and self.area.get_rect().collidepoint(self.pos.xy()):
            self.offscreen_position = None
            
        if self.offscreen_position is None and not self.area.get_rect().collidepoint(self.pos.xy()):
            if self.pos.x > self.area.get_width(): self.pos.x = 0
            elif self.pos.x < 0: self.pos.x = self.area.get_width()
            if self.pos.y > self.area.get_height(): self.pos.y = 0
            elif self.pos.y < 0: self.pos.y = self.area.get_height()
        

class Alien(Obstacle):
    """Abstract class for an enemy that moves around the screen"""

    def __init__(self, *groups):
        super().__init__(groups)
    
    def update(self):
        """Updates the position of the alien on the screen."""
        # Move according to subclass pattern
        self.move()
        # Move the alien to the opposite side if out of bounds
        self.move_to_opposite_side()
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
        
        # Starting position is one of the eight positions adjacent to corners
        screen_width = self.area.get_width()
        screen_height = self.area.get_height()
        img_width = self.images[0].get_width()
        img_height = self.images[0].get_height()
        # x, y, descend direction, end direction
        starting_choices = (
            (-img_width, img_height, RIGHT, DOWN),
            (img_width, -img_height, DOWN, RIGHT),
            (screen_width - img_width, -img_height/2, DOWN, LEFT),
            (screen_width + img_width, img_height, LEFT, DOWN),
            (screen_width + img_width, screen_height - img_height, LEFT, UP),
            (screen_width - img_width, screen_height + img_height/2, UP, LEFT),
            (img_width, screen_height + img_height, UP, RIGHT),
            (-img_width, screen_height - img_height, RIGHT, UP) )
        starting = random.choice(starting_choices)
        self.pos = geometry.Position(starting[0], starting[1])
        self.rect = self.image.get_rect(center=self.pos.xy())
        self.descend_direction = starting[2]
        self.end_direction = starting[3]
        self.to_descend = img_width + img_height
        self.reached_end = False
        
        # Rotate image in the direction of movement
        self.image = pg.transform.rotate(self.images[0], self.descend_direction.angle() + 90)
        self.rect = self.image.get_rect(center=self.rect.center)
        
    def move(self):
        # If alien has to descend, descend
        if self.to_descend > 0:
            self.to_descend -= self.speed
            if self.to_descend < 0:
                displacement = abs(self.to_descend)
                self.to_descend = 0
            else:
                displacement = self.speed
            if self.descend_direction == UP: self.pos.y -= displacement
            elif self.descend_direction == DOWN: self.pos.y += displacement
            elif self.descend_direction == LEFT: self.pos.x -= displacement
            elif self.descend_direction == RIGHT: self.pos.x += displacement
        # If alien is moving to end, move toward end
        else:
            # Determine the correct direction to move
            if self.to_end:
                direction = self.end_direction
            else:
                direction = self.end_direction.opposite()
            # Move toward end
            if direction == UP: self.pos.y -= self.speed
            elif direction == DOWN: self.pos.y += self.speed
            elif direction == LEFT: self.pos.x -= self.speed
            elif direction == RIGHT: self.pos.x += self.speed
            # If reached end, do not go past end
            if self.pos.x > self.area.get_width() - self.rect.width:
                self.pos.x = self.area.get_width() - self.rect.width
                self.reached_end = True
            elif self.pos.x < self.rect.width:
                self.pos.x = self.rect.width
                self.reached_end = True
            elif self.pos.y > self.area.get_height() - self.rect.height:
                self.pos.y = self.area.get_height() - self.rect.height
                self.reached_end = True
            elif self.pos.y < self.rect.height:
                self.pos.y = self.rect.height
                self.reached_end = True
            # If alien reached end, start descent
            if self.reached_end:
                self.to_descend = ALIEN_A_DESCEND_DISTANCE
                self.to_end = not self.to_end
                self.reached_end = False
    
class AlienB(Alien):
    """An alien that moves with a random walk"""
    
    direction = None
    distance = 0
    
    def __init__(self, *groups):
        super().__init__(groups)
        self.speed = ALIEN_B_SPEED
        
        # Set first target to just come on screen
        self.direction = self.offscreen_position.opposite()
        if self.direction == geometry.Direction.LEFT or self.direction == geometry.Direction.RIGHT:
            self.distance = random.randint(self.image.get_width(), self.image.get_width() + ALIEN_B_MAX_MOVE_DISTANCE)
        else:
            self.distance = random.randint(self.image.get_height(), self.image.get_height() + ALIEN_B_MAX_MOVE_DISTANCE)
    
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
        raypoints = []
        if self.offscreen_position == UP:
            raypoints.append(geometry.Position(1, 1))
            raypoints.append(geometry.Position(self.area.get_width() - 1, 1))
        elif self.offscreen_position == RIGHT:
            raypoints.append(geometry.Position(self.area.get_width() - 1, 1))
            raypoints.append(geometry.Position(self.area.get_width() - 1, self.area.get_height() - 1))
        elif self.offscreen_position == DOWN:
            raypoints.append(geometry.Position(self.area.get_width() - 1, self.area.get_height() - 1))
            raypoints.append(geometry.Position(1, self.area.get_height() - 1))
        elif self.offscreen_position == LEFT:
            raypoints.append(geometry.Position(1, self.area.get_height() - 1))
            raypoints.append(geometry.Position(1, 1))
        
        # Calculate the angles between asteroid and points
        rays = []
        for i in range(len(raypoints)):
            delta_x = raypoints[i].x - self.pos.x
            delta_y = raypoints[i].y - self.pos.y
            if delta_x > 0:
                rays.append(math.atan(delta_y / delta_x))
            elif delta_x < 0:
                rays.append(math.atan(delta_y / delta_x) + math.pi)
            elif delta_y > 0:
                rays.append(math.pi / 2)
            else:
                rays.append(-math.pi / 2)
            
        self.angle = random.uniform(rays[0], rays[1])
        self.rotation_amt = random.uniform(-ASTEROID_MAX_ROTATE_ANGLE, ASTEROID_MAX_ROTATE_ANGLE)
        self.rotation = random.randint(0, 360)
    
    def update(self):
        """Updates the position and rotation of the asteroid on the screen."""
        # Move
        self.pos.x += math.cos(self.angle) * self.speed
        self.pos.y += math.sin(self.angle) * self.speed
        
        # Move the asteroid to the opposite side if out of bounds
        self.move_to_opposite_side()
        
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