import enum
from typing import Iterator, Optional, Union

import numpy as np
import abc

from coordinate_system import CoordinateSystem, transform as transform_f

DRAG_SNAP_DISTANCE = 0.07


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
    def is_hovered(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem):
        return

    @abc.abstractmethod
    def move_to(self, mouse_position: np.ndarray):
        return

    @abc.abstractmethod
    def get_array(self) -> np.ndarray:
        """
        Returns the underlying matrix object as np.ndarray.
        Vectors should be of shape (2, 1), Elements with N elements of shape (2, N) to enable matrix multiplication with
        a 2x2 matrix in the form (matrix @ element.get_array()).
        """
        pass


class Vector(Element):
    def __init__(self, name: str, coordinates: np.ndarray, render_kind: RenderKind = RenderKind.LINE):
        super().__init__(name, render_kind)
        self.coordinates = coordinates.reshape((2, 1))

    def is_hovered(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem):
        pos = coordinate_system.transform(self.get_array()).flatten()
        diff = np.sum((mouse_position - pos)**2)
        return diff < 100

    def move_to(self, mouse_position: np.ndarray):
        self.coordinates = snap(mouse_position)

    def __repr__(self):
        return '[{:.2f} {:.2f}]'.format(self.coordinates[0], self.coordinates[1])

    def get_array(self):
        return self.coordinates.reshape((2, 1))


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
        pos = coordinate_system.transform(self.get_array()).T
        diff = np.sum((mouse_position - pos)**2, axis=1)
        return np.any(diff < 100)

    def move_to(self, mouse_position: np.ndarray):
        mouse_position = snap(mouse_position)
        self.coordinates = self.original_coordinates * mouse_position

    def get_array(self):
        return self.coordinates


class Transform2D(Element):
    def __init__(self, name: str, render_kind: RenderKind = RenderKind.LINE):
        super().__init__(name, render_kind)
        self.matrix = np.eye(2)

    def get_array(self):
        return snap(self.matrix)

    def is_hovered(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem):
        return False

    def move_to(self, mouse_position: np.ndarray):
        pass


class Transform3D(Element):
    def __init__(self, name: str, render_kind: RenderKind = RenderKind.LINE):
        super().__init__(name, render_kind)
        self.matrix = np.eye(3)

    def get_array(self):
        return snap(self.matrix)

    def is_hovered(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem):
        return False

    def move_to(self, mouse_position: np.ndarray):
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

    def is_hovered(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem):
        return False

    def move_to(self, mouse_position: np.ndarray):
        pass


class CustomTransformed(Element):
    def __init__(self, name: str, render_kind: RenderKind):
        super().__init__(name, render_kind)
        self.definition = ""
        self.compiled_definition = None
        self.error = None
        self.last_result = None

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

    def is_hovered(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem):
        return False

    def move_to(self, mouse_position: np.ndarray):
        pass


class ElementBuffer:
    def __init__(self):
        self.elements = []
        self.transforms = []
        self.transformed = []

    def __iter__(self) -> Iterator[Element]:
        return iter(self.elements)

    def create_example_elements(self):
        self.elements.append(Vector('v1', np.array([1, 1])))

    def remove_elements(self):
        self.elements = [e for e in self.elements if not e.has_to_be_removed]
        self.transforms = [t for t in self.transforms if not t.has_to_be_removed]
        self.transformed = [t for t in self.transformed if not t.has_to_be_removed]
