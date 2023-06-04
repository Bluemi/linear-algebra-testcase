import enum
from typing import List, Optional, Union

import pygame as pg

from elements import Transform2D, ElementBuffer, Transformed, Vector, UnitCircle, CustomTransformed, Transform3D


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

        unit_circle_add_button = UIButton(pg.Rect(160, element_y_pos-4, 25, 25), action=ActionType.ADD_UNIT_CIRCLE,
                                          sign=UIButton.Sign.PLUS)
        self.ui_elements.append(unit_circle_add_button)
        element_y_pos += 25

        # Objects
        for element in element_buffer:
            if isinstance(element, Vector):
                rect = pg.Rect(20, element_y_pos, 180, 20)
                ui_element = UIVector(rect, element)
                self.ui_elements.append(ui_element)
            elif isinstance(element, UnitCircle):
                rect = pg.Rect(20, element_y_pos, 180, 20)
                ui_element = UIUnitCircle(rect, element)
                self.ui_elements.append(ui_element)
            element_y_pos += 25

        # Transforms Title
        element_y_pos += 10
        transforms_title = UIText(pg.Rect(10, element_y_pos, 120, 20), 'Transforms')
        self.ui_elements.append(transforms_title)

        # Add Button
        transform2d_add_button = UIButton(
            pg.Rect(130, element_y_pos-4, 25, 25), action=ActionType.ADD_TRANSFORM2D, sign=UIButton.Sign.PLUS
        )
        self.ui_elements.append(transform2d_add_button)

        transform3d_add_button = UIButton(
            pg.Rect(160, element_y_pos-4, 25, 25), action=ActionType.ADD_TRANSFORM3D, sign=UIButton.Sign.PLUS
        )
        self.ui_elements.append(transform3d_add_button)

        element_y_pos += 30

        # Transform Objects
        for transform in element_buffer.transforms:
            height = 50 if isinstance(transform, Transform2D) else 70
            rect = pg.Rect(20, element_y_pos, 180, height)

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
        transformed_title = UIText(pg.Rect(10, element_y_pos, 120, 20), 'Transformed')
        self.ui_elements.append(transformed_title)

        # Add Button
        transformed_add_button = UIButton(pg.Rect(130, element_y_pos-4, 25, 25), action=ActionType.ADD_TRANSFORMED,
                                          sign=UIButton.Sign.PLUS)
        self.ui_elements.append(transformed_add_button)

        # Add Button - Custom Transformed
        transformed_add_button = UIButton(pg.Rect(160, element_y_pos-4, 25, 25),
                                          action=ActionType.ADD_CUSTOM_TRANSFORMED, sign=UIButton.Sign.PLUS)
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
        self.rect: pg.Rect = rect

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
