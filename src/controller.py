from typing import Optional

import numpy as np
import pygame as pg

from coordinate_system import CoordinateSystem
from elements import ElementBuffer, Element, Transformed, CustomTransformed
from user_interface import UserInterface


class Controller:
    def __init__(self):
        self.running = True
        self.update_needed = True
        self.is_dragging = False
        self.dragged_element: Element or None = None
        self.mouse_position = np.array(pg.mouse.get_pos(), dtype=int)

        self.selected_transformed: Optional[Transformed] = None
        self.get_definition_for: Optional = None

    def handle_event(self, event, coordinate_system: CoordinateSystem, element_buffer: ElementBuffer,
                     user_interface: UserInterface):
        user_interface.handle_event(event, self.mouse_position)
        if event.type == pg.QUIT:
            self.running = False
        elif event.type == pg.MOUSEWHEEL:
            if not user_interface.ui_rect.collidepoint(self.mouse_position):
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
                        self.dragged_element = element
                        self.is_dragging = False
            self.update_needed = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.is_dragging = False
            self.dragged_element = None
        elif event.type == pg.MOUSEMOTION:
            if self.is_dragging:
                coordinate_system.translate(np.array(event.rel))
                self.update_needed = True
            if self.dragged_element:
                pos = coordinate_system.transform_inverse(np.array(event.pos))
                self.dragged_element.move_to(pos)
                self.update_needed = True
            self.mouse_position = np.array(event.pos, dtype=int)
        elif event.type == pg.WINDOWENTER or event.type == pg.WINDOWFOCUSGAINED:
            self.update_needed = True
        elif event.type == pg.KEYUP:
            if self.get_definition_for is not None:
                if event.key == 27:
                    self.get_definition_for.compile_definition()
                    self.get_definition_for = None
                    self.update_needed = True
                else:
                    custom_transformed: CustomTransformed = self.get_definition_for
                    if event.key == 8:
                        custom_transformed.set_definition(custom_transformed.definition[:-1])
                    elif event.key == 127:
                        custom_transformed.set_definition('')
                    elif event.unicode:
                        custom_transformed.set_definition(custom_transformed.definition + event.unicode)
                    self.update_needed = True
        elif event.type == pg.KEYDOWN:
            self.update_needed = True
        else:
            # print(event)
            pass

        self.handle_hovering(element_buffer, coordinate_system)

    def handle_hovering(self, element_buffer: ElementBuffer, coordinate_system: CoordinateSystem):
        for element in element_buffer:
            element.hovered = element.is_hovered(self.mouse_position, coordinate_system)
