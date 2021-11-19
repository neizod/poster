#!/usr/bin/env python3

import multiprocessing

from PIL import Image
from matplotlib import cm


# parameters =================================================================

# printing quality
dpi = 300
width_inch = 3 * 12
height_inch = 2 * 12

# file handling
fileformat = 'pdf'  # png, pdf

# computation
number_parallel_processors = 8
number_progress_ticks = 100

# mandelbrot precision
limit_depth = 500
repeat_depth = 100

# mandelbrot region
left = -2.5
right = +1.25
top = +1.25
bottom = -1.25

# mandelbrot coloring
diverge_color = [cm.get_cmap('hsv')(d/repeat_depth) for d in range(repeat_depth)]
diverge_color = [tuple(int(x*255) for x in color) for color in diverge_color]
diverge_color *= 1 + limit_depth//repeat_depth
diverge_color = diverge_color[:-38][::-1]
mandelbrot_color = (255, 255, 255)


# code =======================================================================

width_pixel = dpi * width_inch
height_pixel = dpi * height_inch


def mandelbrot_accept(c):
    is_main_cardioid = (abs(1-(1-4*c)**.5) < 1)
    is_main_disk = (abs(1+c) < 1/4)
    return is_main_cardioid or is_main_disk


def mandelbrot_diverge(c, limit_depth):
    if mandelbrot_accept(c):
        return None
    z = complex(0, 0)
    for depth in range(limit_depth):
        z = z**2 + c
        if abs(z) > 2:
            return depth
    return None


def pixel_to_coordinate(px, py):
    cx = left + (right - left) * px / width_pixel
    cy = top - (top - bottom) * py / height_pixel
    return cx, cy


def process(pixel_index):
    if number_progress_ticks and pixel_index % (width_pixel*height_pixel//number_progress_ticks) == 0:
        print(f'.', end='', flush=True)
    y, x = divmod(pixel_index, width_pixel)
    a, b = pixel_to_coordinate(x, y)
    diverge_factor = mandelbrot_diverge(complex(a, b), limit_depth)
    if diverge_factor is None:
        return x, y, mandelbrot_color
    return x, y, diverge_color[diverge_factor]


image = Image.new('RGB', size=(width_pixel, height_pixel))
data = image.load()
pool = multiprocessing.Pool(number_parallel_processors)
for x, y, color in pool.map(process, range(width_pixel*height_pixel)):
    data[x,y] = color
print()
image.save(f'image-mandelbrot-{width_inch}x{height_inch}-{dpi}dpi.{fileformat}', resolution=dpi)
