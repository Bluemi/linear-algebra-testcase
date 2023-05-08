import numpy as np
import pygame as pg
from pygame import Surface

from coordinate_system import CoordinateSystem


def render(screen: Surface, coordinate_system: CoordinateSystem):
    screen.fill("black")
    draw_coordinate_system(screen, coordinate_system)


def draw_coordinate_system(screen: Surface, coordinate_system: CoordinateSystem):
    line_coords = np.array([[-1, -1], [1, 1]])
    line_coords = coordinate_system(line_coords)

    line_coords_green = np.array([[0, -1], [0, 1]])
    line_coords_green = coordinate_system(line_coords_green)

    line_coords1 = np.array([1, -1])
    line_coords2 = np.array([-1, 1])
    line_coords1 = coordinate_system(line_coords1)
    line_coords2 = coordinate_system(line_coords2)

    pg.draw.line(screen, "red", line_coords[0], line_coords[1])
    pg.draw.line(screen, "blue", line_coords1, line_coords2)
    pg.draw.line(screen, "green", line_coords_green[0], line_coords_green[1])
