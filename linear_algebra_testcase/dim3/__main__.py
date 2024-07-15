#!/usr/bin/env python3


import sys
import pygame as pg

from linear_algebra_testcase.dim2.controller import Controller
from linear_algebra_testcase.dim2.coordinate_system import DEFAULT_SCREEN_SIZE, CoordinateSystem
from linear_algebra_testcase.dim2.elements import ElementBuffer
from linear_algebra_testcase.dim3.render import render
from linear_algebra_testcase.utils.user_interface import UserInterface


class Main:
    def __init__(self):
        pg.init()
        pg.key.set_repeat(130, 25)
        self.screen = pg.display.set_mode(DEFAULT_SCREEN_SIZE)
        self.controller = Controller()
        self.coordinate_system = CoordinateSystem()
        self.element_buffer = ElementBuffer()
        self.render_font = pg.font.Font(pg.font.get_default_font(), 18)
        self.user_interface = UserInterface()

    def run(self):
        while self.controller.running:
            events = [pg.event.wait()]
            events = events + pg.event.get()
            self.handle_events(events)

        pg.quit()

    def handle_events(self, events):
        for event in events:
            self.controller.handle_event(event, self.coordinate_system, self.element_buffer, self.user_interface)

        self.element_buffer.remove_elements()

        self.user_interface.build(self.element_buffer)

        if self.controller.update_needed:
            render(self.screen, self.coordinate_system, self.element_buffer, self.render_font, self.user_interface)
            pg.display.flip()
            self.controller.update_needed = False


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
