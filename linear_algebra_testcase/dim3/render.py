import sys

import numpy as np
import pygame as pg
from pygame import Surface, Color

from .coordinate_system import CoordinateSystem, DEFAULT_SCREEN_SIZE
from .elements import ElementBuffer
from linear_algebra_testcase.utils.user_interface import UserInterface
from ..utils import gray

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
    extreme_value = 4.0
    values = np.arange(-extreme_value, extreme_value + 0.01, 0.1)
    for axis in range(3):
        extrem_points = np.zeros((len(values), 3))
        extrem_points[:, axis] = values
        screen_points = coordinate_system.transform(extrem_points)[:, :2]

        last_point = None
        for point in screen_points:
            if last_point is not None:
                pg.draw.line(screen, gray(70), last_point, point, 1)
            last_point = point
