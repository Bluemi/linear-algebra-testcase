import numpy as np
import pygame as pg
from pygame import Surface, Color

from controller import Controller
from coordinate_system import CoordinateSystem
from elements import ElementBuffer, Vector


def render(
    screen: Surface, coordinate_system: CoordinateSystem, element_buffer: ElementBuffer, render_font,
    controller: Controller
):
    screen.fill("black")
    draw_coordinate_system(screen, coordinate_system, render_font)
    draw_elements(screen, coordinate_system, element_buffer, controller)


def draw_coordinate_system(screen: Surface, coordinate_system: CoordinateSystem, render_font):
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

    # draw numbers
    zero_point = coordinate_system.transform(np.array([0, 0]))
    if 0 < zero_point[0] < screen.get_width():
        for y in range(extreme_points[1, 1], extreme_points[0, 1] + 2):
            font = render_font.render(str(y), True, pg.Color(120, 120, 120), pg.Color(0, 0, 0, 0))
            pos = coordinate_system.transform(np.array([0, y]))
            pos += 10
            screen.blit(font, pos)

    if 0 < zero_point[1] < screen.get_height():
        for x in range(extreme_points[0, 0]-1, extreme_points[1, 0] + 1):
            font = render_font.render(str(x), True, pg.Color(120, 120, 120), pg.Color(0, 0, 0, 0))
            pos = coordinate_system.transform(np.array([x, 0]))
            pos += 10
            screen.blit(font, pos)


def draw_elements(
    screen: Surface, coordinate_system: CoordinateSystem, element_buffer: ElementBuffer, controller: Controller
):
    zero_point = coordinate_system.transform(np.array([0, 0]))

    for element in element_buffer.elements:
        if isinstance(element, Vector):
            transformed_vec = coordinate_system.transform(element.coordinates)
            width = 3 if element.is_hovered(controller.mouse_position, coordinate_system) else 1
            pg.draw.line(screen, pg.Color(120, 200, 120), zero_point, transformed_vec, width=width)
