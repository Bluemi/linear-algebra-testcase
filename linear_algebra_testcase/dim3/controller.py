from itertools import chain

import numpy as np
import pygame as pg
from scipy.spatial.transform import Rotation

from .coordinate_system import CoordinateSystem
from .elements import ElementBuffer
from linear_algebra_testcase.utils.user_interface import UserInterface


class Controller:
    def __init__(self):
        self.running = True
        self.is_dragging = False
        self.mouse_position = np.array(pg.mouse.get_pos(), dtype=int)

    def handle_event(self, event, coordinate_system: CoordinateSystem, element_buffer: ElementBuffer,
                     user_interface: UserInterface):
        user_interface.handle_event(event, self.mouse_position)
        if not user_interface.consuming_events(self.mouse_position):
            element_buffer.handle_event(event, coordinate_system, self.mouse_position)
            handle_coordinate_system_events(event, coordinate_system)

        if event.type == pg.QUIT:
            self.running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            if not user_interface.consuming_events(self.mouse_position):
                self.is_dragging = True
                for element in chain(element_buffer.elements, element_buffer.transforms):
                    if element.is_hovered(self.mouse_position, coordinate_system):
                        self.is_dragging = False
        elif event.type == pg.MOUSEBUTTONUP:
            self.is_dragging = False
        elif event.type == pg.MOUSEMOTION:
            self.mouse_position = np.array(event.pos, dtype=int)
        else:
            # print(event)
            pass

    def tick(self, coordinate_system, user_interface):
        if not user_interface.consuming_events(self.mouse_position):
            handle_coordinate_system(coordinate_system)


def handle_coordinate_system(coordinate_system: CoordinateSystem):
    keys = pg.key.get_pressed()
    speed = 0.02
    if keys[pg.K_w]:
        coordinate_system.move(np.array([0.0, 0.0, -speed]))
    if keys[pg.K_a]:
        coordinate_system.move(np.array([-speed, 0.0, 0.0]))
    if keys[pg.K_s]:
        coordinate_system.move(np.array([0.0, 0.0, speed]))
    if keys[pg.K_d]:
        coordinate_system.move(np.array([speed, 0.0, 0.0]))
    if keys[pg.K_SPACE]:
        coordinate_system.move(np.array([0.0, speed, 0.0]))
    if keys[pg.K_LCTRL]:
        coordinate_system.move(np.array([0.0, -speed, 0.0]))


def handle_coordinate_system_events(event, coordinate_system: CoordinateSystem):
    screen_info = pg.display.Info()
    screen_center = np.array([screen_info.current_w // 2, screen_info.current_h // 2], dtype=int)

    pg.mouse.set_pos(*screen_center)

    if event.type == pg.MOUSEMOTION:
        rotation_speed = 0.01
        rotation = np.array(event.rel, dtype=int) * -rotation_speed
        rotation = Rotation.from_euler('yx', rotation)
        coordinate_system.rotate(rotation)

        # keep mouse in center of screen
        pg.mouse.set_pos(*screen_center)
