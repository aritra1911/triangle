import numpy as np
import cairo
import time
import config
from movie_writer import MovieWriter
from constants import *
from utils import *

class TriangleFractal:
    def __init__(self, pw, ph):
        self.pattern = {
            # "background" : cairo.SolidPattern(0, 0, 0, 0),
            "background" : cairo.SolidPattern(0, 0, 0),
            "foreground" : cairo.SolidPattern(0.35, 0.77, 0.87)
        }
        self.pixel_width = pw
        self.pixel_height = ph
        self.pixel_array_dtype = 'uint8'
        self.n_channels = 4
        self.init_cairo_context()

    def init_cairo_context(self):
        # Initialize pixel_array
        self.pixel_array = np.zeros(
            (self.pixel_width, self.pixel_height, self.n_channels),
            dtype=self.pixel_array_dtype
        )

        # Initialize cairo surface and context
        self.surface = cairo.ImageSurface.create_for_data(
            self.pixel_array,
            cairo.FORMAT_ARGB32,
            self.pixel_width, self.pixel_height
        )
        self.ctx = cairo.Context(self.surface)

        # Normalizing the canvas
        self.ctx.scale(self.pixel_height, self.pixel_height)
        aspect_ratio = self.pixel_width / self.pixel_height
        self.ctx.translate(0.5*aspect_ratio, 0.5)

        self.paint_it_black()

    def paint_it_black(self):
        self.ctx.set_source(self.pattern["background"])
        self.ctx.paint()

    def save_cairo_surface(self, filename):
        self.surface.write_to_png(filename)

    def get_frame(self):
        return self.pixel_array

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
        if not isinstance(layers, int):
            raise TypeError("Layers must be of integer type")

        if layers < 2:
            raise ValueError(
                "Recursion of less than 2 layered triangles is not possible"
            )

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
            if not t.draw(self.ctx, self.pattern, 1 / self.pixel_height):
                self.generate_triangles(t, layers)


class TriangleAnimationWriter:
    def __init__(self, fw, fh, fps, layers):
        self.frame_width = fw
        self.frame_height = fh
        self.frame_rate = fps
        self.layers = layers
        self.writer = MovieWriter(fw, fh, fps)
        self.fractal = TriangleFractal(fw, fh)
        self.triangle = Triangle(
            Point(0, CENTROID_Y),
            RADIUS
        )

    def write_animation(self, run_time):
        print("Initializing animation write...", end='\r')
        frames = run_time * self.frame_rate
        factor = self.triangle.get_scale_factor(frames, self.layers)
        start_time = time.time()
        self.writer.open_movie_pipe()

        for frame in range(frames):
            print(" " * 80, end='\r')
            percentage = (frame / frames) * 100
            print(f"{percentage} %", end='\r')
            self.fractal.generate_triangles(self.triangle, self.layers)
            self.writer.write_frame(self.fractal.get_frame())
            self.triangle.update_position(factor)
            self.fractal.paint_it_black()

        self.writer.close_movie_pipe()
        end_time = time.time()

        total_time = end_time - start_time
        if total_time > 0:
            display_time = total_time
            unit = 's'
        else:
            display_time = total_time * 1000
            unit = 'ms'

        print(f"Finished animating in {display_time} {unit}")


def main():
    args = config.parse_cli()
    render_config = config.get_configuration(args)
    layers = render_config["layers"]

    triangle_animation = TriangleAnimationWriter(
        DEFAULT_PIXEL_WIDTH,
        DEFAULT_PIXEL_HEIGHT,
        DEFAULT_FRAME_RATE,
        layers
    )

    triangle = TriangleFractal(
        DEFAULT_PIXEL_WIDTH,
        DEFAULT_PIXEL_HEIGHT
    )

    if render_config["animate"]:
        triangle_animation.write_animation(2)
    else:
        triangle.generate_triangles(
            Triangle(Point(0, 1/6), 2/3),
            layers
        )
        triangle.save_cairo_surface(f"{layers}_layers.png")


if __name__ == '__main__':
    main()
