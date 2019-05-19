import numpy as np
from constants import *

class Point():
    '''Creates a point on a coordinate plane with values x and y.'''
    def __init__(self, x, y):
        '''Defines x and y variables'''
        self.x = x
        self.y = y

    def __eq__(self, other):
        '''Overrides the default implementation'''
        if isinstance(other, Point):
            a1 = np.array([self.x, self.y])
            a2 = np.array([other.x, other.y])
            result = np.isclose(a1, a2)
            return result[0] and result[1]
        return False


    def move(self, dx=0, dy=0):
        '''Determines where x and y move'''
        self.x += dx
        self.y += dy

    def __str__(self):
        return "Point(%s,%s)"%(self.x, self.y)

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def distance(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return np.hypot(dx, dy)


class Triangle:
    def __init__(self, centroid, radius):
        self.centroid = centroid
        self.radius = radius

    def __str__(self):
        return "Centroid : %s, Radius : %f"%(self.centroid, self.radius)

    def __eq__(self, other):
        if isinstance(other, Triangle):
            centroids_equal = self.centroid == other.centroid
            radii_equal = np.isclose(np.array([self.radius]), np.array([other.radius]))[0]
            return centroids_equal and radii_equal
        return False

    def get_radius(self):
        return self.radius

    def get_centroid(self):
        return self.centroid

    def get_height(self):
        return self.radius*(1 + np.sin(TAU/12))

    def get_top_vertex(self):
        return Point(
            self.centroid.get_x(),
            self.centroid.get_y() - self.radius
        )

    def update_position(self, distance):
        self.centroid.move(dy=distance)
        self.radius += distance

    def draw(self, ctx, pattern, max_radius):
        if self.radius <= max_radius:
            ctx.set_source(pattern["foreground"])

            moved = False
            for theta in np.arange(0, TAU, 120*DEGREES):
                point = Point(
                    self.radius * np.cos(theta - TAU/4) + self.centroid.get_x(),
                    self.radius * np.sin(theta - TAU/4) + self.centroid.get_y()
                )
                if not moved:
                    ctx.move_to(point.get_x(), point.get_y())
                    moved = True
                else:
                    ctx.line_to(point.get_x(), point.get_y())

            ctx.close_path()
            ctx.fill()

            return True
        return False
