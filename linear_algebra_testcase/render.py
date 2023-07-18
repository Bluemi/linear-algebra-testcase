import numpy as np
import pygame as pg
from pygame import Surface, Color

from linear_algebra_testcase.coordinate_system import CoordinateSystem, DEFAULT_SCREEN_SIZE
from linear_algebra_testcase.elements import ElementBuffer
from linear_algebra_testcase.user_interface import UserInterface

TARGET_NUM_POINTS = 12
TARGET_DIVIDENDS = [1, 2.5, 5, 10]


def render(
    screen: Surface, coordinate_system: CoordinateSystem, element_buffer: ElementBuffer, render_font,
    user_interface: UserInterface
):
    screen.fill(pg.Color(0, 0, 0))
    draw_coordinate_system(screen, coordinate_system, render_font)
    element_buffer.render(screen, coordinate_system)
    user_interface.render(screen)


def draw_coordinate_system(screen: Surface, coordinate_system: CoordinateSystem, render_font):
    def adapt_quotient(quotient):
        if quotient <= 0:
            raise ValueError('Invalid quotient: {}'.format(quotient))
        numb_ten_potency = 0
        while quotient > 10:
            quotient *= 0.1
            numb_ten_potency += 1
        while quotient < 1:
            quotient *= 10
            numb_ten_potency -= 1

        diffs = [abs(quotient - target) for target in TARGET_DIVIDENDS]
        index = np.argmin(diffs)
        best_fitting = TARGET_DIVIDENDS[index] * (10 ** numb_ten_potency)

        return best_fitting

    extreme_points = np.array([
        [0, 0],
        [screen.get_width(), screen.get_height()]
    ]).T
    extreme_points = coordinate_system.transform_inverse(extreme_points).T
    target_num_points = TARGET_NUM_POINTS * screen.get_width() // DEFAULT_SCREEN_SIZE[0]
    target_dividend = (extreme_points[1, 0] - extreme_points[0, 0]) / target_num_points
    dividend = adapt_quotient(target_dividend)
    x_minimum = np.round(extreme_points[0, 0] / dividend) * dividend
    x_maximum = np.round(extreme_points[1, 0] / dividend) * dividend
    x_points = np.arange(x_minimum, x_maximum + dividend, dividend)
    for x in x_points:
        vertical_lines = np.array([[x, 0], [x, 0]])
        transformed_vertical_lines = coordinate_system.transform(vertical_lines.T).T
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
        transformed_horizontal_lines = coordinate_system.transform(horizontal_lines.T).T
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
