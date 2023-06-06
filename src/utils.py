import pygame as pg


def gray(b=127) -> pg.Color:
    return pg.Color(b, b, b)

def format_float(f):
    return '{:.2f}'.format(f)
