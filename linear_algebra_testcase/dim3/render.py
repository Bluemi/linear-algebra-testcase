import numpy as np
import pygame as pg
from pygame import Surface, Color

from .coordinate_system import CoordinateSystem, DEFAULT_SCREEN_SIZE
from .elements import ElementBuffer
from linear_algebra_testcase.utils.user_interface import UserInterface

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
    pass
