import pygame as pg
import sys
import inspect
import numpy as np


def gray(b=127) -> pg.Color:
    return pg.Color(b, b, b)


def format_float(f):
    return '{:.2f}'.format(f)


def debug(arg):
    """
    Print name of arg and arg.
    :param arg: The argument to print
    """
    # noinspection PyUnresolvedReferences,PyProtectedMember
    fr = sys._getframe(1)  # type: frame
    code = inspect.getsource(fr).split('\n')
    line = code[fr.f_lineno - fr.f_code.co_firstlineno]
    varname = line.partition('debug(')[2].rpartition(')')[0]
    f_string = '{}: {}'
    if isinstance(arg, np.ndarray):
        f_string = '{}:\n{}'
    print(f_string.format(varname, arg))


def normalize_vec(vec):
    return vec / (np.linalg.norm(vec) + 0.000000001)
