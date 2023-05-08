from __future__ import annotations
import numpy as np
import numbers
from typing import Optional

from misc import debug

DEFAULT_SCREEN_SIZE = np.array([1280, 720])


class CoordinateSystem:
    def __init__(self, coord: Optional[np.ndarray] = None):
        if coord is None:
            scale_coord = np.array(
                [[100, 0, 0],
                 [0, 100, 0],
                 [0, 0, 1]]
            ).T
            translate_coord = np.array(
                [[1, 0, DEFAULT_SCREEN_SIZE[0]/2],
                 [0, 1, DEFAULT_SCREEN_SIZE[1]/2],
                 [0, 0, 1]]
            ).T
            coord = scale_coord @ translate_coord
        self.coord: np.ndarray = coord

    @classmethod
    def create(cls, scale=1, translation=1) -> CoordinateSystem:
        if isinstance(scale, numbers.Number):
            scale = (scale, scale)
        scale_coord = np.array(
            [[scale[0], 0, 0],
             [0, scale[1], 0],
             [0, 0, 1]]
        ).T
        if isinstance(translation, numbers.Number):
            translation = (translation, translation)
        translate_coord = np.array(
            [[1, 0, translation[0]],
             [0, 1, translation[1]],
             [0, 0, 1]]
        ).T
        return CoordinateSystem(scale_coord @ translate_coord)

    def __call__(self, mat: np.ndarray):
        """
        Transform the given matrix with the internal coordinates.

        :param mat: A list of column vectors with shape [N, 2] or [2,].
        :return: A list of column vectors with shape [N, 2] or [2,].
        """
        expanded = False
        if len(mat.shape) == 1:
            expanded = True
            mat = np.expand_dims(mat, axis=0)
        result = np.concatenate([mat, np.ones((mat.shape[0], 1))], axis=1) @ self.coord
        if expanded:
            return result[0, :-1]
        else:
            return result[:, :-1]


def test_single_dimension():
    coordinate_system = CoordinateSystem()

    line_coords1 = np.array([100, -100])
    line_coords2 = np.array([-100, 100])
    line_coords1 = coordinate_system(line_coords1.T)
    line_coords2 = coordinate_system(line_coords2.T)
    assert tuple(line_coords1.shape) == (2,), line_coords1.shape
    assert tuple(line_coords2.shape) == (2,), line_coords2.shape


def test_multi_dimension():
    coordinate_system = CoordinateSystem()

    line_coords = np.array([[-100, -100], [100, 100], [200, 200]])
    line_coords = coordinate_system(line_coords)
    assert tuple(line_coords.shape) == (3, 2)
