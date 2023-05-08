import numpy as np


class ElementBuffer:
    def __init__(self):
        self.vectors = []

    def create_example_elements(self):
        self.vectors.append(np.array([1, 1]))
