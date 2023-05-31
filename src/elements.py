from typing import Iterator

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
        return 'Vector [{:.2f} {:.2f}]'.format(self.coordinates[0], self.coordinates[1])


class Transform:
    def __init__(self):
        self.matrix = np.eye(2)


class ElementBuffer:
    def __init__(self):
        self.elements = []
        self.transforms = []

    def __iter__(self) -> Iterator[Element]:
        return iter(self.elements)

    def create_example_elements(self):
        self.elements.append(Vector(np.array([1, 1])))
        self.elements.append(Vector(np.array([-1, 1])))
