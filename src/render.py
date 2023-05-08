import numpy as np
import pygame as pg
from pygame import Surface, Color

from coordinate_system import CoordinateSystem
from element_buffer import ElementBuffer


def render(screen: Surface, coordinate_system: CoordinateSystem, element_buffer: ElementBuffer):
    screen.fill("black")
    draw_coordinate_system(screen, coordinate_system)
    draw_elements(screen, coordinate_system, element_buffer)


def draw_coordinate_system(screen: Surface, coordinate_system: CoordinateSystem):
    for x in range(-10, 11):
        vertical_lines = np.array([[x, -10], [x, 10]])
        transformed_vertical_lines = coordinate_system(vertical_lines)
        color = Color(30, 30, 30)
        if x == 0:
            color = Color(50, 50, 50)
        pg.draw.line(screen, color, transformed_vertical_lines[0], transformed_vertical_lines[1])

    for y in range(-10, 11):
        horizontal_lines = np.array([[-10, y], [10, y]])
        transformed_horizontal_lines = coordinate_system(horizontal_lines)
        color = Color(30, 30, 30)
        if y == 0:
            color = Color(50, 50, 50)
        pg.draw.line(screen, color, transformed_horizontal_lines[0], transformed_horizontal_lines[1])


def draw_elements(screen: Surface, coordinate_system: CoordinateSystem, element_buffer: ElementBuffer):
    zero_point = coordinate_system(np.array([0, 0]))
    for vector in element_buffer.vectors:
        transformed_vec = coordinate_system(vector)
        pg.draw.line(screen, "red", zero_point, transformed_vec)
