import enum
from typing import Iterator, Optional, Union

import numpy as np
import abc

from coordinate_system import CoordinateSystem


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

    def toggle(self):
        return RenderKind(self.value % len(RenderKind) + 1)


class Element:
    __metaclass__ = abc.ABCMeta

    def __init__(self, name: str, render_kind: RenderKind):
        self.name = name
        self.hovered = False
        self.render_kind = render_kind
        self.has_to_be_removed = False

    @abc.abstractmethod
    def is_hovered(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem):
        return

    @abc.abstractmethod
    def move_to(self, mouse_position: np.ndarray):
        return

    @abc.abstractmethod
    def get_array(self):
        return


class Vector(Element):
    def __init__(self, name: str, coordinates: np.ndarray, render_kind: RenderKind = RenderKind.LINE):
        super().__init__(name, render_kind)
        self.coordinates = coordinates

    def is_hovered(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem):
        pos = coordinate_system.transform(self.coordinates)
        diff = np.sum((mouse_position - pos)**2)
        return diff < 100

    def move_to(self, mouse_position: np.ndarray):
        self.coordinates = snap(mouse_position)

    def __repr__(self):
        return '[{:.2f} {:.2f}]'.format(self.coordinates[0], self.coordinates[1])

    def get_array(self):
        return self.coordinates


class UnitCircle(Element):
    def __init__(self, name: str, render_kind: RenderKind = RenderKind.POINT, num_points=40):
        super().__init__(name, render_kind)
        self.num_points = num_points
        space = np.linspace(0, np.pi * 2, num=num_points, endpoint=False)
        coordinates = np.stack([np.cos(space), np.sin(space)], axis=1)
        self.coordinates = np.vstack([coordinates, [0, 0]])  # add zero point

    def is_hovered(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem):
        pos = coordinate_system.transform(self.coordinates)
        diff = np.sum((mouse_position - pos)**2, axis=1)
        return np.any(diff < 100)

    def move_to(self, mouse_position: np.ndarray):
        mouse_position = snap(mouse_position)
        space = np.linspace(0, np.pi * 2, num=self.num_points, endpoint=False)
        self.coordinates = np.stack([np.cos(space) * mouse_position[0], np.sin(space) * mouse_position[1]], axis=1)

    def get_array(self):
        return self.coordinates.T


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
    def __init__(self, name: str, element: Union[None, Vector, UnitCircle], transform: Optional[Transform2D],
                 render_kind: RenderKind):
        super().__init__(name, render_kind)
        self.element = element
        self.transform = transform

    def get_position(self):
        if self.element is not None and self.transform is not None:
            return (self.transform.get_array() @ self.element.coordinates.T).T
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
