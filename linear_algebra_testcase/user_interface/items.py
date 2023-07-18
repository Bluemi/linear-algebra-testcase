from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Union, Callable

import numpy as np
import pygame as pg
from pygame import Surface, Rect

from linear_algebra_testcase.elements import Vector, Transform2D, Transform3D, Element
from linear_algebra_testcase.utils import gray, format_float, noop, Colors


class Item(ABC):
    def __init__(self, name: str, rect: Rect, visible: bool = True):
        """
        Initiate a new item.
        :param rect: The rect of this item, relative to the containing element.
        :param visible: Whether this element should be visible or not.
        """
        self.name: str = name
        self.rect: Rect = rect
        self.visible: bool = visible
        self.hovered: bool = False
        self.on_click: Callable = noop
        self.on_mouse_enter: Callable = noop
        self.on_mouse_leave: Callable = noop

    def handle_event(self, event: pg.event.Event, rel_mouse_position: np.ndarray):
        """
        Function that a subclass can overwrite to handle given events.

        :param event: The pygame event to handle
        :param rel_mouse_position: The mouse position relative to this element as (x, y).
        """
        if self.visible:
            if event.type == pg.MOUSEBUTTONDOWN:
                self.on_click()

    def handle_every_event(self, event: pg.event.Event, rel_mouse_position: np.ndarray):
        """
        Function that a subclass can overwrite to handle given events. Every event is reaching this position.

        :param event: The pygame event to handle
        :param rel_mouse_position: The mouse position relative to this element as (x, y).
        """
        if self.visible:
            if event.type == pg.MOUSEMOTION:
                rect = self.rect.copy()
                rect.topleft = (0, 0)
                hovered = rect.collidepoint(rel_mouse_position)
                if self.hovered and not hovered:
                    self.on_mouse_leave()
                if not self.hovered and hovered:
                    self.on_mouse_enter()
                self.hovered = hovered

    @abstractmethod
    def render(self, surface: Surface):
        """
        Renders this item on the given surface.

        :param surface: The surface to render on
        """
        pass

    def update_from(self, other):
        """
        Update values from other to myself. Should be overwritten by subclasses.
        :param other: The other item to transfer values from
        :type other: Item
        """
        self.visible = other.visible
        self.hovered = other.hovered


class ItemContainer(Item):
    def __init__(self, name: str, rect: Rect, visible: bool = True, child_items: Optional[List[Item]] = None):
        super().__init__(name, rect, visible)
        self.child_items: List[Item] = child_items if child_items is not None else []
        self.scroll_position = 0

    def handle_event(self, event: pg.event.Event, rel_mouse_position: np.ndarray):
        """
        Forwards all events to the child items of this container, if they collide with the mouse position.

        :param event: The pygame event to forward
        :param rel_mouse_position: The mouse position relative to this element as (x, y).
        """
        if self.visible:
            super().handle_event(event, rel_mouse_position)
            for item in self.child_items:
                item_rel_mouse_position = rel_mouse_position - np.array([item.rect.left, item.rect.top])
                if item.rect.collidepoint(rel_mouse_position):
                    item.handle_event(event, item_rel_mouse_position)

    def handle_every_event(self, event: pg.event.Event, rel_mouse_position: np.ndarray):
        """
        Function that a subclass can overwrite to handle given events. Every event is reaching this position.

        :param event: The pygame event to handle
        :param rel_mouse_position: The mouse position relative to this element as (x, y).
        """
        if self.visible:
            super().handle_every_event(event, rel_mouse_position)
            for item in self.child_items:
                item_rel_mouse_position = rel_mouse_position - np.array([item.rect.left, item.rect.top])
                item.handle_every_event(event, item_rel_mouse_position)

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
        subsurface_rect = self.rect.clip(surface.get_rect())
        subsurface = surface.subsurface(subsurface_rect)
        for item in self.child_items:
            if item.visible:
                item.render(subsurface)

    def add_child(self, child: Item):
        self.child_items.append(child)

    def update_from(self, other):
        """
        Update values from other to myself. Should be overwritten by subclasses.
        :param other: The other item to transfer values from
        :type other: ItemContainer
        """
        super().update_from(other)
        self.scroll_position = other.scroll_position
        for child in self.child_items:
            for other_child in other.child_items:
                if child.name == other_child.name:
                    child.update_from(other_child)

    def get_item_by_name(self, name: str) -> Optional[Item]:
        """
        Searches recursively for an item with the given name and returns it.

        :param name: The name of the item.
        :return: An item with the given name or None
        """
        if self.name == name:
            return self
        for c in self.child_items:
            if c.name == name:
                return c
            if isinstance(c, ItemContainer):
                item = c.get_item_by_name(name)
                if item is not None:
                    return item
        return None


class Container(ItemContainer):
    def __init__(self, name: str, rect: Rect, color: Optional[pg.Color] = None, visible: bool = True,
                 child_items: Optional[List[Item]] = None):
        super().__init__(name, rect, visible, child_items)
        self.color = color if color is not None else Colors.BACKGROUND

    def render(self, surface: Surface):
        pg.draw.rect(surface, self.color, self.rect)
        self.render_child_items(surface)

    def update_from(self, other):
        """
        Update values from other to myself. Should be overwritten by subclasses.
        :param other: The other item to transfer values from
        :type other: Container
        """
        super().update_from(other)


class RootContainer(ItemContainer):
    def __init__(self):
        super().__init__('root', Rect(0, 0, 0, 0))

    def render(self, surface: Surface):
        self.rect.width = surface.get_width()
        self.rect.height = surface.get_height()
        self.render_child_items(surface)

    def update_from(self, other):
        """
        Update values from other to myself. Should be overwritten by subclasses.
        :param other: The other item to transfer values from
        :type other: RootContainer
        """
        super().update_from(other)

    def colliding(self, position: np.ndarray):
        """
        Checks whether a child is colliding with the given position.
        :param position: The position to check (x, y).
        """
        if not self.visible:
            return False
        for c in self.child_items:
            if c.visible and c.rect.collidepoint(position):
                return True
        return False


class Label(Item):
    def __init__(self, name: str, position: Union[np.ndarray, Tuple[int, int]], text: str, fontsize: int = 18,
                 text_color: pg.Color = None, font_name: str = '', visible: bool = True):
        """
        Initiate a new item.
        :param name: The name of this item
        :param position: The position where the label should be located (x, y).
        :param text: The text to display
        :param fontsize: The size of the font to draw
        :param text_color: The color of the text
        :param font_name: The name of the font to use. When empty string is supplied the default system font is used.
        :param visible: Whether this element should be visible or not.
        """
        # The width and height of the rect will be determined automatically, when the font is rendered.
        super().__init__(name, Rect(position[0], position[1], 1, 1), visible)
        self.text = text
        self.fontsize = fontsize
        self.text_color = text_color if text_color is not None else Colors.ACTIVE
        self.font_name = font_name if font_name else pg.font.get_default_font()
        self.font = pg.font.Font(self.font_name, self.fontsize)
        self.rendered_font = None
        self.render_font()

    def render_font(self):
        if self.rendered_font:
            return
        self.rendered_font = self.font.render(self.text, True, self.text_color)
        self.rect.width = self.rendered_font.get_width()
        self.rect.height = self.rendered_font.get_height()

    def render(self, surface: Surface):
        self.render_font()
        surface.blit(self.rendered_font, self.rect)

    def update_from(self, other):
        """
        Update values from other to myself. Should be overwritten by subclasses.
        :param other: The other item to transfer values from
        :type other: Label
        """
        super().update_from(other)
        if (self.text != other.text or self.fontsize != other.fontsize or self.text_color != other.text_color or
                self.font_name != other.font_name):
            self.font = pg.font.Font(self.font_name, self.fontsize)
            self.rendered_font = None
            self.render_font()
        else:
            self.font = other.font
            self.rendered_font = other.rendered_font


class Image(Item):
    def __init__(self, name: str, rect: Union[Rect, np.ndarray, Tuple[int, int]], image: Surface):
        """
        Creates an image object, that can be used as menu item.

        :param name: The name of the item
        :param rect: The rect where the image should be located. If only a position is supplied the width and height
                     will be determined by the width and height of the supplied image.
        :param image: The image to draw
        """
        if not isinstance(rect, Rect):
            rect = Rect(rect[0], rect[1], image.get_width(), image.get_height())
        super().__init__(name, rect)
        self.image = image

    def render(self, surface: Surface):
        surface.blit(self.image, self.rect)

    def update_from(self, other):
        """
        Update values from other to myself. Should be overwritten by subclasses.
        :param other: The other item to transfer values from
        :type other: Image
        """
        super().update_from(other)


class Button(Item):
    @staticmethod
    def create_menu_image():
        menu_rect = pg.Rect(10, 10, 40, 40)
        menu_image = pg.Surface((menu_rect.width, menu_rect.height))
        menu_image.fill(Colors.BLACK)
        d = 40 // 6
        pg.draw.rect(
            menu_image, gray(140), Rect(0, 0, menu_rect.width, menu_rect.height),
            border_radius=4
        )
        pg.draw.rect(menu_image, gray(20), Rect(d, d+3, 40-2*d, d-2), border_radius=2)
        pg.draw.rect(menu_image, gray(20), Rect(d, d*3, 40-2*d, d-2), border_radius=2)
        pg.draw.rect(menu_image, gray(20), Rect(d, d*5-3, 40-2*d, d-2), border_radius=2)
        return menu_image

    @staticmethod
    def create_plus_image():
        rect = pg.Rect(0, 0, 25, 25)
        image = pg.Surface((rect.width, rect.height))

        # background
        pg.draw.rect(image, Colors.INACTIVE, rect, border_radius=4)

        # horizontal line
        horizontal_rect = pg.Rect(rect.left + 4, rect.top + 11, rect.width - 8, 3)
        pg.draw.rect(image, gray(30), horizontal_rect, border_radius=2)

        # vertical line
        vertical_rect = pg.Rect(rect.left + 11, rect.top + 4, 3, rect.height - 8)
        pg.draw.rect(image, gray(30), vertical_rect, border_radius=2)

        return image

    def __init__(self, name: str, rect: Union[Rect, np.ndarray, Tuple[int, int]], color: Optional[pg.Color] = None,
                 label: Union[None, Label, Image] = None, visible: bool = True):
        """
        Initiate a new item.
        :param rect: The rect of this item, relative to the containing element. If width or height is set to zero or if
                     only a position is supplied, the width and height are determined by the label. If label is not
                     supplied, there will be an error.
        :param color: The background color of the button.
        :param label: The label to display. Will be centered on the button
        :param visible: Whether this element should be visible or not.
        """
        # handle rect
        if not isinstance(rect, Rect):
            rect = Rect(rect[0], rect[1], 0, 0)
        if rect.width == 0:
            if isinstance(label, Image):
                rect.width = label.rect.width
            elif isinstance(label, Label):
                rect.width = label.rect.width + 20
                if label.rect.left == -1:
                    label.rect.left = 10
            else:
                raise ValueError('Failed to determine Button width from label.')
        if rect.height == 0:
            if isinstance(label, Image):
                rect.height = label.rect.height
            elif isinstance(label, Label):
                rect.height = label.rect.height + 20
                if label.rect.top == -1:
                    label.rect.top = 10
            else:
                raise ValueError('Failed to determine Button height from label.')

        # setup
        super().__init__(name, rect, visible)
        self.color = color if color is not None else gray(80)
        self.label = label

    def render(self, surface: Surface):
        color = self.color if self.hovered else self.color - gray(20)
        pg.draw.rect(surface, color, self.rect)
        if self.label:
            sub_surface = surface.subsurface(self.rect)
            if isinstance(self.label, Image):
                alpha = 255 if self.hovered else 200
                self.label.image.set_alpha(alpha)
            self.label.render(sub_surface)

    def update_from(self, other):
        """
        Update values from other to myself. Should be overwritten by subclasses.
        :param other: The other item to transfer values from
        :type other: Button
        """
        super().update_from(other)
        self.label.update_from(other.label)


class VectorItem(ItemContainer):
    def __init__(self, name: str, position: Union[np.ndarray, Tuple[int, int]], associated_vec: Vector,
                 fontsize: int = 18, text_color: pg.Color = None, font_name: str = ''):
        """
        Creates a new VectorItem that can be used to render a vector ui element.
        :param name: The name of the item
        :param position: The position where this item should be placed, relative to the containing element.
                         The width and height are determined automatically.
        :param associated_vec: The vector this ui element represents
        :param fontsize: The fontsize to use
        :param text_color: The text color to use
        :param font_name: The font to use
        """
        rect = Rect(position[0], position[1], 120, 55)
        super().__init__(name, rect)
        self.associated_vec: Vector = associated_vec
        self.fontsize = fontsize
        text_color = text_color if text_color is not None else Colors.ACTIVE
        self.font_name = font_name if font_name else pg.font.get_default_font()
        self.font: pg.font.Font = pg.font.Font(self.font_name, self.fontsize)

        name_label = Label(self.name + '_name_label', (10, 20), self.associated_vec.name, text_color=text_color)
        self.add_child(name_label)
        self.number_label_1 = Label(
            self.name + '_label_1', (50, 10), format_float(self.associated_vec.get_array()[0, 0]), text_color=text_color
        )
        self.add_child(self.number_label_1)
        self.number_label_2 = Label(
            self.name + '_label_2', (50, 30), format_float(self.associated_vec.get_array()[1, 0]), text_color=text_color
        )
        self.add_child(self.number_label_2)

        self.label_1_dragged = False
        self.label_2_dragged = False

    def render(self, surface: Surface):
        self.render_child_items(surface)

    def handle_event(self, event: pg.event.Event, rel_mouse_position: np.ndarray):
        super().handle_event(event, rel_mouse_position)
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.number_label_1.rect.collidepoint(rel_mouse_position):
                self.label_1_dragged = True
            if self.number_label_2.rect.collidepoint(rel_mouse_position):
                self.label_2_dragged = True

        if event.type == pg.KEYDOWN:
            if event.key == 8 or event.key == 127:  # esc or backspace
                self.associated_vec.has_to_be_removed = True
            if event.key == 114:  # r
                self.associated_vec.render_kind = self.associated_vec.render_kind.next()
            if event.key == 118:  # v
                self.associated_vec.visible = not self.associated_vec.visible

    def handle_every_event(self, event: pg.event.Event, rel_mouse_position: np.ndarray):
        super().handle_every_event(event, rel_mouse_position)
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.label_1_dragged = False
            self.label_2_dragged = False
        elif event.type == pg.MOUSEMOTION:
            if self.label_1_dragged:
                self.associated_vec.coordinates[0] -= event.rel[1] * 0.01
            if self.label_2_dragged:
                self.associated_vec.coordinates[1] -= event.rel[1] * 0.01

    def update_from(self, other):
        """
        Update values from other to myself. Should be overwritten by subclasses.
        :param other: The other item to transfer values from
        :type other: VectorItem
        """
        super().update_from(other)
        self.label_1_dragged = other.label_1_dragged
        self.label_2_dragged = other.label_2_dragged


class TransformItem(ItemContainer):
    def __init__(self, name: str, position: Union[np.ndarray, Tuple[int, int]],
                 associated_transform: Union[Transform2D, Transform3D], fontsize: int = 18,
                 text_color: pg.Color = None, font_name: str = ''):
        """
        Creates a new VectorItem that can be used to render a vector ui element.
        :param name: The name of the item
        :param position: The position where this item should be placed, relative to the containing element.
                         The width and height are determined automatically.
        :param associated_transform: The vector this ui element represents
        :param fontsize: The fontsize to use
        :param text_color: The text color to use
        :param font_name: The font to use
        """
        width = 160 if isinstance(associated_transform, Transform2D) else 205
        height = 55 if isinstance(associated_transform, Transform2D) else 75
        rect = Rect(position[0], position[1], width, height)
        super().__init__(name, rect)
        self.associated_transform: Union[Transform2D, Transform3D] = associated_transform
        self.fontsize = fontsize
        if text_color is None:
            text_color = Colors.ACTIVE if associated_transform.visible else Colors.INACTIVE
        self.font_name = font_name if font_name else pg.font.get_default_font()
        self.font: pg.font.Font = pg.font.Font(self.font_name, self.fontsize)

        name_label = Label(f'{self.name}_name_label', (10, 20), self.associated_transform.name, text_color=text_color)
        self.add_child(name_label)

        # add number labels
        self.number_labels = []
        for y in range(self.associated_transform.get_array().shape[0]):
            line_of_labels = []
            for x in range(self.associated_transform.get_array().shape[1]):
                number_label = Label(
                    f'{self.name}_label_{y}_{x}', (50 + 50*x, 10 + 20*y),
                    format_float(self.associated_transform.get_array()[y, x]), text_color=text_color
                )
                line_of_labels.append(number_label)
                self.add_child(number_label)
            self.number_labels.append(line_of_labels)

        self.dragged_label_index = None

    def render(self, surface: Surface):
        self.render_child_items(surface)

    def handle_event(self, event: pg.event.Event, rel_mouse_position: np.ndarray):
        super().handle_event(event, rel_mouse_position)
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for y in range(self.associated_transform.matrix.shape[0]):
                for x in range(self.associated_transform.matrix.shape[1]):
                    if self.number_labels[y][x].rect.collidepoint(rel_mouse_position):
                        self.dragged_label_index = (y, x)

        if event.type == pg.KEYDOWN:
            if event.key == 8 or event.key == 127:  # esc or backspace
                self.associated_transform.has_to_be_removed = True
            if event.key == 114:  # r
                self.associated_transform.render_kind = self.associated_transform.render_kind.next()
            if event.key == 118:  # v
                self.associated_transform.visible = not self.associated_transform.visible

    def handle_every_event(self, event: pg.event.Event, rel_mouse_position: np.ndarray):
        super().handle_every_event(event, rel_mouse_position)
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.dragged_label_index = None
        elif event.type == pg.MOUSEMOTION:
            if self.dragged_label_index:
                self.associated_transform.matrix[self.dragged_label_index] -= event.rel[1] * 0.01

    def update_from(self, other):
        """
        Update values from other to myself. Should be overwritten by subclasses.
        :param other: The other item to transfer values from
        :type other: TransformItem
        """
        super().update_from(other)
        self.dragged_label_index = other.dragged_label_index


class ElementLabel(Label):
    def __init__(self, name: str, position: Union[np.ndarray, Tuple[int, int]], text: str, associated_element: Element,
                 text_color: Optional[pg.Color] = None):
        super().__init__(name, position, text, text_color=text_color)
        self.associated_element = associated_element

    def handle_event(self, event: pg.event.Event, rel_mouse_position: np.ndarray):
        super().handle_event(event, rel_mouse_position)
        if event.type == pg.KEYDOWN:
            if event.key == 8 or event.key == 127:  # esc or backspace
                self.associated_element.has_to_be_removed = True
            if event.key == 114:  # r
                self.associated_element.render_kind = self.associated_element.render_kind.next()
            if event.key == 118:  # v
                self.associated_element.visible = not self.associated_element.visible
