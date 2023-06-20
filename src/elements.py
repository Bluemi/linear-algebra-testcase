import enum
from itertools import chain
from typing import Iterator, Optional, Union, Iterable, List
import pygame as pg

import numpy as np
import abc

from coordinate_system import CoordinateSystem, transform as transform_f
from utils import normalize_vec

DRAG_SNAP_DISTANCE = 0.07
RED = pg.Color(255, 80, 80)
GREEN = pg.Color(100, 220, 100)
CYAN = pg.Color(0, 220, 220)
YELLOW = pg.Color(220, 220, 0)


def snap(coordinates: np.ndarray):
    coordinates = coordinates.astype(dtype=float)
    rounded = np.round(coordinates)
    close_indices = np.abs(rounded - coordinates) < DRAG_SNAP_DISTANCE
    coordinates[close_indices] = rounded[close_indices]
    coordinates[coordinates == 0] = 0
    return coordinates


class RenderKind(enum.Enum):
    LINE = enum.auto()
    POINT = enum.auto()

    def next(self):
        return RenderKind(self.value % len(RenderKind) + 1)


class Element:
    __metaclass__ = abc.ABCMeta

    def __init__(self, name: str, render_kind: RenderKind):
        self.name = name
        self.hovered = False
        self.render_kind = render_kind
        self.has_to_be_removed = False
        self.visible = True

    @abc.abstractmethod
    def get_array(self) -> np.ndarray:
        """
        Returns the underlying matrix object as np.ndarray.
        Vectors should be of shape (2, 1), Elements with N elements of shape (2, N) to enable matrix multiplication with
        a 2x2 matrix in the form (matrix @ element.get_array()).
        """
        pass

    @abc.abstractmethod
    def render(self, screen: pg.Surface, coordinate_system: CoordinateSystem):
        """
        Renders the element in the coordinate system.

        :param screen: The screen to draw on
        :param coordinate_system: The coordinate system to convert coordinates into screen coordinates.
        """
        pass

    @abc.abstractmethod
    def handle_event(self, event: pg.event.Event, coordinate_system: CoordinateSystem, mouse_position: np.ndarray):
        """
        Handles the given event.

        :param event: The event to handle. All events are handled.
        :param coordinate_system: The coordinate system, that can be used to convert between screen and element space.
        :param mouse_position: The mouse position in screen space
        """
        if event.type == pg.MOUSEMOTION:
            self.hovered = self.is_hovered(mouse_position, coordinate_system)

    def is_hovered(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem):
        return False


class Vector(Element):
    def __init__(self, name: str, coordinates: np.ndarray, render_kind: RenderKind = RenderKind.LINE):
        super().__init__(name, render_kind)
        self.coordinates = coordinates.reshape((2, 1))
        self.dragged = False

    def is_hovered(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem):
        pos = coordinate_system.transform(self.get_array()).flatten()
        diff = np.sum((mouse_position - pos)**2)
        return diff < 100

    def __repr__(self):
        return '[{:.2f} {:.2f}]'.format(self.coordinates[0], self.coordinates[1])

    def get_array(self):
        return self.coordinates.reshape((2, 1))

    def render(self, screen: pg.Surface, coordinate_system: CoordinateSystem):
        transformed_vec = coordinate_system.transform(self.get_array())
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
        self.dragged = False

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
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.is_hovered(mouse_position, coordinate_system):
                self.dragged = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.dragged = False
        elif event.type == pg.MOUSEMOTION:
            if self.dragged:
                pos = coordinate_system.transform_inverse(np.array(event.pos))
                self.move_to(pos.reshape((2, 1)))


class Transform2D(Element):
    def __init__(self, name: str, render_kind: RenderKind = RenderKind.LINE):
        super().__init__(name, render_kind)
        self.matrix = np.eye(2)
        self.dragged_index = None

    def get_array(self):
        return snap(self.matrix)

    def render(self, screen: pg.Surface, coordinate_system: CoordinateSystem):
        transformed_vecs = coordinate_system.transform(self.get_array()).T
        width = 3 if self.hovered else 1
        for i, transformed_vec in enumerate(transformed_vecs):
            color = CYAN if i == 0 else YELLOW
            if self.render_kind == RenderKind.POINT:
                pg.draw.circle(screen, color, transformed_vec, width)
            elif self.render_kind == RenderKind.LINE:
                pg.draw.line(screen, color, coordinate_system.get_zero_point(), transformed_vec, width=width)

    def handle_event(self, event: pg.event.Event, coordinate_system: CoordinateSystem, mouse_position: np.ndarray):
        pass


class Transform3D(Element):
    def __init__(self, name: str, render_kind: RenderKind = RenderKind.LINE):
        super().__init__(name, render_kind)
        self.matrix = np.eye(3)

    def get_array(self):
        return snap(self.matrix)

    def render(self, screen: pg.Surface, coordinate_system: CoordinateSystem):
        pass

    def handle_event(self, event: pg.event.Event, coordinate_system: CoordinateSystem, mouse_position: np.ndarray):
        pass


class Transformed(Element):
    def __init__(self, name: str, element: Union[None, Vector, MultiVectorObject], transform: Optional[Transform2D],
                 render_kind: RenderKind):
        super().__init__(name, render_kind)
        self.element = element
        self.transform = transform

    def get_position(self):
        if self.element is not None and self.transform is not None:
            return transform_f(self.transform.get_array(), self.element.get_array())
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
        self.last_result = None
        self.element_buffer = element_buffer

    def compile_definition(self):
        self.error = None
        try:
            self.compiled_definition = compile(self.definition, "<string>", "eval")
        except SyntaxError as e:
            self.compiled_definition = None
            self.error = repr(e)

    def set_definition(self, definition):
        self.definition = definition
        self.error = None
        self.compiled_definition = None

    def get_array(self):
        return self.last_result

    def render(self, screen: pg.Surface, coordinate_system: CoordinateSystem):
        zero_point = coordinate_system.get_zero_point()
        if self.compiled_definition:
            # build eval locals
            eval_locals = {'np': np, 'mm': transform_f, 'norm': normalize_vec}
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
                print(self.error)

            self.last_result = result
            if not isinstance(result, np.ndarray) and isinstance(result, Iterable):
                result = np.array(result)
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
                                pg.draw.line(screen, RED, zero_point, point, width=1)
                else:
                    self.error = 'Invalid result shape: {}'.format(result.shape)
            elif result is not None:
                self.error = 'result is not numpy array'

    def handle_event(self, event: pg.event.Event, coordinate_system: CoordinateSystem, mouse_position: np.ndarray):
        pass


class ElementBuffer:
    def __init__(self):
        self.elements: List[Element] = []
        self.transforms: List[Element] = []
        self.transformed: List[Element] = []

    def __iter__(self) -> Iterator[Element]:
        return iter(self.elements)

    def create_example_elements(self):
        self.elements.append(Vector('v1', np.array([1, 1])))

    def remove_elements(self):
        self.elements = [e for e in self.elements if not e.has_to_be_removed]
        self.transforms = [t for t in self.transforms if not t.has_to_be_removed]
        self.transformed = [t for t in self.transformed if not t.has_to_be_removed]

    def render(self, screen: pg.Surface, coordinate_system: CoordinateSystem):
        for element in chain(self.elements, self.transforms, self.transformed):
            if element.visible:
                element.render(screen, coordinate_system)

    def handle_event(self, event: pg.event.Event, coordinate_system: CoordinateSystem, mouse_position: np.ndarray):
        for e in self.elements:
            e.handle_event(event, coordinate_system, mouse_position)
        for e in self.transformed:
            e.handle_event(event, coordinate_system, mouse_position)
