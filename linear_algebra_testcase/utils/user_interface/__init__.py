from typing import Optional

import numpy as np
import pygame as pg
from pygame import Surface, Rect

from linear_algebra_testcase.dim2.elements import (Transform2D, ElementBuffer, Transformed, Vector, MultiVectorObject,
                                                   CustomTransformed, Transform3D, RenderKind)
from ..user_interface.items import (Container, Label, Button, Image, RootContainer, VectorItem, TransformItem,
                                    ElementLabel)
from ..user_interface.window import Window
from linear_algebra_testcase.utils import Colors


class UserInterface:
    def __init__(self):
        self.root = RootContainer()
        self.menu_rect = Rect(10, 10, 40, 40)

        self.ui_rect = Rect(0, 0, 400, pg.display.get_window_size()[1])

        self.item_y_position = 0

        self.choosing_for_transformed: Optional[Transformed] = None
        self.text_input_window: Optional[Window] = None

    def render(self, screen: Surface):
        self.root.render(screen)
        if self.text_input_window:
            self.text_input_window.render(screen)

    def handle_event(self, event: pg.event.Event, mouse_position: np.ndarray):
        """
        Handles the given event.

        :param event: The event to handle.
        :param mouse_position: The absolute mouse position
        """
        if self.text_input_window:
            self.text_input_window.handle_event(event)
            if self.text_input_window.has_to_close:
                self.text_input_window = None
        else:
            self.root.handle_event(event, mouse_position)
            self.root.handle_every_event(event, mouse_position)
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    item_container = self.root.get_item_by_name('item_container')
                    assert item_container is not None, 'Item Container is None, but should always be present'
                    item_container.visible = not item_container.visible

    def consuming_events(self, position: np.ndarray):
        return self.root.colliding(position) or bool(self.text_input_window)

    def build(self, element_buffer: ElementBuffer):
        new_root = RootContainer()
        item_container = Container(
            'item_container', Rect(0, 0, 400, pg.display.get_window_size()[1]), color=Colors.BACKGROUND, visible=False
        )
        new_root.add_child(item_container)

        self.item_y_position = 0
        self.add_objects_section(item_container, element_buffer)
        self.add_transforms_section(item_container, element_buffer)
        self.add_transformed_section(item_container, element_buffer)
        self.add_menu_button(new_root, item_container)

        # update from old root
        new_root.update_from(self.root)
        self.root = new_root

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
            obj = MultiVectorObject('u{}'.format(num_elements), MultiVectorObject.generate_unit_circle(40))
            element_buffer.elements.append(obj)
        add_circle_button.on_click = add_circle
        item_container.add_child(add_circle_button)

        # add house button
        add_house_button = Button(
            'add_house_btn', (objects_label.rect.width + 80, 58),
            label=Image('add_house_btn_label', (0, 0), Button.create_plus_image())
        )

        def add_house():
            num_elements = len(element_buffer.elements) + 1
            obj = MultiVectorObject('h{}'.format(num_elements), MultiVectorObject.generate_house())
            element_buffer.elements.append(obj)
        add_house_button.on_click = add_house
        item_container.add_child(add_house_button)

        # add object elements
        self.item_y_position = 90
        for element in element_buffer.elements:
            if isinstance(element, Vector):
                self._create_vector(element, item_container)
            elif isinstance(element, MultiVectorObject):
                self._create_multiobject(element, item_container)

    def _create_multiobject(self, element, item_container):
        text_color = Colors.ACTIVE if element.visible else Colors.INACTIVE
        object_item = ElementLabel(
            element.name + '_ui', (20, self.item_y_position), element.name + '   Object', element,
            text_color=text_color
        )

        def set_multiobject_for_transformed():
            if self.choosing_for_transformed:
                self.choosing_for_transformed.element = element
                self.choosing_for_transformed = None

        object_item.on_click = set_multiobject_for_transformed
        item_container.add_child(object_item)
        self.item_y_position += object_item.rect.height + 1

    def _create_vector(self, element, item_container):
        text_color = Colors.ACTIVE if element.visible else Colors.INACTIVE
        vector_item = VectorItem(element.name + '_ui', (10, self.item_y_position), element, text_color=text_color)
        item_container.add_child(vector_item)

        def set_vector_for_transformed():
            if self.choosing_for_transformed:
                self.choosing_for_transformed.element = element
                self.choosing_for_transformed = None

        vector_item.on_click = set_vector_for_transformed
        self.item_y_position += vector_item.rect.height + 1

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
            self._create_transform(item_container, transform)

    def _create_transform(self, item_container, transform):
        transform_item = TransformItem(transform.name + '_ui', (10, self.item_y_position), transform)

        def set_transform_for_transformed():
            if self.choosing_for_transformed:
                self.choosing_for_transformed.transform = transform
                self.choosing_for_transformed = None

        transform_item.on_click = set_transform_for_transformed
        item_container.add_child(transform_item)
        self.item_y_position += transform_item.rect.height + 1

    def add_transformed_section(self, item_container, element_buffer: ElementBuffer):
        self.item_y_position += 10
        transformed_label = Label('transformed_label', (10, self.item_y_position), 'Transformed')
        item_container.add_child(transformed_label)

        # add transformed button
        add_transformed_button = Button(
            'add_transformed_btn', (transformed_label.rect.width + 20, self.item_y_position - 2),
            label=Image('add_transformed_btn_label', (0, 0), Button.create_plus_image())
        )

        def add_transformed():
            num_transformed = len(element_buffer.transformed) + 1
            element_buffer.transformed.append(
                Transformed('t{}'.format(num_transformed), None, None, render_kind=RenderKind.LINE)
            )
        add_transformed_button.on_click = add_transformed
        item_container.add_child(add_transformed_button)

        # add custom transformed button
        add_custom_transformed_button = Button(
            'add_custom_transform_btn', (transformed_label.rect.width + 50, self.item_y_position - 2),
            label=Image('add_custom_transform_btn_label', (0, 0), Button.create_plus_image())
        )

        def add_custom_transformed():
            num_transformed = len(element_buffer.transformed) + 1
            custom_transformed = CustomTransformed('t{}'.format(num_transformed), RenderKind.LINE, element_buffer)
            element_buffer.transformed.append(custom_transformed)
        add_custom_transformed_button.on_click = add_custom_transformed
        item_container.add_child(add_custom_transformed_button)

        self.item_y_position += transformed_label.rect.height + 10

        for transformed in element_buffer.transformed:
            if isinstance(transformed, Transformed):
                self._create_transformed(item_container, transformed)
            elif isinstance(transformed, CustomTransformed):
                self._create_custom_transformed(item_container, transformed)

    def _create_transformed(self, item_container, transformed):
        transform_str = transformed.transform.name if transformed.transform is not None else '< >'
        element_str = transformed.element.name if transformed.element is not None else '< >'
        text_color = Colors.ACTIVE if transformed.visible else Colors.INACTIVE
        transformed_item = ElementLabel(
            transformed.name + '_ui', (10, self.item_y_position),
            '{} = {} @ {}'.format(transformed.name, transform_str, element_str), transformed, text_color=text_color
        )

        def transformed_label_on_click():
            self.choosing_for_transformed = transformed

        transformed_item.on_click = transformed_label_on_click
        item_container.add_child(transformed_item)
        self.item_y_position += transformed_item.rect.height + 1

    def _create_custom_transformed(self, item_container, transformed):
        text = transformed.name
        if transformed.definition:
            text += ' = ' + transformed.definition
            if transformed.error:
                text += ' [Err]:' + transformed.error
        else:
            text += ' = < >'
        text_color = Colors.ACTIVE if transformed.visible else Colors.INACTIVE
        transformed_item = ElementLabel(
            transformed.name + '_ui', (10, self.item_y_position), text, transformed, text_color=text_color
        )

        def start_custom_transform_text_input():
            def text_window_on_close(window_text):
                transformed.set_definition(window_text)
                transformed.compile_definition()
            self.text_input_window = Window(text_window_on_close, transformed.definition)

        transformed_item.on_click = start_custom_transform_text_input
        item_container.add_child(transformed_item)
        self.item_y_position += transformed_item.rect.height + 1
