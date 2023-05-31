import enum
from typing import List, Optional

import pygame as pg

from elements import Element, Transform, ElementBuffer, Transformed


class UserInterface:
    def __init__(self):
        self.showing = False
        self.menu_rect = pg.Rect(10, 10, 40, 40)
        self.menu_image = self._create_menu_image()

        self.ui_elements: List[UIElement] = []
        self.ui_rect = pg.Rect(0, 0, 400, pg.display.get_window_size()[1])

        self.scroll_position = 0

    def _create_menu_image(self):
        menu_image = pg.Surface((self.menu_rect.width,  self.menu_rect.height))
        menu_image.fill(pg.Color(0, 0, 0))
        d = 40 // 6
        pg.draw.rect(
            menu_image, pg.Color(140, 140, 140), pg.Rect(0, 0, self.menu_rect.width, self.menu_rect.height),
            border_radius=4
        )
        pg.draw.rect(menu_image, pg.Color(20, 20, 20), pg.Rect(d, d+3, 40-2*d, d-2), border_radius=2)
        pg.draw.rect(menu_image, pg.Color(20, 20, 20), pg.Rect(d, d*3, 40-2*d, d-2), border_radius=2)
        pg.draw.rect(menu_image, pg.Color(20, 20, 20), pg.Rect(d, d*5-3, 40-2*d, d-2), border_radius=2)
        return menu_image

    def toggle(self):
        self.showing = not self.showing

    def recreate_ui_elements(self, element_buffer: ElementBuffer):
        self.ui_rect = pg.Rect(0, 0, 400, pg.display.get_window_size()[1])

        self.ui_elements = []
        element_y_pos = 60 - self.scroll_position

        # Object title
        objects_title = UIText(pg.Rect(10, element_y_pos, 120, 20), 'Objects')
        self.ui_elements.append(objects_title)

        vector_add_button = UIButton(pg.Rect(130, element_y_pos-4, 25, 25), action=ActionType.ADD_VECTOR,
                                     sign=UIButton.Sign.PLUS)
        self.ui_elements.append(vector_add_button)
        element_y_pos += 25

        # Objects
        for element in element_buffer:
            rect = pg.Rect(20, element_y_pos, 180, 20)
            ui_element = UIVector(rect, element)
            self.ui_elements.append(ui_element)
            element_y_pos += 25

        # Transforms Title
        element_y_pos += 10
        transforms_title = UIText(pg.Rect(10, element_y_pos, 120, 20), 'Transforms')
        self.ui_elements.append(transforms_title)

        # Add Button
        transform_add_button = UIButton(pg.Rect(130, element_y_pos-4, 25, 25), action=ActionType.ADD_TRANSFORM,
                                        sign=UIButton.Sign.PLUS)
        self.ui_elements.append(transform_add_button)
        element_y_pos += 30

        # Transform Objects
        for transform in element_buffer.transforms:
            rect = pg.Rect(20, element_y_pos, 180, 50)
            transform_element = UIMatrix(rect, transform)
            self.ui_elements.append(transform_element)
            element_y_pos += 60

        # Transformed Title
        element_y_pos += 10
        transformed_title = UIText(pg.Rect(10, element_y_pos, 120, 20), 'Transformed')
        self.ui_elements.append(transformed_title)

        # Add Button
        transformed_add_button = UIButton(pg.Rect(130, element_y_pos-4, 25, 25), action=ActionType.ADD_TRANSFORMED,
                                          sign=UIButton.Sign.PLUS)
        self.ui_elements.append(transformed_add_button)
        element_y_pos += 30

        # Transformed Objects
        for transform in element_buffer.transformed:
            rect = pg.Rect(20, element_y_pos, 240, 20)
            transform_element = UITransformed(rect, transform)
            self.ui_elements.append(transform_element)
            element_y_pos += 25


@enum.unique
class ActionType(enum.Enum):
    ADD_VECTOR = 0
    ADD_TRANSFORM = 1
    ADD_TRANSFORMED = 2
    PICK_FOR_TRANSFORMED = 3
    PICK_TRANSFORM_VAL = 4


class Action:
    def __init__(self, action_type, data=None):
        super().__init__()
        self.action_type = action_type
        self.data = data


class UIElement:
    def __init__(self, rect):
        self.rect: pg.Rect = rect

    def on_click(self, mouse_position) -> Optional[Action]:
        return None


class UIText(UIElement):
    def __init__(self, rect, text):
        super().__init__(rect)
        self.text = text


class UIVector(UIElement):
    def __init__(self, rect, associated_vector=None):
        super().__init__(rect)
        self.associated_vector: Optional[Element] = associated_vector


class UIMatrix(UIElement):
    def __init__(self, rect, associated_transform):
        super().__init__(rect)
        self.associated_transform: Optional[Transform] = associated_transform

    def on_click(self, mouse_position) -> Optional[Action]:
        small_rect = self.rect.copy()
        small_rect.width = 30
        small_rect.height = 20

        if small_rect.move(80, 3).collidepoint(mouse_position):
            return Action(ActionType.PICK_TRANSFORM_VAL, data={'index': (0, 0), 'transform': self.associated_transform})

        if small_rect.move(130, 3).collidepoint(mouse_position):
            return Action(ActionType.PICK_TRANSFORM_VAL, data={'index': (0, 1), 'transform': self.associated_transform})

        if small_rect.move(80, 27).collidepoint(mouse_position):
            return Action(ActionType.PICK_TRANSFORM_VAL, data={'index': (1, 0), 'transform': self.associated_transform})

        if small_rect.move(130, 27).collidepoint(mouse_position):
            return Action(ActionType.PICK_TRANSFORM_VAL, data={'index': (1, 1), 'transform': self.associated_transform})

        return None


class UITransformed(UIElement):
    def __init__(self, rect, associated_transformed):
        super().__init__(rect)
        self.associated_transformed: Optional[Transformed] = associated_transformed

    def on_click(self, mouse_position) -> Optional[Action]:
        if self.rect.collidepoint(mouse_position):
            return Action(ActionType.PICK_FOR_TRANSFORMED, {'transformed': self.associated_transformed})


class UIButton(UIElement):
    class Sign(enum.Enum):
        PLUS = 0

    def __init__(self, rect, action, sign=None):
        super().__init__(rect)
        self.action = action
        self.sign = sign

    def on_click(self, mouse_position) -> Optional[Action]:
        return Action(self.action)
