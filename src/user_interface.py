import pygame as pg


class UserInterface:
    def __init__(self):
        self.showing = False
        self.menu_rect = pg.Rect(10, 10, 40, 40)
        self.menu_image = self._create_menu_image()

    def _create_menu_image(self):
        menu_image = pg.Surface((self.menu_rect.width,  self.menu_rect.height))
        menu_image.fill(pg.Color(0, 0, 0))
        d = 40 // 6
        pg.draw.rect(
            menu_image, pg.Color(140, 140, 140), pg.Rect(0, 0, self.menu_rect.width, self.menu_rect.height),
            border_radius=4
        )
        pg.draw.rect(menu_image, pg.Color(20, 20, 20), pg.Rect(d, d+3, 40-2*d, d-2), border_radius=2)
        pg.draw.rect(menu_image, pg.Color(20, 20, 20), pg.Rect(d, d*3, 40-2*d, d-2), border_radius=2)
        pg.draw.rect(menu_image, pg.Color(20, 20, 20), pg.Rect(d, d*5-3, 40-2*d, d-2), border_radius=2)
        return menu_image

    def toggle(self):
        self.showing = not self.showing
