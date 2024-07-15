from __future__ import annotations
import numpy as np
from typing import Optional

from .matrices import create_affine_transformation

DEFAULT_SCREEN_SIZE = np.array([1280, 720])


class CoordinateSystem:
    def __init__(self, coord: Optional[np.ndarray] = None):
        if coord is None:
            coord = create_affine_transformation(DEFAULT_SCREEN_SIZE/2, (100, -100))
        self.coord: np.ndarray = coord

    @classmethod
    def create(cls, translation=0, scale=1) -> CoordinateSystem:
        mat = create_affine_transformation(translation, scale)
        return CoordinateSystem(mat)

    def zoom_out(self, focus_point=None):
        scale = 1 / 1.2

        scale_mat = create_affine_transformation(scale=scale)
        self.coord = self.coord @ scale_mat

        if focus_point is not None:
            self.translate((focus_point - self.get_zero_point()) * (1 - scale))

    def zoom_in(self, focus_point=None):
        scale = 1.2
        scale_mat = create_affine_transformation(scale=scale)
        self.coord = self.coord @ scale_mat
        if focus_point is not None:
            self.translate((focus_point - self.get_zero_point()) * (1 - scale))

    def translate(self, direction):
        direction *= np.array([1, -1])
        translation_mat = create_affine_transformation(translation=direction / self.coord[0, 0])
        self.coord = self.coord @ translation_mat

    def get_zero_point(self):
        """
        Get the zero point of the coordinate system in screen coordinates.
        """
        return self.transform(np.array([0.0, 0.0]))

    def transform(self, mat: np.ndarray):
        """
        Transform the given matrix with the internal coordinates.

        :param mat: A list of column vectors with shape [2, N]. For vectors shape should be [2, 1].
        :return: A list of column vectors with shape [2, N].
        """
        return transform(self.coord, mat)

    def transform_inverse(self, mat: np.ndarray):
        inv = np.linalg.pinv(self.coord)
        return transform(inv, mat)


def transform(transform_matrix: np.ndarray, mat: np.ndarray, perspective=False):
    """
    Transforms a given matrix with the given transformation matrix.
    Transformation matrix should be of shape [2, 2] or [3, 3]. If transformation matrix is of shape [3, 3] and the
    matrix to transform is of shape [2, N], matrix will be padded with ones to shape [3, N].
    If mat is of shape [2,] it will be converted to [2, 1].

    The calculation will be transform_matrix @ mat.

    :param transform_matrix: A np.ndarray with shape [2, 2] or [3, 3].
    :param mat: The matrix to convert of shape [2, N]. If mat is of shape [2,] it will be converted to [2, 1].
    :param perspective: If perspective is True and the transform_mat is of shape (3, 3), the x- and y-axis of the
                        resulting vector are divided by the resulting z axis.
    :return:
    """
    expanded = False
    if mat.shape == (2,):
        mat = mat.reshape((2, 1))
        expanded = True

    padded = False
    if transform_matrix.shape == (3, 3):
        mat = np.concatenate([mat, np.ones((1, mat.shape[1]))], axis=0)
        padded = True

    result = transform_matrix @ mat

    if expanded:
        result = result[:, 0]

    if padded:
        if perspective:
            result = result[:-1] / result[-1]
        else:
            result = result[:-1]
    return result


def transform_perspective(transform_matrix: np.ndarray, mat: np.ndarray) -> np.ndarray:
    """
    The same as transform, only with perspective set to true.
    """
    return transform(transform_matrix, mat, perspective=True)


def test_single_dimension():
    coordinate_system = CoordinateSystem()

    line_coords1 = np.array([100, -100])
    line_coords2 = np.array([-100, 100])
    line_coords1 = coordinate_system.transform(line_coords1)
    line_coords2 = coordinate_system.transform(line_coords2)
    assert tuple(line_coords1.shape) == (2,), line_coords1.shape
    assert tuple(line_coords2.shape) == (2,), line_coords2.shape


def test_multi_dimension():
    coordinate_system = CoordinateSystem()

    line_coords = np.array([[-100, -100], [100, 100], [200, 200]]).T
    line_coords = coordinate_system.transform(line_coords)
    assert line_coords.shape == (2, 3)
