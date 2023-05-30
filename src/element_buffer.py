import numpy as np


class ElementBuffer:
    def __init__(self):
        self.vectors = []
        self.vectors_transformed = []
        self.points = []
        self.points_transformed = []
        self.eig_vecs = []

        self.elements = []

    def create_example_elements(self):
        # create circle
        # angles = np.linspace(0, 2*np.pi, num=360*10, endpoint=False)
        # x = np.cos(angles)
        # y = np.sin(angles)
        # self.points = np.stack([x, y], axis=1)

        # self.generate_transform()
        self.generate_rotation_vec()

    def generate_transform(self, default=True, verbose=False):
        if default:
            transform = np.array([[0.5, 1], [1, 0.5]])
        else:
            transform = np.random.normal(size=(2, 2))
        if verbose:
            print('transform:', transform)
        self.points_transformed = self.points @ transform.T

        eig_values, eig_vecs = np.linalg.eig(transform)
        if verbose:
            print('eig values:', eig_values)
            print('eig vecs:', eig_vecs)
        self.eig_vecs = (eig_vecs * eig_values).T
        if verbose:
            print('eig vecs scaled:', self.eig_vecs)

    def generate_rotation_vec(self):
        vec = np.random.normal(size=2)

        angle = np.pi / 2
        rotation_matrix = np.array([
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle), np.cos(angle)]
        ])

        self.vectors = [vec]

        transformed_vec = rotation_matrix @ vec
        self.vectors_transformed = [transformed_vec]


class Element:
    def __init__(self):
        pass


class Vector(Element):
    def __init__(self):
        super().__init__()