from typing import Iterable

import numpy as np
import pygame as pg
from pygame import Surface, Color

from controller import Controller
from coordinate_system import CoordinateSystem, DEFAULT_SCREEN_SIZE, transform as transform_helper
from elements import ElementBuffer, Vector, Transformed, MultiVectorObject, CustomTransformed, RenderKind
from user_interface import UserInterface

TARGET_NUM_POINTS = 12
TARGET_DIVIDENDS = [1, 2, 4, 5, 10]


RED = pg.Color(255, 80, 80)
GREEN = pg.Color(100, 220, 100)


def render(
    screen: Surface, coordinate_system: CoordinateSystem, element_buffer: ElementBuffer, render_font,
    controller: Controller, user_interface: UserInterface
):
    screen.fill("black")
    draw_coordinate_system(screen, coordinate_system, render_font)
    draw_elements(screen, coordinate_system, element_buffer)
    draw_user_interface(screen, user_interface, controller, render_font)


def draw_coordinate_system(screen: Surface, coordinate_system: CoordinateSystem, render_font):
    def adapt_quotient(quotient):
        if quotient <= 0:
            raise ValueError('Invalid quotient: {}'.format(quotient))
        numb_ten_potency = 0
        while quotient > 10:
            quotient *= 0.1
            numb_ten_potency += 1
        while quotient < 1:
            quotient *= 10
            numb_ten_potency -= 1

        diffs = [abs(quotient - target) for target in TARGET_DIVIDENDS]
        index = np.argmin(diffs)
        best_fitting = TARGET_DIVIDENDS[index] * (10 ** numb_ten_potency)

        return best_fitting

    extreme_points = np.array([
        [0, 0],
        [screen.get_width(), screen.get_height()]
    ]).T
    extreme_points = coordinate_system.transform_inverse(extreme_points).T
    target_num_points = TARGET_NUM_POINTS * screen.get_width() // DEFAULT_SCREEN_SIZE[0]
    target_dividend = (extreme_points[1, 0] - extreme_points[0, 0]) / target_num_points
    # extreme_points = np.trunc(extreme_points).astype(int)
    dividend = adapt_quotient(target_dividend)
    x_minimum = np.round(extreme_points[0, 0] / dividend) * dividend
    x_maximum = np.round(extreme_points[1, 0] / dividend) * dividend
    x_points = np.arange(x_minimum, x_maximum + dividend, dividend)
    for x in x_points:
        vertical_lines = np.array([[x, 0], [x, 0]])
        transformed_vertical_lines = coordinate_system.transform(vertical_lines.T).T
        transformed_vertical_lines[:, 1] = [0, screen.get_height()]
        color = Color(30, 30, 30)
        if x == 0:
            color = Color(50, 50, 50)
        pg.draw.line(screen, color, transformed_vertical_lines[0], transformed_vertical_lines[1])

    y_minimum = np.round(extreme_points[1, 1] / dividend) * dividend
    y_maximum = np.round(extreme_points[0, 1] / dividend) * dividend
    y_points = np.arange(y_minimum, y_maximum + dividend, dividend)

    for y in y_points:
        horizontal_lines = np.array([[extreme_points[0, 0], y], [extreme_points[1, 0], y]])
        transformed_horizontal_lines = coordinate_system.transform(horizontal_lines.T).T
        transformed_horizontal_lines[:, 0] = [0, screen.get_width()]
        color = Color(30, 30, 30)
        if y == 0:
            color = Color(50, 50, 50)
        pg.draw.line(screen, color, transformed_horizontal_lines[0], transformed_horizontal_lines[1])

    # draw numbers
    zero_point = coordinate_system.transform(np.array([0, 0]))

    if 0 < zero_point[1] < screen.get_height():
        for x in x_points:
            if abs(x) > 10 ** -5:
                float_format = '{:.2f}' if abs(x) > 1 else '{:.2}'
                font = render_font.render(float_format.format(x), True, pg.Color(120, 120, 120), pg.Color(0, 0, 0, 0))
                pos = coordinate_system.transform(np.array([x, 0]))
                pos += 10
                screen.blit(font, pos)

    if 0 < zero_point[0] < screen.get_width():
        for y in y_points:
            if abs(y) > 10 ** -5:
                float_format = '{:.2f}' if abs(y) > 1 else '{:.2}'
                font = render_font.render(float_format.format(y), True, pg.Color(120, 120, 120), pg.Color(0, 0, 0, 0))
                pos = coordinate_system.transform(np.array([0, y]))
                pos += 10
                screen.blit(font, pos)


def draw_user_interface(screen: Surface, user_interface: UserInterface, controller: Controller,
                        render_font: pg.font.Font):
    user_interface.render(screen)

    if controller.get_definition_for is not None:
        draw_text_input(screen, controller, render_font)


def draw_text_input(screen: Surface, controller: Controller, render_font):
    pg.draw.rect(screen, pg.Color(128, 128, 128), pg.Rect(200, 200, screen.get_width() - 400, 200))
    small_rect = pg.Rect(220, 200+80, screen.get_width() - 440, 40)
    pg.draw.rect(screen, pg.Color(28, 28, 28), small_rect)

    elem: CustomTransformed = controller.get_definition_for

    font = render_font.render(elem.definition, True, pg.Color(220, 220, 220))
    screen.blit(font, small_rect.move(3, 12))


def draw_elements(screen: Surface, coordinate_system: CoordinateSystem, element_buffer: ElementBuffer):
    zero_point = coordinate_system.transform(np.array([0, 0]))

    for element in element_buffer.elements:
        if isinstance(element, Vector):
            transformed_vec = coordinate_system.transform(element.get_array())
            width = 3 if element.hovered else 1
            if element.render_kind == RenderKind.POINT:
                pg.draw.circle(screen, GREEN, transformed_vec, width)
            elif element.render_kind == RenderKind.LINE:
                pg.draw.line(screen, GREEN, zero_point, transformed_vec, width=width)

        if isinstance(element, MultiVectorObject):
            transformed_vec = coordinate_system.transform(element.get_array()).T
            width = 4 if element.hovered else 3
            for point in transformed_vec:
                if element.render_kind == RenderKind.POINT:
                    pg.draw.circle(screen, GREEN, point, width)
                elif element.render_kind == RenderKind.LINE:
                    pg.draw.line(screen, GREEN, zero_point, point, width=1)

    for element in element_buffer.transformed:
        if isinstance(element, Transformed):
            new_vec = element.get_position()
            if new_vec is not None:
                if isinstance(element.element, Vector):
                    transformed_vec = coordinate_system.transform(new_vec).flatten()
                    if element.render_kind == RenderKind.POINT:
                        pg.draw.circle(screen, RED, transformed_vec, 3)
                    elif element.render_kind == RenderKind.LINE:
                        pg.draw.line(screen, RED, zero_point, transformed_vec, width=1)
                elif isinstance(element.element, MultiVectorObject):
                    transformed_vec = coordinate_system.transform(new_vec).T
                    for point in transformed_vec:
                        if element.render_kind == RenderKind.POINT:
                            pg.draw.circle(screen, RED, point, 3)
                        elif element.render_kind == RenderKind.LINE:
                            pg.draw.line(screen, RED, zero_point, point, width=1)
        elif isinstance(element, CustomTransformed):
            if element.compiled_definition:
                # build eval locals
                eval_locals = {'np': np, 'mm': transform_helper, 'norm': normalize_vec}
                for e in element_buffer.elements:
                    eval_locals[e.name] = e.get_array()
                for t in element_buffer.transforms:
                    eval_locals[t.name] = t.get_array()
                for t in element_buffer.transformed:
                    eval_locals[t.name] = t.get_array()

                result = None
                element.error = None
                try:
                    result = eval(element.compiled_definition, {}, eval_locals)
                except Exception as e:
                    element.error = repr(e)
                    print(element.error)

                element.last_result = result
                if not isinstance(result, np.ndarray) and isinstance(result, Iterable):
                    result = np.array(result)
                if isinstance(result, np.ndarray):
                    element.last_result = result
                    if result.shape == (2,):
                        result = np.expand_dims(result, 0)
                    if result.shape[0] == 2 and len(result.shape) == 2:
                        transformed_vecs = coordinate_system.transform(result).T
                        # width = 3 if element.hovered else 1
                        for point in transformed_vecs:
                            if element.render_kind == RenderKind.POINT:
                                pg.draw.circle(screen, RED, point, 3)
                            elif element.render_kind == RenderKind.LINE:
                                pg.draw.line(screen, RED, zero_point, point, width=1)
                    else:
                        element.error = 'Invalid result shape: {}'.format(result.shape)
                elif result is not None:
                    element.error = 'result is not numpy array'


def normalize_vec(vec):
    return vec / (np.linalg.norm(vec) + 0.000000001)
