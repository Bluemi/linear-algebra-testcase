#!/usr/bin/env python3


import pygame as pg

from controller import Controller
from coordinate_system import DEFAULT_SCREEN_SIZE, CoordinateSystem
from element_buffer import ElementBuffer
from render import render


def main():
    pg.init()
    screen = pg.display.set_mode(DEFAULT_SCREEN_SIZE)
    controller = Controller()
    coordinate_system = CoordinateSystem()
    element_buffer = ElementBuffer()
    element_buffer.create_example_elements()
    render_font = pg.font.Font(pg.font.get_default_font(), 18)

    while controller.running:
        events = [pg.event.wait()]
        for event in events + pg.event.get():
            controller.handle_event(event, coordinate_system, element_buffer)

        if controller.update_needed:
            render(screen, coordinate_system, element_buffer, render_font)
            pg.display.flip()
            controller.update_needed = False

    pg.quit()


if __name__ == '__main__':
    main()

