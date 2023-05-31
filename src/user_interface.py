from typing import List, Optional

import pygame as pg

from elements import Element


class UserInterface:
    def __init__(self):
        self.showing = False
        self.menu_rect = pg.Rect(10, 10, 40, 40)
        self.menu_image = self._create_menu_image()

        self.ui_rect = pg.Rect(0, 0, 400, pg.display.get_window_size()[1])
        self.ui_elements: List[UIElement] = []

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

    def recreate_ui_elements(self, element_buffer):
        self.ui_elements = []
        element_y_pos = 60

        # Object title
        objects_title = UIElement('Objects', pg.Rect(10, element_y_pos, 120, 20))
        self.ui_elements.append(objects_title)
        element_y_pos += 25

        # Objects
        for element in element_buffer:
            rect = pg.Rect(20, element_y_pos, 180, 20)
            ui_element = UIElement(repr(element), rect, element)
            self.ui_elements.append(ui_element)
            element_y_pos += 25


class UIElement:
    def __init__(self, text, rect, associated_element=None):
        self.text: str = text
        self.rect: pg.Rect = rect
        self.associated_element: Optional[Element] = associated_element
