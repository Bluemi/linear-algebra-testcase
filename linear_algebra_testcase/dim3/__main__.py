#!/usr/bin/env python3


import sys
import time

import numpy as np
import pygame as pg

from linear_algebra_testcase.dim3.controller import Controller
from linear_algebra_testcase.dim3.coordinate_system import DEFAULT_SCREEN_SIZE, CoordinateSystem
from linear_algebra_testcase.dim3.elements import ElementBuffer
from linear_algebra_testcase.dim3.render import render
from linear_algebra_testcase.utils import Dimension
from linear_algebra_testcase.utils.user_interface import UserInterface


class Main:
    def __init__(self):
        pg.init()
        pg.key.set_repeat(130, 25)
        self.screen = pg.display.set_mode(DEFAULT_SCREEN_SIZE)
        self.controller = Controller()
        self.coordinate_system = CoordinateSystem(position=np.array([1.1, 1.0, 2.8]))
        self.coordinate_system.rotate(np.array([0.2, -0.16]))
        self.element_buffer = ElementBuffer()
        self.render_font = pg.font.Font(pg.font.get_default_font(), 18)
        self.user_interface = UserInterface()
        self.frame_rate = 60
        self.clock = pg.time.Clock()

    def run(self):
        while self.controller.running:
            self.handle_events(pg.event.get())

            # render
            render(self.screen, self.coordinate_system, self.element_buffer, self.render_font, self.user_interface)
            pg.display.flip()

            self.clock.tick(self.frame_rate)

        pg.quit()

    def handle_events(self, events):
        for event in events:
            self.controller.handle_event(event, self.coordinate_system, self.element_buffer, self.user_interface)
        self.controller.tick(self.coordinate_system, self.user_interface)
        self.element_buffer.remove_elements()

        self.user_interface.build(self.element_buffer, Dimension.d3)


def main():
    main_instance = Main()
    if "pyodide" in sys.modules:
        # noinspection PyUnresolvedReferences
        pg.event.register_event_callback(main_instance.handle_events)
        return main_instance
    else:
        main_instance.run()


if __name__ == '__main__':
    main()
