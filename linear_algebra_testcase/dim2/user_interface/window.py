from typing import Callable, Optional

import pygame as pg

from ..utils import gray


def on_close_noop(_text):
    pass


class Window:
    def __init__(self, on_close: Optional[Callable] = None, text: str = '', fontsize: int = 18,
                 text_color: pg.Color = None, font_name: str = ''):
        self.text = text
        self.cursor_position = len(text)
        self.fontsize = fontsize
        self.text_color = text_color or gray(220)
        self.font_name = font_name or pg.font.get_default_font()
        self.font = pg.font.Font(self.font_name, self.fontsize)
        self.on_close: Callable = on_close or on_close_noop
        self.has_to_close = False

    def render(self, screen: pg.Surface):
        pg.draw.rect(screen, pg.Color(128, 128, 128), pg.Rect(200, 200, screen.get_width() - 400, 200))
        small_rect = pg.Rect(220, 200+80, screen.get_width() - 440, 40)
        pg.draw.rect(screen, pg.Color(28, 28, 28), small_rect)

        font = self.font.render(self.text, True, pg.Color(220, 220, 220))
        cursor_position = self.font.size(self.text[:self.cursor_position])[0]
        cursor_top_spacing = 4
        cursor_rect = small_rect.move(cursor_position+3, cursor_top_spacing)
        cursor_rect.width = 2
        cursor_rect.height = cursor_rect.height - 2 * cursor_top_spacing
        pg.draw.rect(screen, gray(100), cursor_rect)
        screen.blit(font, small_rect.move(3, 12))

    def handle_event(self, event: pg.event.Event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.on_close(self.text)
                self.has_to_close = True
            else:
                if event.key == pg.K_BACKSPACE:
                    if len(self.text) >= self.cursor_position > 0:
                        l = list(self.text)
                        del l[self.cursor_position-1]
                        self.text = ''.join(l)
                        self.cursor_position -= 1
                elif event.key == pg.K_DELETE:
                    if self.cursor_position < len(self.text):
                        l = list(self.text)
                        del l[self.cursor_position]
                        self.text = ''.join(l)
                elif event.key == pg.K_LEFT:
                    self.cursor_position = max(self.cursor_position-1, 0)
                elif event.key == pg.K_RIGHT:
                    self.cursor_position = min(self.cursor_position+1, len(self.text))
                elif event.unicode:
                    l = list(self.text)
                    l.insert(self.cursor_position, event.unicode)
                    self.text = ''.join(l)
                    self.cursor_position += 1
