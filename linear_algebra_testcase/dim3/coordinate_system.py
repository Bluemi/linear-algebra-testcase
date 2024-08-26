from __future__ import annotations
import numpy as np
from scipy.spatial.transform import Rotation
from typing import Optional

from linear_algebra_testcase.common.utils import normalize_vec, np_cross

DEFAULT_SCREEN_SIZE = np.array([1280, 720])


class CoordinateSystem:
    def __init__(self, position: Optional[np.ndarray] = None):
        self.position = position if position is not None else np.array([0.0, 0.0, 0.0])
        self.screen_size = np.copy(DEFAULT_SCREEN_SIZE)

        # rotations
        self.yaw_rotation = Rotation.from_quat([0.0, 0.0, 0.0, 1.0])
        self.pitch_rotation = Rotation.from_quat([0.0, 0.0, 0.0, 1.0])
        self.rotation = self.yaw_rotation * self.pitch_rotation

        # projection info
        self.field_of_view = 60 / 180 * np.pi  # 60 degrees in radians
        self.aspect_ratio = DEFAULT_SCREEN_SIZE[0] / DEFAULT_SCREEN_SIZE[1]
        self.near = 0.1
        self.far = 100.0

        # transformation matrices
        self.projection_matrix = self.get_projection_matrix()
        self.transformation_matrix = self.get_projection_matrix() @ self.get_view_matrix()

    def rotate(self, rotation: np.ndarray):
        self.yaw_rotation = self.yaw_rotation * Rotation.from_quat([0.0, rotation[0], 0.0, 1.0])
        self.pitch_rotation = self.pitch_rotation * Rotation.from_quat([rotation[1], 0.0, 0.0, 1.0])
        self.rotation = self.yaw_rotation * self.pitch_rotation
        self._update_matrix()

    def move(self, direction: np.ndarray, absolute: bool = False):
        if not absolute:
            direction = self.rotation.apply(direction)
        self.position += direction
        self._update_matrix()

    def _update_matrix(self):
        self.transformation_matrix = self.projection_matrix @ self.get_view_matrix()

    def get_zero_point(self):
        """
        Get the zero point of the coordinate system in screen coordinates.
        """
        return self.transform(np.array([0.0, 0.0, 0.0]), clip=False)

    def transform(self, vecs: np.ndarray, clip: bool = True) -> np.ndarray:
        """
        Transform the given world coordinates to screen coordinates.

        :param vecs: A list of vectors with shape [N, 3] or [3,].
        :param clip: Filter out vectors that are outside the clip space.
        :return: A list of vectors with shape [N, 3]. The z coordinate can be ignored for rendering on screen
        """
        # prepare vecs
        if vecs.shape == (3,):
            vecs = vecs.reshape(1, 3)
        # pad to 4D vec
        vecs = np.pad(vecs, ((0, 0), (0, 1)), 'constant', constant_values=1.0)

        # projection
        proj_vecs = (self.transformation_matrix @ vecs.T).T

        # perspective division
        proj_vecs[:, :3] = proj_vecs[:, :3] / proj_vecs[:, 3].reshape(-1, 1)
        proj_vecs = proj_vecs[:, :3]  # remove w-coordinate

        # clip outside vectors
        if clip:
            valid_indices = np.all(np.logical_and(proj_vecs < 1.0, proj_vecs > -1.0), axis=1)
            proj_vecs = proj_vecs[valid_indices]

        # convert to screen space
        proj_vecs[:, 1] *= -1.0  # invert y-axis
        proj_vecs[:, :2] = (proj_vecs[:, :2] + 1) / 2.0  # scale from [-1, 1] to [0, 1]
        proj_vecs[:, 0] *= self.screen_size[0]  # scale to screen size
        proj_vecs[:, 1] *= self.screen_size[1]  # scale to screen size

        return proj_vecs

    def get_projection_matrix(self):
        projection_matrix = get_perspective_matrix(self.field_of_view, 16 / 9, self.near, self.far)
        return projection_matrix

    def get_view_matrix(self):
        # first translate
        translation_matrix = np.eye(4, dtype=float)
        translation_matrix[:3, 3] = -self.position
        # second rotate
        rotation_matrix = np.eye(4, dtype=float)
        rotation_matrix[:3, :3] = self.rotation.inv().as_matrix()
        view_matrix = rotation_matrix @ translation_matrix
        return view_matrix


def get_perspective_matrix(angle: float, ratio: float, near: float, far: float) -> np.ndarray:
    perspective = np.zeros((4, 4))
    tan_half_angle = np.tan(angle / 2)

    perspective[0, 0] = 1 / (ratio * tan_half_angle)
    perspective[1, 1] = 1 / tan_half_angle
    perspective[2, 2] = -(far + near) / (far - near)
    perspective[3, 2] = -1
    perspective[2, 3] = -(2 * far * near) / (far - near)
    return perspective


def get_lookat(position: np.ndarray, target: np.ndarray, world_up: np.ndarray):
    # calculate camera-direction
    z_axis = normalize_vec(position - target)
    # get positive right axis vector
    x_axis = normalize_vec(np_cross(normalize_vec(world_up), z_axis))
    # calculate camera up vector
    y_axis = np_cross(z_axis, x_axis)

    # create translation and rotation matrix
    translation = np.eye(4)
    # translation[3, :3] = -position
    translation[:3, 3] = -position

    rotation = np.eye(4)
    rotation[0, :3] = x_axis
    rotation[1, :3] = y_axis
    rotation[2, :3] = z_axis

    return translation @ rotation


def test_coordinate_system():
    system = CoordinateSystem(np.array([0.0, 0.0, 2.0]))

    # vecs = np.random.random((5, 3))
    vecs = np.eye(3)

    transformed_vecs = system.transform(vecs)

    print('\ntransformed_vecs\n', transformed_vecs, '\nshape:', transformed_vecs.shape)

    screen_coordinates = np.round(transformed_vecs[:, :2]).astype(int)

    print('screen_coordinates:', screen_coordinates)


if __name__ == '__main__':
    test_coordinate_system()
