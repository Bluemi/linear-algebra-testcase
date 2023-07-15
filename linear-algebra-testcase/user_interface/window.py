from typing import Callable, Optional

import pygame as pg

from utils import gray


def on_close_noop(_text):
    pass


class Window:
    def __init__(self, on_close: Optional[Callable] = None, text: str = '', fontsize: int = 18,
                 text_color: pg.Color = None, font_name: str = ''):
        self.text = text
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
        screen.blit(font, small_rect.move(3, 12))

    def handle_event(self, event: pg.event.Event):
        if event.type == pg.KEYDOWN:
            if event.key == 27:
                self.on_close(self.text)
                self.has_to_close = True
            else:
                if event.key == 8:
                    self.text = self.text[:-1]
                elif event.key == 127:
                    self.text = ''
                elif event.unicode:
                    self.text += event.unicode
