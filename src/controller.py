import numpy as np
import pygame as pg

from coordinate_system import CoordinateSystem
from elements import ElementBuffer, Element, Transform
from user_interface import UserInterface, Action, UIElement, UIText


class Controller:
    def __init__(self):
        self.running = True
        self.update_needed = True
        self.is_dragging = False
        self.dragged_element: Element or None = None
        self.mouse_position = np.array(pg.mouse.get_pos(), dtype=int)
        self.actions = []

    def handle_event(self, event, coordinate_system: CoordinateSystem, element_buffer: ElementBuffer,
                     user_interface: UserInterface):
        self.actions = []
        if event.type == pg.QUIT:
            self.running = False
        elif event.type == pg.MOUSEWHEEL:
            if user_interface.showing and user_interface.ui_rect.collidepoint(self.mouse_position):
                user_interface.scroll_position = max(user_interface.scroll_position - event.y * 8, 0)
            else:
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
                if user_interface.showing and user_interface.ui_rect.collidepoint(self.mouse_position):
                    # handle mouse press in ui rect
                    for ui_element in user_interface.ui_elements:
                        if ui_element.rect.collidepoint(self.mouse_position):
                            self.actions.append(ui_element.on_click())
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

        self.handle_actions(element_buffer)
        self.handle_hovering(element_buffer, coordinate_system, user_interface)

    def update_element_buffer(self, element_buffer: ElementBuffer):
        # set selected element
        # element_buffer()
        pass

    def handle_hovering(self, element_buffer: ElementBuffer, coordinate_system: CoordinateSystem,
                        user_interface: UserInterface):
        for element in element_buffer:
            element.hovered = element.is_hovered(self.mouse_position, coordinate_system)

        if user_interface.showing:
            for ui_element in user_interface.ui_elements:
                if isinstance(ui_element, UIText):
                    if ui_element.associated_element:
                        if ui_element.rect.collidepoint(self.mouse_position):
                            ui_element.associated_element.hovered = True

    def handle_actions(self, element_buffer: ElementBuffer):
        for action in self.actions:
            if action == Action.ADD_TRANSFORM:
                element_buffer.transforms.append(Transform())
