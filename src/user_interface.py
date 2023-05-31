import enum
from typing import List, Optional

import pygame as pg

from elements import Element, Transform, ElementBuffer


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
        objects_title = UIText('Objects', pg.Rect(10, element_y_pos, 120, 20))
        self.ui_elements.append(objects_title)
        element_y_pos += 25

        # Objects
        for element in element_buffer:
            rect = pg.Rect(20, element_y_pos, 180, 20)
            ui_element = UIText(repr(element), rect, element)
            self.ui_elements.append(ui_element)
            element_y_pos += 25

        # Transforms Title
        element_y_pos += 10
        transforms_title = UIText('Transforms', pg.Rect(10, element_y_pos, 120, 20))
        self.ui_elements.append(transforms_title)

        # Add Button
        transform_add_button = UIButton(pg.Rect(120, element_y_pos-4, 25, 25), sign=UIButton.Sign.PLUS)
        self.ui_elements.append(transform_add_button)
        element_y_pos += 25

        # Transform Objects
        for transform in element_buffer.transforms:
            rect = pg.Rect(20, element_y_pos, 180, 50)
            transform_element = UIMatrix(rect, transform)
            self.ui_elements.append(transform_element)
            element_y_pos += 60


class Action(enum.Enum):
    ADD_TRANSFORM = 0


class UIElement:
    def __init__(self, rect):
        self.rect: pg.Rect = rect

    def on_click(self):
        return


class UIText(UIElement):
    def __init__(self, text, rect, associated_element=None):
        super().__init__(rect)
        self.text: str = text
        self.associated_element: Optional[Element] = associated_element


class UIMatrix(UIElement):
    def __init__(self, rect, associated_transform):
        super().__init__(rect)
        self.associated_transform: Optional[Transform] = associated_transform

    def on_click(self):
        return


class UIButton(UIElement):
    class Sign(enum.Enum):
        PLUS = 0

    def __init__(self, rect, sign=None):
        super().__init__(rect)
        self.sign = sign

    def on_click(self) -> Action:
        return Action.ADD_TRANSFORM
