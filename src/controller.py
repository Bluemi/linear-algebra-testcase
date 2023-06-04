from typing import Optional

import numpy as np
import pygame as pg

from coordinate_system import CoordinateSystem
from elements import ElementBuffer, Element, Transform, Transformed, Vector, UnitCircle, CustomTransformed
from user_interface import UserInterface, ActionType, UIVector, Action, UIMatrix, UIUnitCircle, UITransformed


class Controller:
    def __init__(self):
        self.running = True
        self.update_needed = True
        self.is_dragging = False
        self.dragged_element: Element or None = None
        self.mouse_position = np.array(pg.mouse.get_pos(), dtype=int)
        self.actions = []

        self.selected_transformed: Optional[Transformed] = None
        self.selected_transform: Optional = None
        self.get_definition_for: Optional = None

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
                            # handle select transform
                            if self.selected_transformed:
                                if isinstance(ui_element, UIVector):
                                    self.selected_transformed.element = ui_element.associated_vector
                                    self.selected_transformed = None
                                    self.update_needed = True
                                elif isinstance(ui_element, UIUnitCircle):
                                    self.selected_transformed.element = ui_element.associated_unit_circle
                                    self.selected_transformed = None
                                    self.update_needed = True
                                elif isinstance(ui_element, UIMatrix):
                                    self.selected_transformed.transform = ui_element.associated_transform
                                    self.selected_transformed = None
                                    self.update_needed = True
                            if isinstance(ui_element, UITransformed):
                                if isinstance(ui_element.associated_transformed, CustomTransformed):
                                    self.get_definition_for = ui_element
                                    self.update_needed = True
                            # handle on click
                            action = ui_element.on_click(self.mouse_position)
                            if action is not None:
                                self.actions.append(action)
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
            self.selected_transform = None
        elif event.type == pg.MOUSEMOTION:
            if self.is_dragging:
                coordinate_system.translate(np.array(event.rel))
            if self.dragged_element:
                pos = coordinate_system.transform_inverse(np.array(event.pos))
                self.dragged_element.move_to(pos)
            if self.selected_transform is not None:
                transform = self.selected_transform['transform']
                index = self.selected_transform['index']
                transform.matrix[index] -= event.rel[1] * 0.01
            self.mouse_position = np.array(event.pos, dtype=int)
            self.update_needed = True
        elif event.type == pg.WINDOWENTER or event.type == pg.WINDOWFOCUSGAINED:
            self.update_needed = True
        elif event.type == pg.KEYUP:
            if self.get_definition_for is not None:
                if event.key == 27:
                    # self.running = False
                    self.get_definition_for.associated_transformed.compile_definition()
                    self.get_definition_for = None
                    self.update_needed = True
                else:
                    custom_transformed: CustomTransformed = self.get_definition_for.associated_transformed
                    if event.key == 8:
                        custom_transformed.set_definition(custom_transformed.definition[:-1])
                    elif event.key == 127:
                        custom_transformed.set_definition('')
                    elif event.unicode:
                        custom_transformed.set_definition(custom_transformed.definition + event.unicode)
                    self.update_needed = True
            else:
                if event.unicode == 'n':
                    # element_buffer.generate_transform(default=False)
                    self.update_needed = True
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
                if isinstance(ui_element, UIVector):
                    if ui_element.associated_vector:
                        if ui_element.rect.collidepoint(self.mouse_position):
                            ui_element.associated_vector.hovered = True
                if isinstance(ui_element, UIUnitCircle):
                    if ui_element.associated_unit_circle:
                        if ui_element.rect.collidepoint(self.mouse_position):
                            ui_element.associated_unit_circle.hovered = True

    def handle_actions(self, element_buffer: ElementBuffer):
        for action in self.actions:
            num_elements = len(element_buffer.elements) + 1
            num_transformed = len(element_buffer.transformed) + 1
            num_transforms = len(element_buffer.transforms) + 1
            if action.action_type == ActionType.ADD_VECTOR:
                element_buffer.elements.append(Vector('v{}'.format(num_elements), np.array([1, 0])))
                self.update_needed = True
            elif action.action_type == ActionType.ADD_UNIT_CIRCLE:
                element_buffer.elements.append(UnitCircle('u{}'.format(num_elements)))
                self.update_needed = True
            elif action.action_type == ActionType.ADD_TRANSFORM:
                element_buffer.transforms.append(Transform('T{}'.format(num_transforms)))
                self.update_needed = True
            elif action.action_type == ActionType.ADD_TRANSFORMED:
                element_buffer.transformed.append(Transformed('t{}'.format(num_transformed), None, None))
                self.update_needed = True
            elif action.action_type == ActionType.ADD_CUSTOM_TRANSFORMED:
                element_buffer.transformed.append(CustomTransformed('t{}'.format(num_transformed)))
                self.update_needed = True
            elif action.action_type == ActionType.PICK_FOR_TRANSFORMED:
                self.selected_transformed = action.data['transformed']
                self.update_needed = True
            elif action.action_type == ActionType.PICK_TRANSFORM_VAL:
                self.selected_transform = action.data
                self.update_needed = True
