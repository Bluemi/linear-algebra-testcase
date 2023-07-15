import numbers

import numpy as np


def create_affine_transformation(translation=0, scale=1) -> np.ndarray:
    if isinstance(scale, numbers.Number):
        scale = (scale, scale)
    scale_coord = np.array(
        [[scale[0], 0, 0],
         [0, scale[1], 0],
         [0, 0, 1]]
    )
    if isinstance(translation, numbers.Number):
        translation = (translation, translation)
    translate_coord = np.array(
        [[1, 0, translation[0]],
         [0, 1, translation[1]],
         [0, 0, 1]]
    )
    return translate_coord @ scale_coord
