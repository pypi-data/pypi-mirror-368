from functools import lru_cache

import pygame

from mlgame.game.paia_game import GameResultState, GameStatus
from .env import *


class Point(pygame.sprite.Sprite):
    def __init__(self, game, coordinate):
        self.group = game.all_points
        pygame.sprite.Sprite.__init__(self, self.group)
        self.game = game
        self.x, self.y = (coordinate[0] - TILESIZE / PPM, -coordinate[1] + TILESIZE / PPM)
        # self.x, self.y = (coordinate[0] + TILESIZE / (2 * PPM), -coordinate[1] - TILESIZE / (2 * PPM))

    def get_info(self):
        return {
            "coordinate": ((self.x + 0.5) * 5, (self.y - 0.5) * 5)
        }

    def get_progress_data(self):
        asset_data = {}
        return asset_data


def trnsfer_box2d_to_pygame(coordinate):
    '''
    :param coordinate: vertice of body of box2d object
    :return: center of pygame rect
    '''
    return ((coordinate[0]) * PPM, (0 - coordinate[1]) * PPM)


class End_point(Point):
    def __init__(self, game, coordinate):
        Point.__init__(self, game, coordinate)
        self.size = TILESIZE * 3
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.rect.x, self.rect.y = trnsfer_box2d_to_pygame((self.x, self.y))

    def update(self, *args, **kwargs) -> None:
        self.detect_cars_collision()

    def detect_cars_collision(self):
        hits = pygame.sprite.spritecollide(self, self.game.cars, False)
        for hit in hits:
            if hit.is_running:
                hit.end_frame = self.game.frame
                hit.check_point += 1

                hit.is_completed = True
                self.game.eliminated_user.append(hit)  # TODO #外部注入
                if len(self.game.cars)==1:
                    self.game.state = GameResultState.PASSED
                else:
                    self.game.state = GameResultState.FINISH

                hit.is_running = False
                hit.status = GameStatus.GAME_PASS

    def get_progress_data(self):
        asset_data = {"type": "image",
                      "x": self.rect.x,
                      "y": self.rect.y,
                      "width": self.size,
                      "height": self.size,
                      "image_id": "endpoint",
                      "angle": 0}
        return asset_data


class Check_point(Point):

    def __init__(self, game, coordinate):
        Point.__init__(self, game, coordinate)
        self.size = TILESIZE * 3
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.rect.x, self.rect.y = trnsfer_box2d_to_pygame((self.x, self.y))

        self.car_has_hit = []
        self._touched = False
        self._game = game

    def update(self, *args, **kwargs) -> None:
        self.detect_cars_collision()

    def detect_cars_collision(self):
        hits = pygame.sprite.spritecollide(self, self.game.cars, False)
        if hits:
            self._touched = True
        else:
            self._touched = False

        for hit in hits:
            if hit.status and hit not in self.car_has_hit:
                hit.check_point += 1
                hit.end_frame = self.game.frame
                self.car_has_hit.append(hit)

    def get_progress_data(self):
        # asset_data = {"type": "rect",
        #               "x": self.rect.x,
        #               "y": self.rect.y,
        #               "width": 60,
        #               "height": 60,
        #               "color": RED,
        #               "angle": 0}
        asset_data = {"type": "image",
                      "x": self.rect.x,
                      "y": self.rect.y,
                      "width": self.size,
                      "height": self.size,
                      "image_id": self._image_id(self._touched),
                      "angle": 0}
        return asset_data

    @lru_cache
    def _image_id(self, touched: bool):
        if touched:
            return "checkpoint_2"
        else:
            return "checkpoint"


class Outside_point(Point):
    '''
    if car colliding these point, car will be swich to start point
    '''

    def __init__(self, game, coordinate):
        Point.__init__(self, game, coordinate)
        # self.image = pygame.Surface((TILESIZE, TILESIZE))
        # self.image.fill(BLUE)
        # self.rect = self.image.get_rect()
        self.rect = pygame.Rect(self.x, self.y, TILESIZE * 3, TILESIZE * 3)

    def update(self, *args, **kwargs) -> None:
        self.detect_cars_collision()

    def detect_cars_collision(self):
        hits = pygame.sprite.spritecollide(self, self.game.cars, False)
        for hit in hits:
            if hit.status:
                hit.body.position = (hit.x, hit.y)
                hit.body.linearVelocity = 0, 0
                pass
