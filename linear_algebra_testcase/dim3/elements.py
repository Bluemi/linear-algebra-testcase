from itertools import chain
from typing import Iterator, Optional, Union, Iterable, List, Self
import pygame as pg

import numpy as np

from .coordinate_system import CoordinateSystem
from linear_algebra_testcase.utils import normalize_vec
from linear_algebra_testcase.dim2.elements import (Element, RenderKind, RED, GREEN, CYAN, YELLOW, MAGENTA, snap)


AXIS_COLORS = [CYAN, YELLOW, MAGENTA]


class Vector3D(Element):
    def __init__(self, name: str, coordinates: np.ndarray, render_kind: RenderKind = RenderKind.LINE):
        super().__init__(name, render_kind)
        self.coordinates = coordinates.reshape((3, 1))
        self.dragged = False

    def is_hovered(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem):
        if not self.visible:
            return False
        pos = coordinate_system.transform(self.get_array()).flatten()
        if not len(pos):
            return False
        diff = np.sum((mouse_position - pos[:2])**2)
        return diff < 100

    def __repr__(self):
        return '[{:.2f} {:.2f} {:.2f}]'.format(self.coordinates[0], self.coordinates[1], self.coordinates[2])

    def get_array(self):
        return self.coordinates.reshape((1, 3))

    def render(self, screen: pg.Surface, coordinate_system: CoordinateSystem):
        transformed_vec = coordinate_system.transform(self.get_array()).flatten()
        if not len(transformed_vec):
            return
        width = 3 if self.hovered else 1
        if self.render_kind == RenderKind.POINT:
            pg.draw.circle(screen, GREEN, transformed_vec[:2], width)
        elif self.render_kind == RenderKind.LINE:
            pg.draw.line(
                screen, GREEN, coordinate_system.get_zero_point().flatten()[:2], transformed_vec[:2], width=width
            )

    def handle_event(self, event: pg.event.Event, coordinate_system: CoordinateSystem, mouse_position: np.ndarray):
        super().handle_event(event, coordinate_system, mouse_position)
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.is_hovered(mouse_position, coordinate_system):
                self.dragged = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.dragged = False
        # elif event.type == pg.MOUSEMOTION:
        #     if self.dragged:
        #         pos = coordinate_system.transform_inverse(np.array(event.pos))
        #         self.coordinates = snap(pos)


class MultiVectorObject3D(Element):
    def __init__(
            self, name: str, coordinates: np.ndarray, line_indices: np.ndarray,
            render_kind: RenderKind = RenderKind.LINE
    ):
        super().__init__(name, render_kind)
        self.coordinates = coordinates
        self.line_indices = line_indices
        self.dragged = False

    @classmethod
    def create_cube(
            cls, name: str, bot_left_back: np.ndarray, top_right_front: np.ndarray,
            render_kind: RenderKind = RenderKind.POINT
    ) -> Self:
        x1, y1, z1 = bot_left_back
        x2, y2, z2 = top_right_front
        coordinates = np.array([
            [x1, y1, z1],  # 0
            [x2, y1, z1],  # 1
            [x2, y2, z1],  # 2
            [x1, y2, z1],  # 3
            [x1, y1, z2],  # 4
            [x2, y1, z2],  # 5
            [x2, y2, z2],  # 6
            [x1, y2, z2]   # 7
        ])
        line_indices = np.array([
            # x changes
            [0, 1],
            [2, 3],
            [4, 5],
            [6, 7],
            # y changes
            [0, 3],
            [1, 2],
            [4, 7],
            [5, 6],
            # z changes
            [0, 4],
            [1, 5],
            [2, 6],
            [3, 7],
        ])
        return MultiVectorObject3D(name, coordinates, line_indices, render_kind)

    def is_hovered(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem):
        if not self.visible:
            return False
        pos = coordinate_system.transform(self.coordinates)[:, :2]
        diffs = np.sum((mouse_position.reshape(1, 2) - pos)**2, axis=1)
        return np.any(diffs < 100)

    def __repr__(self):
        return '[{:.2f} {:.2f}]'.format(self.coordinates[0], self.coordinates[1])

    def get_array(self):
        return self.coordinates

    def render(self, screen: pg.Surface, coordinate_system: CoordinateSystem):
        transformed_points = coordinate_system.transform(self.coordinates, clip=False)[:, :2]
        width = 3 if self.hovered else 1
        if self.render_kind == RenderKind.POINT:
            for index, point in enumerate(transformed_points):
                pg.draw.circle(screen, GREEN, point, width)
        elif self.render_kind == RenderKind.LINE:
            for indices in self.line_indices:
                points = transformed_points[indices]
                pg.draw.line(screen, GREEN, points[0], points[1], width=width)

    def handle_event(self, event: pg.event.Event, coordinate_system: CoordinateSystem, mouse_position: np.ndarray):
        super().handle_event(event, coordinate_system, mouse_position)
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.is_hovered(mouse_position, coordinate_system):
                self.dragged = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.dragged = False
        # elif event.type == pg.MOUSEMOTION:
            # if self.dragged:
            #     pos = coordinate_system.transform_inverse(np.array(event.pos))
            #     self.coordinates = snap(pos)


class Transform3D(Element):
    def __init__(self, name: str, render_kind: RenderKind = RenderKind.LINE):
        super().__init__(name, render_kind)
        self.matrix = np.eye(3)
        self.dragged_index = None
        self.hovered_index = None

    def get_array(self):
        return snap(self.matrix)

    def render(self, screen: pg.Surface, coordinate_system: CoordinateSystem):
        transformed_vecs = coordinate_system.transform(self.get_array(), clip=False)[:, :2]
        zero_point = coordinate_system.get_zero_point().flatten()[:2]
        for i, transformed_vec in enumerate(transformed_vecs):
            width = 3 if self.hovered_index == i else 1
            color = AXIS_COLORS[i]
            if self.render_kind == RenderKind.POINT:
                pg.draw.circle(screen, color, transformed_vec, width)
            elif self.render_kind == RenderKind.LINE:
                pg.draw.line(screen, color, zero_point, transformed_vec, width=width)

    def is_hovered(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem):
        return self.hovered_index is not None

    def get_hovered_index(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem) -> Optional[int]:
        if not self.visible:
            return None
        pos = coordinate_system.transform(self.get_array(), clip=False)[:, :2]
        diff = np.sum((mouse_position - pos)**2, axis=1)
        indices: np.ndarray = np.where(diff < 100)[0]
        if len(indices):
            return int(indices[0])
        return None

    def handle_event(self, event: pg.event.Event, coordinate_system: CoordinateSystem, mouse_position: np.ndarray):
        super().handle_event(event, coordinate_system, mouse_position)
        if event.type == pg.MOUSEBUTTONDOWN:
            self.dragged_index = self.hovered_index
        elif event.type == pg.MOUSEBUTTONUP:
            self.dragged_index = None
        elif event.type == pg.MOUSEMOTION:
            self.hovered_index = self.get_hovered_index(mouse_position, coordinate_system)
            # if self.dragged_index is not None:
            #     pos = coordinate_system.transform_inverse(np.array(event.pos))
            #     self.matrix[:, self.dragged_index] = snap(pos)


class Translate3D(Element):
    def __init__(self, name: str, render_kind: RenderKind = RenderKind.LINE):
        super().__init__(name, render_kind)
        self.matrix = np.eye(4)
        self.dragged_index = None
        self.hovered_index = None

    def get_array(self):
        return snap(self.matrix)

    def get_render_locations(self, coordinate_system: CoordinateSystem):
        vecs = self.get_array()[:3]
        offset = vecs[:, 3].reshape(1, 3)
        first_vecs = vecs[:, :3] + offset
        first_vecs_transformed = coordinate_system.transform(first_vecs, clip=False)[:, :2]
        offset_transformed = coordinate_system.transform(offset, clip=False)[:, :2]
        return np.concatenate([first_vecs_transformed, offset_transformed.reshape(1, 2)], axis=0)

    def render(self, screen: pg.Surface, coordinate_system: CoordinateSystem):
        render_locations = self.get_render_locations(coordinate_system)
        offset_location = render_locations[3]
        zero_point = coordinate_system.get_zero_point().flatten()[:2]
        for i, transformed_vec in enumerate(render_locations):
            width = 3 if self.hovered_index == i else 1
            color = [CYAN, YELLOW, MAGENTA, MAGENTA][i]
            if self.render_kind == RenderKind.POINT:
                pg.draw.circle(screen, color, transformed_vec, width)
            elif self.render_kind == RenderKind.LINE:
                if i < 3:
                    pg.draw.line(screen, color, offset_location, transformed_vec, width=width)
                else:
                    pg.draw.line(screen, color, zero_point, offset_location, width=width)

    def get_hovered_index(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem) -> Optional[int]:
        if not self.visible:
            return None
        pos = self.get_render_locations(coordinate_system)[:, :2]
        diff = np.sum((mouse_position - pos)**2, axis=1)
        indices: np.ndarray = np.where(diff < 100)[0]
        if len(indices):
            return int(indices[0])
        return None

    def is_hovered(self, _mouse_position: np.ndarray, _coordinate_system: CoordinateSystem):
        return self.hovered_index is not None

    def handle_event(self, event: pg.event.Event, coordinate_system: CoordinateSystem, mouse_position: np.ndarray):
        super().handle_event(event, coordinate_system, mouse_position)
        if event.type == pg.MOUSEBUTTONDOWN:
            self.dragged_index = self.hovered_index
        elif event.type == pg.MOUSEBUTTONUP:
            self.dragged_index = None
        elif event.type == pg.MOUSEMOTION:
            self.hovered_index = self.get_hovered_index(mouse_position, coordinate_system)
            # if self.dragged_index is not None:
            #     pos = coordinate_system.transform_inverse(np.array(event.pos))
            #     offset = np.zeros(2) if self.dragged_index == 2 else self.get_array()[:2, 2]
            #     self.matrix[:2, self.dragged_index] = snap(pos - offset)


class Transformed(Element):
    def __init__(self, name: str, element: Union[None, MultiVectorObject3D], transform: Optional[Transform3D],
                 render_kind: RenderKind):
        super().__init__(name, render_kind)
        self.element = element
        self.transform = transform

    # noinspection PyMethodMayBeStatic
    def get_position(self):
        # TODO
        # if self.element is not None and self.transform is not None:
        # return transform_p(self.transform.get_array(), self.element.get_array())
        return None

    def get_array(self):
        return self.get_position()

    def render(self, screen: pg.Surface, coordinate_system: CoordinateSystem):
        pass
        # new_vec = self.get_position()
        # zero_point = coordinate_system.get_zero_point()
        # if new_vec is None:
        #     return
        # transformed_vec = coordinate_system.transform(new_vec).T
        # for point in transformed_vec:
        #     if self.render_kind == RenderKind.POINT:
        #         pg.draw.circle(screen, RED, point, 3)
        #     elif self.render_kind == RenderKind.LINE:
        #         pg.draw.line(screen, RED, zero_point, point, width=1)

    def handle_event(self, event: pg.event.Event, coordinate_system: CoordinateSystem, mouse_position: np.ndarray):
        pass


class CustomTransformed(Element):
    def __init__(self, name: str, render_kind: RenderKind, element_buffer):
        super().__init__(name, render_kind)
        self.definition = ""
        self.compiled_definition = None
        self.error = None
        self.last_error = None
        self.last_result = None
        self.element_buffer = element_buffer

    def compile_definition(self):
        self.error = None
        self.last_error = None
        try:
            self.compiled_definition = compile(self.definition, "<string>", "eval")
        except SyntaxError as e:
            self.compiled_definition = None
            self.error = repr(e)
            self.last_error = self.error

    def set_definition(self, definition):
        self.definition = definition
        self.error = None
        self.last_error = None
        self.compiled_definition = None

    def get_array(self):
        return self.last_result

    def render(self, screen: pg.Surface, coordinate_system: CoordinateSystem):
        zero_point = coordinate_system.get_zero_point()
        if self.compiled_definition:
            # build eval locals
            # eval_locals = {'np': np, 'mm': transform_p, 'norm': normalize_vec}
            eval_locals = {'np': np, 'norm': normalize_vec}
            for e in self.element_buffer.elements:
                eval_locals[e.name] = e.get_array()
            for t in self.element_buffer.transforms:
                eval_locals[t.name] = t.get_array()
            for t in self.element_buffer.transformed:
                eval_locals[t.name] = t.get_array()

            result = None
            self.error = None
            try:
                result = eval(self.compiled_definition, {}, eval_locals)
            except Exception as e:
                self.error = repr(e)

            self.last_result = result
            if not isinstance(result, np.ndarray) and isinstance(result, Iterable):
                try:
                    result = np.array(result)
                except ValueError as e:
                    self.error = repr(e)
            if isinstance(result, np.ndarray):
                self.last_result = result
                if result.shape == (2,):
                    result = np.expand_dims(result, 0)
                if result.shape[0] == 2 and len(result.shape) == 2:
                    if self.visible:
                        transformed_vecs = coordinate_system.transform(result).T
                        # width = 3 if element.hovered else 1
                        for point in transformed_vecs:
                            if self.render_kind == RenderKind.POINT:
                                pg.draw.circle(screen, RED, point, 3)
                            elif self.render_kind == RenderKind.LINE:
                                pg.draw.line(screen, RED, zero_point, point.real, width=1)
                else:
                    self.error = 'Invalid result shape: {}'.format(result.shape)
            elif result is not None:
                self.error = 'result is not numpy array'

        if self.error:
            if not (self.last_error and self.error == self.last_error):
                print(self.error)
        self.last_error = self.error

    def handle_event(self, event: pg.event.Event, coordinate_system: CoordinateSystem, mouse_position: np.ndarray):
        pass


class ElementBuffer:
    def __init__(self):
        self.elements: List[Element] = []
        self.transforms: List[Element] = []
        self.transformed: List[Element] = []

        # self.create_example_elements()

    def __iter__(self) -> Iterator[Element]:
        return iter(self.elements)

    def create_example_elements(self):
        self.elements.append(
            MultiVectorObject3D.create_cube(
                'c1', np.zeros(3, dtype=float) - 0.5, np.zeros(3, dtype=float) + 0.5, render_kind=RenderKind.POINT
            )
        )

    def remove_elements(self):
        self.elements = [e for e in self.elements if not e.has_to_be_removed]
        self.transforms = [t for t in self.transforms if not t.has_to_be_removed]
        self.transformed = [t for t in self.transformed if not t.has_to_be_removed]

    def render(self, screen: pg.Surface, coordinate_system: CoordinateSystem):
        for element in chain(self.elements, self.transforms, self.transformed):
            if element.visible:
                element.render(screen, coordinate_system)

    def handle_event(self, event: pg.event.Event, coordinate_system: CoordinateSystem, mouse_position: np.ndarray):
        for e in chain(self.elements, self.transforms, self.transformed):
            e.handle_event(event, coordinate_system, mouse_position)
