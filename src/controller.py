import numpy as np
import pygame as pg

from coordinate_system import CoordinateSystem


class Controller:
    def __init__(self):
        self.running = True
        self.update_needed = True
        self.is_dragging = False

    def handle_event(self, event, coordinate_system: CoordinateSystem):
        if event.type == pg.QUIT:
            self.running = False
        elif event.type == pg.MOUSEWHEEL:
            if event.y < 0:
                coordinate_system.zoom_out()
            else:
                coordinate_system.zoom_in()
            self.update_needed = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            self.is_dragging = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.is_dragging = False
        elif event.type == pg.MOUSEMOTION:
            if self.is_dragging:
                coordinate_system.translate(np.array(event.rel))
                self.update_needed = True
        else:
            # print(event)
            pass
