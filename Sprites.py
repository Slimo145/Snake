from Settings import *
import pygame as pg
from random import choice
from copy import deepcopy
from math import ceil, sqrt


vec = pg.math.Vector2

class Player(pg.sprite.Sprite):

    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.last_update = 0
        self.changed_dir = False
        self.tiles = []
        self.cur_tile = INIT_DIRECTION
        self.next_tile = INIT_DIRECTION #x, y, top,left coordinates of the tile to turn to
        self.cur_dir = vec(0, -1)
        self.next_dir = vec(0, -1)

    def update(self):
        #move every tile
        for i in range(len(self.tiles)):
            tile = self.tiles[i]
            if tile.type == "standard":
                dist = self.distance((self.tiles[i-1].rect.left, self.tiles[i-1].rect.top), (tile.rect.left, tile.rect.top))
                tile.rect.left += SPEED * (self.tiles[i-1].rect.left - tile.rect.left) / dist
                tile.rect.top += SPEED * (self.tiles[i-1].rect.top - tile.rect.top) / dist
        self.tiles[0].rect.center += SPEED * self.cur_dir

        head = self.tiles[0]
        #check if at the center of the tile
        if abs(head.rect.left // PLAYER_SIZE - head.rect.left / PLAYER_SIZE) < SPEED / PLAYER_SIZE / 2 \
        and abs(head.rect.top // PLAYER_SIZE - head.rect.top / PLAYER_SIZE) < SPEED / PLAYER_SIZE / 2:
            i = 0
            while i < len(self.tiles):
                #move tile to the next link
                if self.tiles[i].type == "corner":
                    self.tiles[i], self.tiles[i+1] = self.tiles[i+1], self.tiles[i]
                    i += 1
                i += 1
            #add corner
            if self.cur_dir != self.next_dir:
                self.tiles.insert(1, Body(self.game, head.rect.left, head.rect.top, "corner"))
            self.cur_dir = self.next_dir

        #if last link is empty, delete corner
        if self.tiles[-1:][0].type == "corner":
            self.tiles[-1:][0].kill()
            self.tiles.pop()


    def select_next_tile(self, key):
        turn_keys = [pg.K_UP, pg.K_DOWN, pg.K_RIGHT, pg.K_LEFT]
        directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]
        for i in range(len(turn_keys)):
            if key == turn_keys[i] and self.cur_dir * -1 != vec(directions[i]):
                self.next_dir = vec(directions[i])


    def distance(self, a, b):  #a, b - tuples
        return sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


    def print_tiles(self):
        a = []
        for tile in self.tiles:
            a += [tile.rect.left, tile.rect.top, tile.type]
        print(a)

class Body(pg.sprite.Sprite):

    def __init__(self, game, x, y, type = "standard"):#, vel = vec(0, 0)):
        self.groups = game.all_sprites, game.bodies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.type = type
        self.image = pg.Surface((PLAYER_SIZE, PLAYER_SIZE))
        if self.type == "head":
            self.image.fill(RED)
        elif self.type == "corner":
            self.image.fill(BLUE)
        else:
            self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        #self.number = len(self.game.player.tiles)
        #self.vel = vel

    def update(self):
        if self.type == "head":
            self.image.fill(RED)
        elif self.type == "corner":
            self.image.fill(BLUE)
        else:
            self.image.fill(GREEN)

class Fruit(pg.sprite.Sprite):

    def __init__(self, game, type):
        self.groups = game.all_sprites, game.fruits
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.create_time = pg.time.get_ticks()
        self.type = type
        if self.type == "big":
            self.image = pg.Surface((2 * PLAYER_SIZE, 2 * PLAYER_SIZE))
            self.image.fill(YELLOW)
        else:
            self.image = pg.Surface((PLAYER_SIZE, PLAYER_SIZE))
            self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        (self.rect.left, self.rect.top) = self.spawn(self.game.player.tiles, self.type)

    def spawn(self, tiles, type):
        board = []
        for i in range (0, WIDTH, PLAYER_SIZE):
            for j in range (0, HEIGHT, PLAYER_SIZE):
                board.append([i, j])

        big_fruit_tiles = [(0, 0), (0, -PLAYER_SIZE), (-PLAYER_SIZE, 0), (-PLAYER_SIZE, -PLAYER_SIZE)]
        for body_tile in tiles:
            x = body_tile.rect.left // PLAYER_SIZE * PLAYER_SIZE
            y = body_tile.rect.top // PLAYER_SIZE * PLAYER_SIZE
            if type == "standard":
                if [x, y] in board:
                    board.remove([x, y])
            if type == "big":
                for t in big_fruit_tiles:
                    if [x + t[0], y + t[1]] in board:
                        board.remove([x + t[0], y + t[1]])

        fruit_tile = choice(board)
        return (fruit_tile[0], fruit_tile[1])

    def update(self):
        if self.type == "big" and \
           pg.time.get_ticks() - self.create_time > BIG_FR_TIME:
            self.game.big_fruit_exist = False
            self.kill()
