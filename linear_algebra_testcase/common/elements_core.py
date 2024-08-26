import abc
import enum
from itertools import chain
from typing import List, Iterator

import numpy as np
import pygame as pg

from linear_algebra_testcase.dim2.coordinate_system import CoordinateSystem as CoordSystem2D
from linear_algebra_testcase.dim3.coordinate_system import CoordinateSystem as CoordSystem3D


DRAG_SNAP_DISTANCE = 0.07

RED = pg.Color(255, 80, 80)
GREEN = pg.Color(100, 220, 100)
BLUE = pg.Color(80, 80, 240)
CYAN = pg.Color(0, 220, 220)
YELLOW = pg.Color(220, 220, 0)
MAGENTA = pg.Color(220, 0, 220)

AXIS_COLORS = [CYAN, YELLOW, MAGENTA, BLUE]


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


CoordinateSystem = CoordSystem2D | CoordSystem3D


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
    def render(self, screen: pg.Surface, coordinate_system: CoordSystem2D | CoordSystem3D):
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
        if event.type == pg.KEYDOWN:
            if event.unicode == 'v':
                if self.is_hovered(mouse_position, coordinate_system):
                    self.visible = not self.visible

    def is_hovered(self, _mouse_position: np.ndarray, _coordinate_system: CoordinateSystem):
        return False


class ElementBuffer:
    def __init__(self):
        self.elements: List[Element] = []
        self.transforms: List[Element] = []
        self.transformed: List[Element] = []

    def __iter__(self) -> Iterator[Element]:
        return iter(self.elements)

    def create_example_elements(self):
        # self.elements.append(Vector('v1', np.array([1, 1])))
        pass

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
