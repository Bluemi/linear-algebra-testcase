#!/usr/bin/env python3


import pygame as pg

from coordinate_system import DEFAULT_SCREEN_SIZE, CoordinateSystem
from render import render


def main():
    pg.init()
    screen = pg.display.set_mode(DEFAULT_SCREEN_SIZE)
    clock = pg.time.Clock()
    running = True
    coordinate_system = CoordinateSystem()

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame
        render(screen, coordinate_system)

        pg.display.flip()

        clock.tick(60)  # limits FPS to 60

    pg.quit()


if __name__ == '__main__':
    main()

