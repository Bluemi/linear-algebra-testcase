from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Union, Callable

import numpy as np
import pygame as pg
from pygame import Surface, Rect

from utils import gray


class Item(ABC):
    def __init__(self, rect: Rect, visible: bool = True):
        """
        Initiate a new item.
        :param rect: The rect of this item, relative to the containing element.
        :param visible: Whether this element should be visible or not.
        """
        self.rect: Rect = rect
        self.visible: bool = visible

    @abstractmethod
    def handle_event(self, event: pg.event.Event, rel_mouse_position: np.ndarray):
        """
        Function that a subclass can overwrite to handle given events.

        :param event: The pygame event to handle
        :param rel_mouse_position: The mouse position relative to this element as (x, y).
        """
        pass

    @abstractmethod
    def render(self, surface: Surface):
        """
        Renders this item on the given surface.

        :param surface: The surface to render on
        """
        pass


class ItemContainer(Item):
    def __init__(self, rect: Rect, visible: bool = True, child_items: Optional[Item] = None):
        super().__init__(rect, visible)
        self.child_items: List[Item] = child_items if child_items is not None else []
        self.scroll_position = 0

    def handle_event(self, event: pg.event.Event, rel_mouse_position: np.ndarray):
        """
        Forwards all events to the child items of this container, if they collide with the mouse position.

        :param event: The pygame event to forward
        :param rel_mouse_position: The mouse position relative to this element as (x, y).
        """
        for item in self.child_items:
            item_rel_mouse_position = rel_mouse_position - np.array([item.rect.left, item.rect.top])
            if item.rect.collidepoint(rel_mouse_position):
                item.handle_event(event, item_rel_mouse_position)

    def render(self, surface: Surface):
        """
        This item should not be rendered directly
        :param surface:
        """
        raise AssertionError('Do not render ItemContainer directly')

    def render_child_items(self, surface: Surface):
        """
        Renders this item on the given surface as well as all sub items.
        This function should be called after the container is rendered itself.

        :param surface: The surface to render on
        """
        if not self.visible:
            return
        subsurface = surface.subsurface(self.rect)
        for item in self.child_items:
            if item.visible:
                item.render(subsurface)

    def add_child(self, child: Item):
        self.child_items.append(child)


class Container(ItemContainer):
    def __init__(self, rect: Rect, color: Optional[pg.Color] = None, visible: bool = True, child_items: Optional[Item] = None):
        super().__init__(rect, visible, child_items)
        self.color = color if color is not None else gray(42)

    def render(self, surface: Surface):
        pg.draw.rect(surface, self.color, self.rect)
        self.render_child_items(surface)


class Label(Item):
    def __init__(self, position: Union[np.ndarray or Tuple[int, int]], text: str, fontsize: int = 18, text_color: pg.Color = None, font_name: str = '', visible: bool = True):
        """
        Initiate a new item.
        :param position: The position where the label should be located (x, y).
        :param text: The text to display
        :param fontsize: The size of the font to draw
        :param text_color: The color of the text
        :param font_name: The name of the font to use. When empty string is supplied the default system font is used.
        :param visible: Whether this element should be visible or not.
        """
        # The width and height of the rect will be determined automatically, when the font is rendered.
        super().__init__(Rect(position[0], position[1], 1, 1), visible)
        self.text = text
        self.fontsize = fontsize
        self.text_color = text_color if text_color is not None else gray(220)
        self.font_name = font_name if font_name else pg.font.get_default_font()
        self.font = pg.font.Font(self.font_name, self.fontsize)
        self.rendered_font = None
        self.render_font()

    def handle_event(self, event: pg.event.Event, rel_mouse_position: np.ndarray):
        """
        Do not handle events.
        """
        if event.type == pg.MOUSEBUTTONDOWN:
            print('label clicked!')

    def render_font(self):
        if self.rendered_font:
            return
        self.rendered_font = self.font.render(self.text, True, self.text_color)
        self.rect.width = self.rendered_font.get_width()
        self.rect.height = self.rendered_font.get_height()

    def render(self, surface: Surface):
        self.render_font()
        surface.blit(self.rendered_font, self.rect)


class Image(Item):
    def __init__(self, rect: Union[Rect, np.ndarray, Tuple[int, int]], image: Surface):
        """
        Creates an image object, that can be used as menu item.

        :param rect: The rect where the image should be located. If only a position is supplied the width and height
                     will be determined by the width and height of the supplied image.
        :param image: The image to draw
        """
        if not isinstance(rect, Rect):
            rect = Rect(rect[0], rect[1], image.get_width(), image.get_height())
        super().__init__(rect)
        self.image = image

    def handle_event(self, event: pg.event.Event, rel_mouse_position: np.ndarray):
        if event.type == pg.MOUSEBUTTONDOWN:
            print('image clicked!')

    def render(self, surface: Surface):
        surface.blit(self.image, self.rect)


class Button(Item):
    @staticmethod
    def create_menu_image():
        menu_rect = pg.Rect(10, 10, 40, 40)
        menu_image = pg.Surface((menu_rect.width, menu_rect.height))
        menu_image.fill(pg.Color(0, 0, 0))
        d = 40 // 6
        pg.draw.rect(
            menu_image, pg.Color(140, 140, 140), Rect(0, 0, menu_rect.width, menu_rect.height),
            border_radius=4
        )
        pg.draw.rect(menu_image, pg.Color(20, 20, 20), Rect(d, d+3, 40-2*d, d-2), border_radius=2)
        pg.draw.rect(menu_image, pg.Color(20, 20, 20), Rect(d, d*3, 40-2*d, d-2), border_radius=2)
        pg.draw.rect(menu_image, pg.Color(20, 20, 20), Rect(d, d*5-3, 40-2*d, d-2), border_radius=2)
        return menu_image

    def __init__(self, rect: Union[Rect, np.ndarray, Tuple[int, int]], color: Optional[pg.Color] = None,
                 label: Union[None, Label, Image] = None, visible: bool = True):
        """
        Initiate a new item.
        :param rect: The rect of this item, relative to the containing element. If width or height is set to zero or if
                     only a position is supplied, the width and height are determined by the label. If label is not
                     supplied, an error is raised.
        :param color: The background color of the button.
        :param label: The label to display. Will be centered on the button
        :param visible: Whether this element should be visible or not.
        """
        # handle rect
        if not isinstance(rect, Rect):
            rect = Rect(rect[0], rect[1], 0, 0)
        if rect.width == 0:
            if isinstance(label, Image) or isinstance(label, Label):
                rect.width = label.rect.width
            else:
                raise ValueError('Failed to determine Button width from label.')
        if rect.height == 0:
            if isinstance(label, Image) or isinstance(label, Label):
                rect.height = label.rect.height
            else:
                raise ValueError('Failed to determine Button height from label.')
        super().__init__(rect, visible)
        self.color = color if color is not None else gray(80)
        self.label = label

    def handle_event(self, event: pg.event.Event, rel_mouse_position: np.ndarray):
        """
        Do not handle events.
        """
        if event.type == pg.MOUSEBUTTONDOWN:
            print('button clicked!')

    def render(self, surface: Surface):
        pg.draw.rect(surface, self.color, self.rect)
        if self.label:
            sub_surface = surface.subsurface(self.rect)
            self.label.render(sub_surface)