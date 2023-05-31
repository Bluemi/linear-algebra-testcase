import numpy as np
import pygame as pg

from coordinate_system import CoordinateSystem
from elements import ElementBuffer, Element
from user_interface import UserInterface


class Controller:
    def __init__(self):
        self.running = True
        self.update_needed = True
        self.is_dragging = False
        self.dragged_element: Element or None = None
        self.mouse_position = np.array(pg.mouse.get_pos(), dtype=int)

    def handle_event(self, event, coordinate_system: CoordinateSystem, element_buffer: ElementBuffer,
                     user_interface: UserInterface):
        if event.type == pg.QUIT:
            self.running = False
        elif event.type == pg.MOUSEWHEEL:
            if event.y < 0:
                coordinate_system.zoom_out()
            else:
                coordinate_system.zoom_in()
            self.update_needed = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            if user_interface.menu_rect.collidepoint(self.mouse_position):
                user_interface.toggle()
                self.update_needed = True
            else:
                self.is_dragging = True
                for element in element_buffer.elements:
                    if element.is_hovered(self.mouse_position, coordinate_system):
                        self.dragged_element = element
                        self.is_dragging = False
                        break
        elif event.type == pg.MOUSEBUTTONUP:
            self.is_dragging = False
            self.dragged_element = None
        elif event.type == pg.MOUSEMOTION:
            if self.is_dragging:
                coordinate_system.translate(np.array(event.rel))
            if self.dragged_element:
                pos = coordinate_system.transform_inverse(np.array(event.pos))
                self.dragged_element.move_to(pos)
            self.mouse_position = np.array(event.pos, dtype=int)
            self.update_needed = True
        elif event.type == pg.WINDOWENTER or event.type == pg.WINDOWFOCUSGAINED:
            self.update_needed = True
        elif event.type == pg.KEYUP:
            if event.unicode == 'n':
                # element_buffer.generate_transform(default=False)
                self.update_needed = True
            elif event.key == 27:
                self.running = False
        else:
            # print(event)
            pass

    def update_element_buffer(self, element_buffer: ElementBuffer):
        # set selected element
        # element_buffer()
        pass
