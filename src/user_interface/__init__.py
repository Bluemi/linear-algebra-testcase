import enum
from typing import List, Optional, Union

import numpy as np
import pygame as pg
from pygame import Surface, Rect

from elements import Transform2D, ElementBuffer, Transformed, Vector, UnitCircle, CustomTransformed, Transform3D
from user_interface.items import Container, Label, Button, Image, Item, RootContainer, VectorItem, TransformItem
from utils import gray


class UserInterface:
    def __init__(self):
        self.root = RootContainer()
        self.showing = False
        self.menu_rect = Rect(10, 10, 40, 40)

        self.ui_elements: List[UIElement] = []
        self.ui_rect = Rect(0, 0, 400, pg.display.get_window_size()[1])

        self.scroll_position = 0
        self.item_y_position = 0

    def render(self, screen: Surface):
        self.root.render(screen)

    def toggle(self):
        self.showing = not self.showing

    def handle_event(self, event: pg.event.Event, mouse_position: np.ndarray):
        self.root.handle_event(event, mouse_position)
        self.root.handle_every_event(event, mouse_position)

    def recreate_ui_elements(self, element_buffer: ElementBuffer):
        new_root = RootContainer()
        item_container = Container('item_container', Rect(0, 0, 400, pg.display.get_window_size()[1]), color=gray(50), visible=False)
        new_root.add_child(item_container)

        self.item_y_position = 0
        self.add_objects_section(item_container, element_buffer)
        self.add_transforms_section(item_container, element_buffer)
        self.add_menu_button(new_root, item_container)

        # update from old root
        new_root.update_from(self.root)
        self.root = new_root

        return
        self.ui_rect = Rect(0, 0, 400, pg.display.get_window_size()[1])

        self.ui_elements = []
        element_y_pos = 60 - self.scroll_position

        # Object title
        objects_title = UIText(Rect(10, element_y_pos, 120, 20), 'Objects')
        self.ui_elements.append(objects_title)

        vector_add_button = UIButton(Rect(130, element_y_pos-4, 25, 25), action=ActionType.ADD_VECTOR,
                                     sign=UIButton.Sign.PLUS)
        self.ui_elements.append(vector_add_button)

        unit_circle_add_button = UIButton(Rect(160, element_y_pos-4, 25, 25), action=ActionType.ADD_UNIT_CIRCLE,
                                          sign=UIButton.Sign.PLUS)
        self.ui_elements.append(unit_circle_add_button)
        element_y_pos += 25

        # Objects
        for element in element_buffer:
            if isinstance(element, Vector):
                rect = Rect(20, element_y_pos, 180, 20)
                ui_element = UIVector(rect, element)
                self.ui_elements.append(ui_element)
            elif isinstance(element, UnitCircle):
                rect = Rect(20, element_y_pos, 180, 20)
                ui_element = UIUnitCircle(rect, element)
                self.ui_elements.append(ui_element)
            element_y_pos += 25

        # Transforms Title
        element_y_pos += 10
        transforms_title = UIText(Rect(10, element_y_pos, 120, 20), 'Transforms')
        self.ui_elements.append(transforms_title)

        # Add Button
        transform2d_add_button = UIButton(
            Rect(130, element_y_pos-4, 25, 25), action=ActionType.ADD_TRANSFORM2D, sign=UIButton.Sign.PLUS
        )
        self.ui_elements.append(transform2d_add_button)

        transform3d_add_button = UIButton(
            Rect(160, element_y_pos-4, 25, 25), action=ActionType.ADD_TRANSFORM3D, sign=UIButton.Sign.PLUS
        )
        self.ui_elements.append(transform3d_add_button)

        element_y_pos += 30

        # Transform Objects
        for transform in element_buffer.transforms:
            height = 50 if isinstance(transform, Transform2D) else 70
            rect = Rect(20, element_y_pos, 180, height)

            if isinstance(transform, Transform2D):
                transform_element = UITransform2D(rect, transform)
            elif isinstance(transform, Transform3D):
                transform_element = UITransform3D(rect, transform)
            else:
                raise TypeError('transform neither Transform2D nor Transform3D')
            self.ui_elements.append(transform_element)
            element_y_pos += height + 10

        # Transformed Title
        element_y_pos += 10
        transformed_title = UIText(Rect(10, element_y_pos, 120, 20), 'Transformed')
        self.ui_elements.append(transformed_title)

        # Add Button
        transformed_add_button = UIButton(Rect(130, element_y_pos-4, 25, 25), action=ActionType.ADD_TRANSFORMED,
                                          sign=UIButton.Sign.PLUS)
        self.ui_elements.append(transformed_add_button)

        # Add Button - Custom Transformed
        transformed_add_button = UIButton(Rect(160, element_y_pos-4, 25, 25),
                                          action=ActionType.ADD_CUSTOM_TRANSFORMED, sign=UIButton.Sign.PLUS)
        self.ui_elements.append(transformed_add_button)
        element_y_pos += 30

        # Transformed Objects
        for transform in element_buffer.transformed:
            rect = Rect(20, element_y_pos, 240, 20)
            transform_element = UITransformed(rect, transform)
            self.ui_elements.append(transform_element)
            element_y_pos += 25

    @staticmethod
    def add_menu_button(new_root, item_container):
        menu_button = Button('menu_button', (10, 10),
                             label=Image('menu_button_label', (0, 0), Button.create_menu_image()))

        def menu_button_on_click():
            item_container.visible = not item_container.visible

        menu_button.on_click = menu_button_on_click
        new_root.add_child(menu_button)

    def add_objects_section(self, item_container, element_buffer: ElementBuffer):
        objects_label = Label('objects_label', (10, 60), 'Objects')
        item_container.add_child(objects_label)

        # add vec button
        add_vec_button = Button(
            'add_vec_btn', (objects_label.rect.width + 20, 58),
            label=Image('add_vec_btn_label', (0, 0), Button.create_plus_image())
        )
        def add_vec():
            num_elements = len(element_buffer.elements) + 1
            element_buffer.elements.append(Vector('v{}'.format(num_elements), np.array([1.0, 0.0])))
        add_vec_button.on_click = add_vec
        item_container.add_child(add_vec_button)

        # add circle button
        add_circle_button = Button(
            'add_circle_btn', (objects_label.rect.width + 50, 58),
            label=Image('add_circle_btn_label', (0, 0), Button.create_plus_image())
        )
        def add_circle():
            num_elements = len(element_buffer.elements) + 1
            element_buffer.elements.append(UnitCircle('u{}'.format(num_elements)))
        add_circle_button.on_click = add_circle
        item_container.add_child(add_circle_button)

        # add object elements
        self.item_y_position = 90
        for element in element_buffer.elements:
            if isinstance(element, Vector):
                vector_item = VectorItem(element.name + '_ui', (10, self.item_y_position), element)
                item_container.add_child(vector_item)
                self.item_y_position += vector_item.rect.height + 1
            elif isinstance(element, UnitCircle):
                object_item = Label(element.name + '_ui', (20, self.item_y_position), element.name + '   UnitCircle')
                item_container.add_child(object_item)
                self.item_y_position += object_item.rect.height + 1

    def add_transforms_section(self, item_container, element_buffer: ElementBuffer):
        self.item_y_position += 10
        transforms_label = Label('transforms_label', (10, self.item_y_position), 'Transforms')
        item_container.add_child(transforms_label)

        # add 2d transform button
        add_2d_transform_button = Button(
            'add_2d_transform_btn', (transforms_label.rect.width + 20, self.item_y_position - 2),
            label=Image('add_2d_transform_btn_label', (0, 0), Button.create_plus_image())
        )
        def add_2d_transform():
            num_transforms = len(element_buffer.transforms) + 1
            element_buffer.transforms.append(Transform2D('T{}'.format(num_transforms)))
        add_2d_transform_button.on_click = add_2d_transform
        item_container.add_child(add_2d_transform_button)

        # add 3d transform button
        add_3d_transform_button = Button(
            'add_3d_transform_btn', (transforms_label.rect.width + 50, self.item_y_position - 2),
            label=Image('add_3d_transform_btn_label', (0, 0), Button.create_plus_image())
        )
        def add_3d_transform():
            num_transforms = len(element_buffer.transforms) + 1
            element_buffer.transforms.append(Transform3D('T{}'.format(num_transforms)))
        add_3d_transform_button.on_click = add_3d_transform
        item_container.add_child(add_3d_transform_button)

        self.item_y_position += transforms_label.rect.height + 10

        for transform in element_buffer.transforms:
            transform_item = TransformItem(transform.name + '_ui', (10, self.item_y_position), transform)
            item_container.add_child(transform_item)
            self.item_y_position += transform_item.rect.height + 1


@enum.unique
class ActionType(enum.Enum):
    ADD_VECTOR = 0
    ADD_UNIT_CIRCLE = 1
    ADD_TRANSFORM2D = 2
    ADD_TRANSFORM3D = 3
    ADD_TRANSFORMED = 4
    ADD_CUSTOM_TRANSFORMED = 5
    PICK_FOR_TRANSFORMED = 6
    PICK_TRANSFORM_VAL = 7


class Action:
    def __init__(self, action_type, data=None):
        super().__init__()
        self.action_type = action_type
        self.data = data


class UIElement:
    def __init__(self, rect):
        self.rect: Rect = rect

    def on_click(self, mouse_position) -> Optional[Action]:
        return None

    def toggle_render_kind(self):
        pass


class UIText(UIElement):
    def __init__(self, rect, text):
        super().__init__(rect)
        self.text = text


class UIVector(UIElement):
    def __init__(self, rect, associated_vector=None):
        super().__init__(rect)
        self.associated_vector: Optional[Vector] = associated_vector

    def toggle_render_kind(self):
        self.associated_vector.render_kind = self.associated_vector.render_kind.toggle()


class UIUnitCircle(UIElement):
    def __init__(self, rect, associated_unit_circle=None):
        super().__init__(rect)
        self.associated_unit_circle: Optional[UnitCircle] = associated_unit_circle

    def toggle_render_kind(self):
        self.associated_unit_circle.render_kind = self.associated_unit_circle.render_kind.toggle()


class UITransform2D(UIElement):
    def __init__(self, rect, associated_transform):
        super().__init__(rect)
        self.associated_transform: Optional[Transform2D] = associated_transform

    def on_click(self, mouse_position) -> Optional[Action]:
        small_rect = self.rect.copy()
        small_rect.width = 30
        small_rect.height = 20

        matrix = self.associated_transform.matrix
        for y in range(matrix.shape[0]):
            for x in range(matrix.shape[1]):
                if small_rect.move(40 + 50*x, 3 + 24 * y).collidepoint(mouse_position):
                    return Action(
                        ActionType.PICK_TRANSFORM_VAL, data={'index': (y, x), 'transform': self.associated_transform}
                    )

        return None


class UITransform3D(UIElement):
    def __init__(self, rect, associated_transform):
        super().__init__(rect)
        self.associated_transform: Optional[Transform3D] = associated_transform

    def on_click(self, mouse_position) -> Optional[Action]:
        small_rect = self.rect.copy()
        small_rect.width = 30
        small_rect.height = 20

        matrix = self.associated_transform.matrix
        for y in range(matrix.shape[0]):
            for x in range(matrix.shape[1]):
                if small_rect.move(40 + 50*x, 3 + 24 * y).collidepoint(mouse_position):
                    return Action(
                        ActionType.PICK_TRANSFORM_VAL, data={'index': (y, x), 'transform': self.associated_transform}
                    )

        return None


class UITransformed(UIElement):
    def __init__(self, rect, associated_transformed):
        super().__init__(rect)
        self.associated_transformed: Optional[Union[Transformed, CustomTransformed]] = associated_transformed

    def on_click(self, mouse_position) -> Optional[Action]:
        if self.rect.collidepoint(mouse_position):
            if isinstance(self.associated_transformed, Transformed):
                return Action(ActionType.PICK_FOR_TRANSFORMED, {'transformed': self.associated_transformed})

    def toggle_render_kind(self):
        self.associated_transformed.render_kind = self.associated_transformed.render_kind.toggle()


class UIButton(UIElement):
    class Sign(enum.Enum):
        PLUS = 0

    def __init__(self, rect, action, sign=None):
        super().__init__(rect)
        self.action = action
        self.sign = sign

    def on_click(self, mouse_position) -> Optional[Action]:
        return Action(self.action)
