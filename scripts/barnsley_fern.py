#!/usr/bin/env python3

from functools import reduce

from numpy import array, matmul, pad, eye
from numpy.linalg import inv
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance


# ============================================================================

# printing quality
dpi = 300
width_inch = 2 * 12
height_inch = 3 * 12

# file handling
fileformat = 'pdf'  # png, pdf

# computation
log_progress = True
log_inner_iterate_image = True

# fern precision
depth = 50

# fern coloring
background_color = '#fff'
stem_color = '#040'
final_brightness = 0.75


# ============================================================================

width_pixel = width_inch * dpi
height_pixel = height_inch * dpi
size = (width_pixel, height_pixel)

plot_length = 11
linewidth = 2 * width_inch
unit = height_pixel / plot_length


def make_pil_affine(mtx, vec):
    # NOTE: PIL use invert affine transformation!
    to_origin = array([[1, 0, +width_pixel/2], [0, 1, +height_pixel], [0, 0, 1]])
    move_back = array([[1, 0, -width_pixel/2], [0, 1, -height_pixel], [0, 0, 1]])
    alternate = array([(-1)**k for k in range(9)]).reshape((3,3))
    transform = inv(alternate*pad(mtx, [(0,1),(0,1)]) + pad([[1]], [(2,0),(2,0)]))
    translate = eye(3) + unit*pad([vec], [(2,0), (0,1)]).transpose()
    return reduce(matmul, [to_origin, transform, move_back, translate]).flatten()


def draw_stem(image):
    spec = [ width_pixel/2 - linewidth/2, height_pixel,
             width_pixel/2 - 0.9 * linewidth/2, height_pixel - 1.6*unit - 1,
             width_pixel/2 + 0.9 * linewidth/2, height_pixel - 1.6*unit - 1,
             width_pixel/2 + linewidth/2, height_pixel, ]
    ImageDraw.Draw(image).polygon(spec, fill=stem_color)



affines = [ make_pil_affine(mtx=[[+.85, +.04], [-.04, +.85]], vec=[0, 1.6]),
            make_pil_affine(mtx=[[+.20, -.26], [+.23, +.22]], vec=[0, 1.6]),
            make_pil_affine(mtx=[[-.15, +.28], [+.26, +.24]], vec=[0, .44]), ]

stem = Image.new('RGBA', size)
draw_stem(stem)
if log_inner_iterate_image:
    stem.save(f'iterate-0.png')

for i in range(depth):
    base = Image.new('RGBA', size)
    draw_stem(base)
    stem = stem.filter(ImageFilter.MaxFilter(size=3))
    for affine in affines:
        altered = stem.transform(size, Image.AFFINE, affine, resample=Image.BICUBIC)
        base.paste(altered, (0,0), altered)
        altered.close()
    stem.close()
    stem = base
    if log_inner_iterate_image:
        stem.save(f'iterate-{i+1}.png')
    if log_progress:
        print(f'done loop: {i+1}')

stem = ImageEnhance.Brightness(stem).enhance(final_brightness)
final = Image.new('RGBA', size, background_color)
final.paste(stem, (0,0), stem)
final.save('fern-final.{fileformat}', resolution=dpi)
