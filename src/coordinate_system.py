from __future__ import annotations
import numpy as np
import numbers
from typing import Optional

from matrices import create_affine_transformation

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
    def create(cls, translation=0, scale=1) -> CoordinateSystem:
        mat = create_affine_transformation(translation, scale)
        return CoordinateSystem(mat)

    def zoom_out(self):
        scale = 1 / 1.2
        scale_mat = create_affine_transformation(scale=scale)
        self.coord = scale_mat @ self.coord

    def zoom_in(self):
        scale = 1.2
        scale_mat = create_affine_transformation(scale=scale)
        self.coord = scale_mat @ self.coord

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
