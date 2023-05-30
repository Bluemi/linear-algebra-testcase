import numpy as np
import pygame as pg

from coordinate_system import CoordinateSystem
from element_buffer import ElementBuffer


class Controller:
    def __init__(self):
        self.running = True
        self.update_needed = True
        self.is_dragging = False
        self.mouse_position = np.array(pg.mouse.get_pos(), dtype=int)

    def handle_event(self, event, coordinate_system: CoordinateSystem, element_buffer: ElementBuffer):
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
            self.mouse_position = np.array(event.pos, dtype=int)
        elif event.type == pg.WINDOWENTER or event.type == pg.WINDOWFOCUSGAINED:
            self.update_needed = True
        elif event.type == pg.KEYUP:
            if event.unicode == 'n':
                # element_buffer.generate_transform(default=False)
                element_buffer.generate_rotation_vec()
                self.update_needed = True
            elif event.key == 27:
                self.running = False
        else:
            # print(event)
            pass

    def update_element_buffer(self, element_buffer: ElementBuffer):
        # set selected element
        element_buffer()
