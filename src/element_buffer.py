import numpy as np


class ElementBuffer:
    def __init__(self):
        self.vectors = []
        self.points = None
        self.points_transformed = None
        self.eig_vecs = None

    def create_example_elements(self):
        # self.vectors.append(np.array([1, 1]))

        # create circle
        angles = np.linspace(0, 2*np.pi, num=360*10, endpoint=False)
        x = np.cos(angles)
        y = np.sin(angles)
        self.points = np.stack([x, y], axis=1)

        transform = np.random.normal(size=(2, 2))
        # transform = np.array([[0.5, 1], [1, 0.5]])
        self.points_transformed = self.points @ transform.T

        eig_values, eig_vecs = np.linalg.eig(transform)
        print('eig values:', eig_values)
        print('eig vecs:', eig_vecs)
        self.eig_vecs = (eig_vecs * eig_values).T
        print('eig vecs scaled:', self.eig_vecs)

