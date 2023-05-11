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
    extreme_points = np.array([
        [0, 0],
        [screen.get_width(), screen.get_height()]
    ])
    extreme_points = np.trunc(coordinate_system.transform_inverse(extreme_points)).astype(int)
    for x in range(extreme_points[0, 0], extreme_points[1, 0]+1):
        vertical_lines = np.array([[x, 0], [x, 0]])
        transformed_vertical_lines = coordinate_system.transform(vertical_lines)
        transformed_vertical_lines[:, 1] = [0, screen.get_height()]
        color = Color(30, 30, 30)
        if x == 0:
            color = Color(50, 50, 50)
        pg.draw.line(screen, color, transformed_vertical_lines[0], transformed_vertical_lines[1])

    for y in range(extreme_points[1, 1], extreme_points[0, 1]+1):
        horizontal_lines = np.array([[extreme_points[0, 0], y], [extreme_points[1, 0], y]])
        transformed_horizontal_lines = coordinate_system.transform(horizontal_lines)
        transformed_horizontal_lines[:, 0] = [0, screen.get_width()]
        color = Color(30, 30, 30)
        if y == 0:
            color = Color(50, 50, 50)
        pg.draw.line(screen, color, transformed_horizontal_lines[0], transformed_horizontal_lines[1])


def draw_elements(screen: Surface, coordinate_system: CoordinateSystem, element_buffer: ElementBuffer):
    zero_point = coordinate_system.transform(np.array([0, 0]))

    if element_buffer.vectors:
        for vector in element_buffer.vectors:
            transformed_vec = coordinate_system.transform(vector)
            pg.draw.line(screen, "green", zero_point, transformed_vec)

    if element_buffer.vectors_transformed:
        for vector in element_buffer.vectors_transformed:
            transformed_vec = coordinate_system.transform(vector)
            pg.draw.line(screen, "red", zero_point, transformed_vec)

    if element_buffer.points:
        transformed_points = coordinate_system.transform(element_buffer.points)
        for p in transformed_points:
            if 0 <= p[0] <= screen.get_width() and 0 <= p[1] <= screen.get_height():
                pg.draw.circle(screen, "green", p, 2)

    if element_buffer.points_transformed:
        transformed_points = coordinate_system.transform(element_buffer.points_transformed)
        for p in transformed_points:
            if 0 <= p[0] <= screen.get_width() and 0 <= p[1] <= screen.get_height():
                pg.draw.circle(screen, "red", p, 2)

    if element_buffer.eig_vecs:
        transformed_eig_vecs = coordinate_system.transform(element_buffer.eig_vecs)
        for p in transformed_eig_vecs:
            pg.draw.line(screen, "red", zero_point, p)
