from itertools import chain
from typing import Iterator, Optional, Union, Iterable, List
import pygame as pg

import numpy as np

from .coordinate_system import CoordinateSystem, transform_perspective as transform_p
from linear_algebra_testcase.common.utils import normalize_vec
from linear_algebra_testcase.common.elements_core import Element, RenderKind, GREEN, RED, snap, AXIS_COLORS


class Vector(Element):
    def __init__(self, name: str, coordinates: np.ndarray, render_kind: RenderKind = RenderKind.LINE):
        super().__init__(name, render_kind)
        self.coordinates = coordinates.reshape((2, 1))
        self.dragged = False

    def is_hovered(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem):
        if not self.visible:
            return False
        pos = coordinate_system.transform(self.get_array()).flatten()
        diff = np.sum((mouse_position - pos)**2)
        return diff < 100

    def __repr__(self):
        return '[{:.2f} {:.2f}]'.format(self.coordinates[0], self.coordinates[1])

    def get_array(self):
        return self.coordinates.reshape((2, 1))

    def render(self, screen: pg.Surface, coordinate_system: CoordinateSystem):
        transformed_vec = coordinate_system.transform(self.get_array()).flatten()
        width = 3 if self.hovered else 1
        if self.render_kind == RenderKind.POINT:
            pg.draw.circle(screen, GREEN, transformed_vec, width)
        elif self.render_kind == RenderKind.LINE:
            pg.draw.line(screen, GREEN, coordinate_system.get_zero_point(), transformed_vec, width=width)

    def handle_event(self, event: pg.event.Event, coordinate_system: CoordinateSystem, mouse_position: np.ndarray):
        super().handle_event(event, coordinate_system, mouse_position)
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.is_hovered(mouse_position, coordinate_system):
                self.dragged = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.dragged = False
        elif event.type == pg.MOUSEMOTION:
            if self.dragged:
                pos = coordinate_system.transform_inverse(np.array(event.pos))
                self.coordinates = snap(pos)


class MultiVectorObject(Element):
    def __init__(self, name: str, coordinates: np.ndarray, render_kind: RenderKind = RenderKind.POINT):
        super().__init__(name, render_kind)
        self.coordinates = coordinates
        self.original_coordinates = coordinates

    @staticmethod
    def generate_unit_circle(num_points, include_center=True):
        space = np.linspace(0, np.pi * 2, num=num_points, endpoint=False)
        coordinates = np.vstack([np.cos(space), np.sin(space)])
        if include_center:
            coordinates = np.hstack([coordinates, [[0], [0]]])  # add center
        return coordinates

    @staticmethod
    def generate_house():
        lines = [
            # sides
            MultiVectorObject.generate_line([-1, -1], [-1, 1]),
            MultiVectorObject.generate_line([-1, 1], [1, 1]),
            MultiVectorObject.generate_line([1, 1], [1, -1]),
            MultiVectorObject.generate_line([1, -1], [-1, -1]),

            # roof
            MultiVectorObject.generate_line([-1, 1], [0, 2], num_points=8),
            MultiVectorObject.generate_line([0, 2], [1, 1], num_points=8),

            # door
            MultiVectorObject.generate_line([0, -1], [0, 0], num_points=5),
            MultiVectorObject.generate_line([0, 0], [0.5, 0], num_points=2),
            MultiVectorObject.generate_line([0.5, 0], [0.5, -1], num_points=5),

            # windows
            MultiVectorObject.generate_line([-0.8, 0.2], [-0.8, 0.8], num_points=4),
            MultiVectorObject.generate_line([-0.8, 0.8], [-0.2, 0.8], num_points=4),
            MultiVectorObject.generate_line([-0.2, 0.8], [-0.2, 0.2], num_points=4),
            MultiVectorObject.generate_line([-0.2, 0.2], [-0.8, 0.2], num_points=4),

            # chimney
            MultiVectorObject.generate_line([-0.75, 1.25], [-0.75, 2], num_points=4),
            MultiVectorObject.generate_line([-0.75, 2], [-0.37, 2], num_points=3),
            MultiVectorObject.generate_line([-0.37, 2], [-0.37, 1.62], num_points=2),
        ]
        return np.concatenate(lines, axis=1)

    @staticmethod
    def generate_line(a, b, num_points=10, endpoint=False):
        space = np.linspace(0, 1, num_points, endpoint=endpoint)
        return np.reshape(a, (2, 1)) * (1 - space) + np.reshape(b, (2, 1)) * space

    def is_hovered(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem):
        if not self.visible:
            return False
        pos = coordinate_system.transform(self.get_array()).T
        diff = np.sum((mouse_position - pos)**2, axis=1)
        return np.any(diff < 100)

    def move_to(self, mouse_position: np.ndarray):
        mouse_position = snap(mouse_position)
        self.coordinates = self.original_coordinates * mouse_position

    def get_array(self):
        return self.coordinates

    def render(self, screen: pg.Surface, coordinate_system: CoordinateSystem):
        transformed_vec = coordinate_system.transform(self.get_array()).T
        width = 4 if self.hovered else 3
        for point in transformed_vec:
            if self.render_kind == RenderKind.POINT:
                pg.draw.circle(screen, GREEN, point, width)
            elif self.render_kind == RenderKind.LINE:
                pg.draw.line(screen, GREEN, coordinate_system.get_zero_point(), point, width=1)

    def handle_event(self, event: pg.event.Event, coordinate_system: CoordinateSystem, mouse_position: np.ndarray):
        super().handle_event(event, coordinate_system, mouse_position)


class Transform2D(Element):
    def __init__(self, name: str, render_kind: RenderKind = RenderKind.LINE):
        super().__init__(name, render_kind)
        self.matrix = np.eye(2)
        self.dragged_index = None
        self.hovered_index = None

    def get_array(self):
        return snap(self.matrix)

    def render(self, screen: pg.Surface, coordinate_system: CoordinateSystem):
        transformed_vecs = coordinate_system.transform(self.get_array()).T
        for i, transformed_vec in enumerate(transformed_vecs):
            width = 3 if self.hovered_index == i else 1
            color = AXIS_COLORS[i]
            if self.render_kind == RenderKind.POINT:
                pg.draw.circle(screen, color, transformed_vec, width)
            elif self.render_kind == RenderKind.LINE:
                pg.draw.line(screen, color, coordinate_system.get_zero_point(), transformed_vec, width=width)

    def is_hovered(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem):
        return self.hovered_index is not None

    def get_hovered_index(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem) -> Optional[int]:
        if not self.visible:
            return None
        pos = coordinate_system.transform(self.get_array()).T
        diff = np.sum((mouse_position - pos)**2, axis=1)
        indices: np.ndarray = np.where(diff < 100)[0]
        if len(indices):
            return indices[0]
        return None

    def handle_event(self, event: pg.event.Event, coordinate_system: CoordinateSystem, mouse_position: np.ndarray):
        super().handle_event(event, coordinate_system, mouse_position)
        if event.type == pg.MOUSEBUTTONDOWN:
            self.dragged_index = self.hovered_index
        elif event.type == pg.MOUSEBUTTONUP:
            self.dragged_index = None
        elif event.type == pg.MOUSEMOTION:
            self.hovered_index = self.get_hovered_index(mouse_position, coordinate_system)
            if self.dragged_index is not None:
                pos = coordinate_system.transform_inverse(np.array(event.pos))
                self.matrix[:, self.dragged_index] = snap(pos)


class Translate2D(Element):
    def __init__(self, name: str, render_kind: RenderKind = RenderKind.LINE):
        super().__init__(name, render_kind)
        self.matrix = np.eye(3)
        self.dragged_index = None
        self.hovered_index = None

    def get_array(self):
        return snap(self.matrix)

    def get_render_locations(self, coordinate_system: CoordinateSystem):
        vecs = self.get_array()[:2]
        offset = vecs[:, 2].reshape(2, 1)
        first_vecs = vecs[:, :2] + offset
        first_vecs_transformed = coordinate_system.transform(first_vecs)
        offset_transformed = coordinate_system.transform(offset)
        return np.concatenate([first_vecs_transformed, offset_transformed.reshape(2, 1)], axis=1)

    def render(self, screen: pg.Surface, coordinate_system: CoordinateSystem):
        render_locations = self.get_render_locations(coordinate_system).T
        offset_location = render_locations[2]
        for i, transformed_vec in enumerate(render_locations):
            width = 3 if self.hovered_index == i else 1
            color = AXIS_COLORS[i]
            if self.render_kind == RenderKind.POINT:
                pg.draw.circle(screen, color, transformed_vec, width)
            elif self.render_kind == RenderKind.LINE:
                if i < 2:
                    pg.draw.line(screen, color, offset_location, transformed_vec, width=width)
                else:
                    pg.draw.line(screen, color, coordinate_system.get_zero_point(), offset_location, width=width)

    def get_hovered_index(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem) -> Optional[int]:
        if not self.visible:
            return None
        pos = self.get_render_locations(coordinate_system).T
        diff = np.sum((mouse_position - pos)**2, axis=1)
        indices: np.ndarray = np.where(diff < 100)[0]
        if len(indices):
            return indices[0]
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
            if self.dragged_index is not None:
                pos = coordinate_system.transform_inverse(np.array(event.pos))
                offset = np.zeros(2) if self.dragged_index == 2 else self.get_array()[:2, 2]
                self.matrix[:2, self.dragged_index] = snap(pos - offset)


class Transformed2D(Element):
    def __init__(self, name: str, element: Union[None, Vector, MultiVectorObject], transform: Optional[Transform2D],
                 render_kind: RenderKind):
        super().__init__(name, render_kind)
        self.element = element
        self.transform = transform

    def get_position(self):
        if self.element is not None and self.transform is not None:
            return transform_p(self.transform.get_array(), self.element.get_array())
        return None

    def get_array(self):
        return self.get_position()

    def render(self, screen: pg.Surface, coordinate_system: CoordinateSystem):
        new_vec = self.get_position()
        zero_point = coordinate_system.get_zero_point()
        if new_vec is None:
            return
        transformed_vec = coordinate_system.transform(new_vec).T
        for point in transformed_vec:
            if self.render_kind == RenderKind.POINT:
                pg.draw.circle(screen, RED, point, 3)
            elif self.render_kind == RenderKind.LINE:
                pg.draw.line(screen, RED, zero_point, point, width=1)

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
            eval_locals = {'np': np, 'mm': transform_p, 'norm': normalize_vec}
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
