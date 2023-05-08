#!/usr/bin/env python3


import pygame as pg

from coordinate_system import DEFAULT_SCREEN_SIZE, CoordinateSystem
from render import render


def main():
    pg.init()
    screen = pg.display.set_mode(DEFAULT_SCREEN_SIZE)
    running = True
    update_needed = True
    coordinate_system = CoordinateSystem()

    while running:
        events = [pg.event.wait()]
        for event in events + pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEWHEEL:
                if event.y == -1:
                    coordinate_system.zoom_out()
                else:
                    coordinate_system.zoom_in()
                update_needed = True
            else:
                pass
                # print(event)

        if update_needed:
            render(screen, coordinate_system)
            pg.display.flip()
            update_needed = False

    pg.quit()


if __name__ == '__main__':
    main()

