"""Quantities represented by classes that define geometric properties"""

import math
from enum import Enum

# Directions
class Direction(Enum):
    RIGHT = 1
    UP = 2
    LEFT = 3
    DOWN = 4
    
    def opposite(self):
        """Returns the opposite direction."""
        lookup = {
            Direction.RIGHT: Direction.LEFT,
            Direction.LEFT: Direction.RIGHT,
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            }
        return lookup[self]
    
    def angle(self):
        """Returns the opposite direction."""
        lookup = {
            Direction.RIGHT: 0,
            Direction.UP: 90,
            Direction.LEFT: 180,
            Direction.DOWN: 270,
            }
        return lookup[self]
        
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