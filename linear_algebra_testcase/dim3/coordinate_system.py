from __future__ import annotations
import numpy as np
from scipy.spatial.transform import Rotation
from typing import Optional

DEFAULT_SCREEN_SIZE = np.array([1280, 720])


class CoordinateSystem:
    def __init__(self, position: Optional[np.ndarray] = None, rotation: Optional[Rotation] = None):
        self.position = position if position is not None else np.array([0.0, 0.0, 0.0])
        self.rotation = rotation if rotation is not None else Rotation.from_quat([0.0, 0.0, 0.0, 1.0])
        self.field_of_view = 60 / 180 * np.pi  # 60 degrees in radians
        self.aspect_ratio = DEFAULT_SCREEN_SIZE[0] / DEFAULT_SCREEN_SIZE[1]
        self.near = 0.1
        self.far = 100.0

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
        :return: A list of vectors with shape [N, 3].
        """
        if vecs.shape == (3,):
            vecs = vecs.reshape(1, 3)

        # pad to 4D vec
        vecs = np.pad(vecs, ((0, 0), (0, 1)), 'constant', constant_values=1.0)

        # first translate
        translation_matrix = np.eye(4, dtype=float)
        translation_matrix[:3, 3] = -self.position

        # second rotate
        # rotation_matrix = np.eye(4, dtype=float)
        # rotation_matrix[:3, :3] = self.rotation.inv().as_matrix()

        # view_matrix = rotation_matrix @ translation_matrix
        view_matrix = translation_matrix
        print('\nview_matrix\n', view_matrix)

        projection_matrix = get_perspective_matrix(self.field_of_view, 16 / 9, self.near, self.far)
        print('\nprojection_matrix\n', projection_matrix)

        print('\nvecs\n', vecs)
        proj_vecs = (projection_matrix @ view_matrix @ vecs.T).T
        print('\nproj_vecs\n', proj_vecs)
        proj_vecs[:, :3] /= proj_vecs[:, 3]
        # TODO: perspective
        # TODO: Clipping

        return proj_vecs.T[:, :3]


def get_perspective_matrix(angle: float, ratio: float, near: float, far: float) -> np.ndarray:
    perspective = np.zeros((4, 4))
    tan_half_angle = np.tan(angle / 2)

    perspective[0, 0] = 1 / (ratio * tan_half_angle)
    perspective[1, 1] = 1 / tan_half_angle
    perspective[2, 2] = -(far + near) / (far - near)
    perspective[2, 3] = -1
    perspective[3, 2] = -(2 * far * near) / (far - near)
    return perspective


def test_coordinate_system():
    system = CoordinateSystem(np.array([0.0, 0.0, 2.0]), Rotation.from_quat([0.0, 0.0, 0.0, 1.0]))

    # vecs = np.random.random((5, 3))
    vecs = np.eye(3)

    transformed_vecs = system.transform(vecs)

    print('\ntransformed_vecs\n', transformed_vecs, '\nshape:', transformed_vecs.shape)


if __name__ == '__main__':
    test_coordinate_system()
