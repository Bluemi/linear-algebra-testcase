import numpy as np
import pygame as pg
from pygame import Surface, Color

from controller import Controller
from coordinate_system import CoordinateSystem
from elements import ElementBuffer, Vector
from user_interface import UserInterface

TARGET_NUM_POINTS = 12
TARGET_DIVIDENDS = [1, 2, 4, 5, 10]


def render(
    screen: Surface, coordinate_system: CoordinateSystem, element_buffer: ElementBuffer, render_font,
    controller: Controller, user_interface: UserInterface
):
    screen.fill("black")
    draw_coordinate_system(screen, coordinate_system, render_font)
    draw_elements(screen, coordinate_system, element_buffer, controller)
    draw_user_interface(screen, user_interface, element_buffer, controller)


def draw_coordinate_system(screen: Surface, coordinate_system: CoordinateSystem, render_font):
    def adapt_quotient(quotient):
        if quotient <= 0:
            raise ValueError('Invalid quotient: {}'.format(quotient))
        numb_ten_potentes = 0
        while quotient > 10:
            quotient *= 0.1
            numb_ten_potentes += 1
        while quotient < 1:
            quotient *= 10
            numb_ten_potentes -= 1

        diffs = [abs(quotient - target) for target in TARGET_DIVIDENDS]
        index = np.argmin(diffs)
        best_fitting = TARGET_DIVIDENDS[index] * (10 ** numb_ten_potentes)

        return best_fitting

    extreme_points = np.array([
        [0, 0],
        [screen.get_width(), screen.get_height()]
    ])
    extreme_points = coordinate_system.transform_inverse(extreme_points)
    target_dividend = (extreme_points[1, 0] - extreme_points[0, 0]) / TARGET_NUM_POINTS
    # extreme_points = np.trunc(extreme_points).astype(int)
    dividend = adapt_quotient(target_dividend)
    x_minimum = np.round(extreme_points[0, 0] / dividend) * dividend
    x_maximum = np.round(extreme_points[1, 0] / dividend) * dividend
    x_points = np.arange(x_minimum, x_maximum + dividend, dividend)
    for x in x_points:
        vertical_lines = np.array([[x, 0], [x, 0]])
        transformed_vertical_lines = coordinate_system.transform(vertical_lines)
        transformed_vertical_lines[:, 1] = [0, screen.get_height()]
        color = Color(30, 30, 30)
        if x == 0:
            color = Color(50, 50, 50)
        pg.draw.line(screen, color, transformed_vertical_lines[0], transformed_vertical_lines[1])

    y_minimum = np.round(extreme_points[1, 1] / dividend) * dividend
    y_maximum = np.round(extreme_points[0, 1] / dividend) * dividend
    y_points = np.arange(y_minimum, y_maximum + dividend, dividend)

    for y in y_points:
        horizontal_lines = np.array([[extreme_points[0, 0], y], [extreme_points[1, 0], y]])
        transformed_horizontal_lines = coordinate_system.transform(horizontal_lines)
        transformed_horizontal_lines[:, 0] = [0, screen.get_width()]
        color = Color(30, 30, 30)
        if y == 0:
            color = Color(50, 50, 50)
        pg.draw.line(screen, color, transformed_horizontal_lines[0], transformed_horizontal_lines[1])

    # draw numbers
    zero_point = coordinate_system.transform(np.array([0, 0]))

    if 0 < zero_point[1] < screen.get_height():
        for x in x_points:
            if abs(x) > 10 ** -5:
                float_format = '{:.2f}' if abs(x) > 1 else '{:.2}'
                font = render_font.render(float_format.format(x), True, pg.Color(120, 120, 120), pg.Color(0, 0, 0, 0))
                pos = coordinate_system.transform(np.array([x, 0]))
                pos += 10
                screen.blit(font, pos)

    if 0 < zero_point[0] < screen.get_width():
        for y in y_points:
            if abs(y) > 10 ** -5:
                float_format = '{:.2f}' if abs(y) > 1 else '{:.2}'
                font = render_font.render(float_format.format(y), True, pg.Color(120, 120, 120), pg.Color(0, 0, 0, 0))
                pos = coordinate_system.transform(np.array([0, y]))
                pos += 10
                screen.blit(font, pos)


def draw_user_interface(screen: Surface, user_interface: UserInterface, element_buffer: ElementBuffer,
                        controller: Controller):
    if user_interface.showing:
        pass
    else:
        # *([40] * 3)
        alpha = 255 if user_interface.menu_rect.collidepoint(controller.mouse_position) else 180
        user_interface.menu_image.set_alpha(alpha)
        screen.blit(user_interface.menu_image, user_interface.menu_rect)
        # pg.draw.rect(screen, Color(40, 40, 40, 50), user_interface.menu_rect)


def draw_elements(
    screen: Surface, coordinate_system: CoordinateSystem, element_buffer: ElementBuffer, controller: Controller
):
    zero_point = coordinate_system.transform(np.array([0, 0]))

    for element in element_buffer.elements:
        if isinstance(element, Vector):
            transformed_vec = coordinate_system.transform(element.coordinates)
            width = 3 if element.is_hovered(controller.mouse_position, coordinate_system) else 1
            pg.draw.line(screen, pg.Color(120, 200, 120), zero_point, transformed_vec, width=width)
