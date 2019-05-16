import numpy as np
import cairo

TAU = 2*np.pi
DEGREES = TAU / 360

HEIGHT = 1080
WIDTH = int(2*HEIGHT / np.sqrt(3))

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

class TriangleFractal:
    def __init__(self):
        self.pattern = {
            # "background" : cairo.SolidPattern(0, 0, 0, 0),
            "background" : cairo.SolidPattern(0.06, 0.06, 0.06),
            "foreground" : cairo.SolidPattern(0.35, 0.77, 0.87)
        }
        self.init_cairo_context()

    def init_cairo_context(self):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
        self.ctx = cairo.Context(self.surface)
        self.ctx.scale(HEIGHT, HEIGHT)  # Normalizing the canvas
        self.ctx.translate(0.5*(WIDTH/HEIGHT), 0.5)
        self.ctx.set_source(self.pattern["background"])
        self.ctx.paint()

    def save_cairo_surface(self, filename):
        self.surface.write_to_png(filename)

    def generate_triangles_in_row(self, triangle, row_index):
        if row_index < 0:
            raise ValueError("row_index cannot be negative.")

        x = triangle.get_centroid().get_x()
        y = triangle.get_centroid().get_y()
        radius = triangle.get_radius()
        radius_component = radius*np.cos(TAU / 12)
        x_left = x - radius_component
        x_right = x + radius_component
        triangles = list()

        if row_index % 2 == 0:
            # draw odd number of triangles
            triangles.append(triangle)
            for i in range(1, int(row_index / 2) + 1):
                dx = i * 2 * radius_component
                triangles.append(Triangle(Point(x - dx, y), radius))
                triangles.append(Triangle(Point(x + dx, y), radius))
        else:
            # draw even number of triangles
            for i in range(1, int((row_index + 1) / 2) + 1):
                dx = i * 2 * radius_component
                triangles.append(Triangle(Point(x_right - dx, y), radius))
                triangles.append(Triangle(Point(x_left + dx, y), radius))

        return triangles

    def generate_triangles(self, triangle, layers):
        x = triangle.get_top_vertex().get_x()
        y = triangle.get_top_vertex().get_y()
        height = triangle.get_height()
        next_radius = triangle.get_radius() / layers
        step = next_radius*(np.sin(TAU / 12) + 1)
        triangles = list()

        row_index = 0
        for r_y in np.arange(next_radius, height, step):
            triangles.extend(self.generate_triangles_in_row(
                Triangle(Point(x, y + r_y), next_radius),
                row_index
            ))
            row_index += 1

        for t in triangles:
            if not t.draw(self.ctx, self.pattern, 1 / HEIGHT):
                self.generate_triangles(t, layers)


def main():
    sierpinski = TriangleFractal()
    main_triangle = Triangle(Point(0, 1/6), 2/3)
    sierpinski.generate_triangles(main_triangle, 3)

    sierpinski.save_cairo_surface("3_layers.png")

if __name__ == '__main__':
    main()
