from __future__ import annotations
import numpy as np
from scipy.spatial.transform import Rotation
from typing import Optional

from linear_algebra_testcase.utils import normalize_vec

DEFAULT_SCREEN_SIZE = np.array([1280, 720])


class CoordinateSystem:
    def __init__(self, position: Optional[np.ndarray] = None, rotation: Optional[Rotation] = None):
        self.position = position if position is not None else np.array([0.0, 0.0, 0.0])
        self.rotation = rotation if rotation is not None else Rotation.from_quat([0.0, 0.0, 0.0, 1.0])
        self.field_of_view = 60 / 180 * np.pi  # 60 degrees in radians
        self.aspect_ratio = DEFAULT_SCREEN_SIZE[0] / DEFAULT_SCREEN_SIZE[1]
        self.near = 0.1
        self.far = 100.0
        self.screen_size = np.copy(DEFAULT_SCREEN_SIZE)

    def rotate(self, rotation: Rotation):
        self.rotation = self.rotation * rotation

    def get_zero_point(self):
        """
        Get the zero point of the coordinate system in screen coordinates.
        """
        return self.transform(np.array([0.0, 0.0, 0.0]))

    def transform(self, vecs: np.ndarray) -> np.ndarray:
        """
        Transform the given world coordinates to screen coordinates.

        :param vecs: A list of vectors with shape [N, 3] or [3,].
        :return: A list of vectors with shape [N, 3]. The z coordinate can be ignored for rendering on screen
        """
        if vecs.shape == (3,):
            vecs = vecs.reshape(1, 3)

        # pad to 4D vec
        vecs = np.pad(vecs, ((0, 0), (0, 1)), 'constant', constant_values=1.0)

        # first translate
        translation_matrix = np.eye(4, dtype=float)
        translation_matrix[:3, 3] = -self.position

        # second rotate
        rotation_matrix = np.eye(4, dtype=float)
        rotation_matrix[:3, :3] = self.rotation.inv().as_matrix()

        view_matrix = rotation_matrix @ translation_matrix
        # print('\nview_matrix\n', view_matrix)

        projection_matrix = get_perspective_matrix(self.field_of_view, 16 / 9, self.near, self.far)
        # print('\nprojection_matrix\n', projection_matrix)

        # print('\nvecs\n', vecs)
        proj_vecs = (projection_matrix @ view_matrix @ vecs.T).T
        # print('\nproj_vecs\n', proj_vecs)

        # perspective division
        proj_vecs[:, :3] = proj_vecs[:, :3] / proj_vecs[:, 3].reshape(-1, 1)

        # convert to screen space
        proj_vecs[:, :2] = (proj_vecs[:, :2] + 1) / 2.0
        proj_vecs[:, 0] *= self.screen_size[0]
        proj_vecs[:, 1] *= self.screen_size[1]

        return proj_vecs[:, :3]


def get_perspective_matrix(angle: float, ratio: float, near: float, far: float) -> np.ndarray:
    perspective = np.zeros((4, 4))
    tan_half_angle = np.tan(angle / 2)

    perspective[0, 0] = 1 / (ratio * tan_half_angle)
    perspective[1, 1] = 1 / tan_half_angle
    perspective[2, 2] = -(far + near) / (far - near)
    perspective[2, 3] = -1
    perspective[3, 2] = -(2 * far * near) / (far - near)
    return perspective.T  # TODO place values at the right spot immediately


def get_lookat(position: np.ndarray, target: np.ndarray, world_up: np.ndarray):
    # 1. Position = known
    # 2. Calculate cameraDirection
    z_axis = normalize_vec(position - target)
    # 3. Get positive right axis vector
    x_axis = normalize_vec(np.cross(normalize_vec(world_up), z_axis))
    # 4. Calculate camera up vector
    y_axis = np.cross(z_axis, x_axis)

    # Create translation and rotation matrix
    # In glm we access elements as mat[col][row] due to column-major layout
    translation = np.eye(4)  # Identity matrix by default
    translation[3][0] = -position[0]  # Third column, first row
    translation[3][1] = -position[1]
    translation[3][2] = -position[2]
    rotation = np.eye(4)
    rotation[0][0] = x_axis[0]  # First column, first row
    rotation[1][0] = x_axis[1]
    rotation[2][0] = x_axis[2]
    rotation[0][1] = y_axis[0]  # First column, second row
    rotation[1][1] = y_axis[1]
    rotation[2][1] = y_axis[2]
    rotation[0][2] = z_axis[0]  # First column, third row
    rotation[1][2] = z_axis[1]
    rotation[2][2] = z_axis[2]

    # print('translation:\n', translation)
    # print('\nrotation:\n', rotation)

    # Return lookAt matrix as combination of translation and rotation matrix
    return (rotation @ translation).T  # Remember to read from right to left (first translation then rotation)


def test_coordinate_system():
    system = CoordinateSystem(np.array([0.0, 0.0, 2.0]), Rotation.from_quat([0.0, 0.0, 0.0, 1.0]))

    # vecs = np.random.random((5, 3))
    vecs = np.eye(3)

    transformed_vecs = system.transform(vecs)

    print('\ntransformed_vecs\n', transformed_vecs, '\nshape:', transformed_vecs.shape)

    screen_coordinates = np.round(transformed_vecs[:, :2]).astype(int)

    print('screen_coordinates:', screen_coordinates)


if __name__ == '__main__':
    test_coordinate_system()
