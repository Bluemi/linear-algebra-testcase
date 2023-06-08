#!/usr/bin/env python3


import pygame as pg

from controller import Controller
from coordinate_system import DEFAULT_SCREEN_SIZE, CoordinateSystem
from elements import ElementBuffer
from render import render
from user_interface import UserInterface


def main():
    pg.init()
    screen = pg.display.set_mode(DEFAULT_SCREEN_SIZE)
    controller = Controller()
    coordinate_system = CoordinateSystem()
    element_buffer = ElementBuffer()
    render_font = pg.font.Font(pg.font.get_default_font(), 18)
    user_interface = UserInterface()

    while controller.running:
        events = [pg.event.wait()]
        for event in events + pg.event.get():
            controller.handle_event(event, coordinate_system, element_buffer, user_interface)

        element_buffer.remove_elements()

        user_interface.build(element_buffer)

        if controller.update_needed:
            render(screen, coordinate_system, element_buffer, render_font, user_interface)
            pg.display.flip()
            controller.update_needed = False

    pg.quit()


if __name__ == '__main__':
    main()

