import numpy as np
import pygame as pg

from coordinate_system import CoordinateSystem
from elements import ElementBuffer
from user_interface import UserInterface


class Controller:
    def __init__(self):
        self.running = True
        self.update_needed = True
        self.is_dragging = False
        self.mouse_position = np.array(pg.mouse.get_pos(), dtype=int)

    def handle_event(self, event, coordinate_system: CoordinateSystem, element_buffer: ElementBuffer,
                     user_interface: UserInterface):
        user_interface.handle_event(event, self.mouse_position)
        if not user_interface.consuming_events(self.mouse_position):
            element_buffer.handle_event(event, coordinate_system, self.mouse_position)

        if event.type == pg.QUIT:
            self.running = False
        elif event.type == pg.MOUSEWHEEL:
            if not user_interface.consuming_events(self.mouse_position):
                if event.y < 0:
                    coordinate_system.zoom_out()
                else:
                    coordinate_system.zoom_in()
            self.update_needed = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            if not user_interface.ui_rect.collidepoint(self.mouse_position):
                self.is_dragging = True
                for element in element_buffer.elements:
                    if element.is_hovered(self.mouse_position, coordinate_system):
                        self.is_dragging = False
            self.update_needed = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.is_dragging = False
            self.update_needed = True
        elif event.type == pg.MOUSEMOTION:
            if self.is_dragging:
                coordinate_system.translate(np.array(event.rel))
            self.mouse_position = np.array(event.pos, dtype=int)
            self.update_needed = True
        elif event.type == pg.WINDOWENTER or event.type == pg.WINDOWFOCUSGAINED:
            self.update_needed = True
        elif event.type == pg.KEYUP:
            self.update_needed = True
        elif event.type == pg.KEYDOWN:
            self.update_needed = True
        elif event.type == pg.WINDOWRESIZED:
            self.update_needed = True
        else:
            pass

        self.handle_hovering(element_buffer, coordinate_system)

    def handle_hovering(self, element_buffer: ElementBuffer, coordinate_system: CoordinateSystem):
        for element in element_buffer:
            element.hovered = element.is_hovered(self.mouse_position, coordinate_system)
