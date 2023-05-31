from typing import Iterator, Optional, Union

import numpy as np
import abc

from coordinate_system import CoordinateSystem


class Element:
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.hovered = False

    @abc.abstractmethod
    def is_hovered(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem):
        return

    @abc.abstractmethod
    def move_to(self, mouse_position: np.ndarray):
        return


class Vector(Element):
    def __init__(self, coordinates: np.ndarray):
        super().__init__()
        self.coordinates = coordinates

    def is_hovered(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem):
        pos = coordinate_system.transform(self.coordinates)
        diff = np.sum((mouse_position - pos)**2)
        return diff < 100

    def move_to(self, mouse_position: np.ndarray):
        self.coordinates = mouse_position.astype(dtype=float)

    def __repr__(self):
        return '[{:.2f} {:.2f}]'.format(self.coordinates[0], self.coordinates[1])


class UnitCircle(Element):
    def __init__(self, num_points=40):
        super().__init__()
        self.num_points = num_points
        space = np.linspace(0, np.pi * 2, num=num_points, endpoint=False)
        self.coordinates = np.stack([np.cos(space), np.sin(space)], axis=1)

    def is_hovered(self, mouse_position: np.ndarray, coordinate_system: CoordinateSystem):
        pos = coordinate_system.transform(self.coordinates)
        diff = np.sum((mouse_position - pos)**2, axis=1)
        return np.any(diff < 100)

    def move_to(self, mouse_position: np.ndarray):
        space = np.linspace(0, np.pi * 2, num=self.num_points, endpoint=False)
        self.coordinates = np.stack([np.cos(space) * mouse_position[0], np.sin(space) * mouse_position[1]], axis=1)

    def __repr__(self):
        return 'UnitCircle'


class Transform:
    def __init__(self):
        self.matrix = np.eye(2)

    def __repr__(self):
        # return '[[{:.2f}, {:.2f}], [{:.2f}, {:.2f}]]'.format(*self.matrix.flatten())
        return 'Matrix'


class Transformed:
    def __init__(self, element: Union[None, Vector, UnitCircle], transform: Optional[Transform]):
        self.element = element
        self.transform = transform

    def get_position(self):
        if self.element is not None and self.transform is not None:
            return (self.transform.matrix @ self.element.coordinates.T).T
        return None


class ElementBuffer:
    def __init__(self):
        self.elements = []
        self.transforms = []
        self.transformed = []

    def __iter__(self) -> Iterator[Element]:
        return iter(self.elements)

    def create_example_elements(self):
        self.elements.append(Vector(np.array([1, 1])))
        # self.elements.append(Vector(np.array([-1, 1])))
