from Settings import *
import pygame as pg
from random import choice, randint
from copy import deepcopy
from math import ceil, sqrt
from os import path


vec = pg.math.Vector2

class Player():

    def __init__(self, game):
        self.game = game
        self.tiles = []
        self.floating = []
        self.next_dir = vec(0, -1)
        self.starve_time = pg.time.get_ticks() + TIME_TO_STARVE
        self.last_food_type = "standard"

    #updates the snake
    def update(self):
        #move every tile
        for tile in self.tiles:
            if tile.type != "corner":
                tile.rect.center += SPEED * tile.dir

        head = self.tiles[0]
        #check if at the center of the tile
        if self.check_if_center(head):
            self.align_tiles()
            #start at the end, because otherwise getting wrong direction if two consequent turns
            i = len(self.tiles) - 1
            while i > 0:
                #move tile to the next link
                if self.tiles[i].type == "corner":
                    self.tiles[i], self.tiles[i+1] = self.tiles[i+1], self.tiles[i]
                    self.tiles[i].dir = self.tiles[i-1].dir
                    i -= 1
                i -= 1
            #add corner
            if head.dir != self.next_dir:
                self.tiles.insert(1, Body(self.game, head.rect.left, head.rect.top, self.next_dir, "corner"))
            head.dir = self.next_dir

            if self.floating != []:
                self.tiles.append(self.floating.pop(0))

        #delete tile if starving
        if pg.time.get_ticks() > self.starve_time:
            self.tiles.pop().kill()
            self.starve_time += TIME_TO_STARVE
            self.last_food_type = "standard"

        #if last link is empty, delete corner
        if self.tiles != []:
            if self.tiles[-1:][0].type == "corner":
                self.tiles.pop().kill()

    #checks if tiles are aligned with the grid
    def check_if_center(self, head):
        A = self.find_closest(head.rect.left, head.rect.top)
        A_h = (head.rect.left, head.rect.top)
        at_center = False
        if self.distance(A, A_h) < 0.1 or \
          (self.distance(A, A_h) < SPEED and \
           self.distance(A, A_h) > self.distance(A, A_h + 0.1 * SPEED * head.dir)):
               at_center = True
        return at_center

    #finds distance btw two points
    def distance(self, a, b):  #a, b - tuples
        return sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    #finds the closest corner to the point
    def find_closest(self, x, y):
        x0 = x // PLAYER_SIZE * PLAYER_SIZE
        y0 = y // PLAYER_SIZE * PLAYER_SIZE
        points = [(x0, y0), (x0 + PLAYER_SIZE, y0), (x0, y0 + PLAYER_SIZE), (x0 + PLAYER_SIZE, y0 + PLAYER_SIZE)]
        min_d = 1000
        point = (0, 0)
        for p in points:
            if self.distance((x, y), p) < min_d:
                point = p
                min_d = self.distance((x, y), p)
        return point

    #move snake, so it is aligned with the grid
    def align_tiles(self):
        disp = (0, 0)
        for tile in self.tiles:
            p = self.find_closest(tile.rect.left, tile.rect.top)
            tile.rect.left = p[0]
            tile.rect.top = p[1]


class Body(pg.sprite.Sprite):

    def __init__(self, game, x, y, dir = (0, 0), type = "standard"):#, vel = vec(0, 0)):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.type = type
        self.image = self.game.tile_image
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.dir = vec(dir)

    def update(self):
        pass


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

        #where big fruit can't spawn
        big_fruit_tiles = [(0, 0), (0, -PLAYER_SIZE), (-PLAYER_SIZE, 0), (-PLAYER_SIZE, -PLAYER_SIZE)]
        #big fruit tiles
        fruit_area = [(0, 0), (PLAYER_SIZE, 0), (0, PLAYER_SIZE), (PLAYER_SIZE, PLAYER_SIZE)]


        #remove body tiles
        for body_tile in tiles:
            x = body_tile.rect.left // PLAYER_SIZE * PLAYER_SIZE
            y = body_tile.rect.top // PLAYER_SIZE * PLAYER_SIZE
            if type == "standard":
                if [x, y] in board:
                    board.remove([x, y])
            elif type == "big":
                for t in big_fruit_tiles:
                    if [x + t[0], y + t[1]] in board:
                        board.remove([x + t[0], y + t[1]])

        #remove fruits
        for f in self.game.fruits:
            x = f.rect.left
            y = f.rect.top
            if f.type == "standard":
                if type == "standard":
                    if [x, y] in board:
                        board.remove([x, y])
                elif type == "big":
                    for t in big_fruit_tiles:
                        if [x + t[0], y + t[1]] in board:
                            board.remove([x + t[0], y + t[1]])
            elif f.type == "big":
                for d in fruit_area:
                    if type == "standard":
                        if [x, y] in board:
                            board.remove([x, y])
                    elif type == "big":
                        for t in big_fruit_tiles:
                            if [x + d[0] + t[0], y + d[1] + t[1]] in board:
                                board.remove([x + d[0] + t[0], y + d[1] + t[1]])

        #remove obstacles
        for obs in self.game.obstacles:
            x = obs.rect.left
            y = obs.rect.top
            if type == "standard":
                if [x, y] in board:
                    board.remove([x, y])
            elif type == "big":
                for t in big_fruit_tiles:
                    if [x + t[0], y + t[1]] in board:
                        board.remove([x + t[0], y + t[1]])

        #remove border if big fruit
        if type == "big":
            for i in range(0, WIDTH, PLAYER_SIZE):
                if [i, HEIGHT - PLAYER_SIZE] in board:
                    board.remove([i, HEIGHT - PLAYER_SIZE])
            for i in range(0, HEIGHT, 25):
                if [WIDTH - PLAYER_SIZE, i] in board:
                    board.remove([WIDTH - PLAYER_SIZE, i])

        fruit_tile = choice(board)
        return (fruit_tile[0], fruit_tile[1])

    def update(self):
        if self.type == "big" and \
           pg.time.get_ticks() - self.create_time > BIG_FR_TIME:
            self.game.big_fruit_exist = False
            self.kill()

class Obstacle(pg.sprite.Sprite):

    def __init__(self, game, new = True):
        self.groups = game.all_sprites, game.obstacles
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(CHESTNUT_BROWN)
        self.rect = self.image.get_rect()
        (self.rect.left, self.rect.top) = self.select_tile(new)

    def select_tile(self, new):
        board = []
        if new:
            for i in range (0, WIDTH, PLAYER_SIZE):
                for j in range (0, HEIGHT, PLAYER_SIZE):
                    board.append([i, j])

            #remove body tiles
            for body_tile in self.game.player.tiles:
                x = body_tile.rect.left // PLAYER_SIZE * PLAYER_SIZE
                y = body_tile.rect.top // PLAYER_SIZE * PLAYER_SIZE
                if [x, y] in board:
                    board.remove([x, y])

            #remove obstacles
            for group in self.game.list_obstacles:
                for i in range(1, len(group)):
                    obs = group[i]
                    if [obs.rect.left, obs.rect.top] in board:
                        board.remove([obs.rect.left, obs.rect.top])

            #remove fruits
            fruit_area = [(0, 0), (PLAYER_SIZE, 0), (0, PLAYER_SIZE), (PLAYER_SIZE, PLAYER_SIZE)]
            for f in self.game.fruits:
                x = f.rect.left
                y = f.rect.top
                if f.type == "standard":
                    if [x, y] in board:
                        board.remove([x, y])
                elif f.type == "big":
                    for d in fruit_area:
                        if [x + d[0], y + d[1]] in board:
                            board.remove([x + d[0], y + d[1]])

        else:
            board = []
            directions = [(0, -PLAYER_SIZE), (0, PLAYER_SIZE), (PLAYER_SIZE, 0), (-PLAYER_SIZE, 0)]
            group = self.game.list_obstacles[-1:][0]
            for i in range(1, len(group)):
                obs = group[i]
                x = obs.rect.left
                y = obs.rect.top
                for d in directions:
                    if not [x + d[0], y + d[1]] in board and \
                       not self.exist(x + d[0], y + d[1]) and \
                       (x + d[0] >= 0 and x + d[0] <= WIDTH - PLAYER_SIZE and \
                        y + d[1] >= 0 and y + d[1] <= HEIGHT - PLAYER_SIZE):
                       board.append([x + d[0], y + d[1]])

        tile = choice(board)

        return tile

    def exist(self, x, y):
        exist = False
        for group in self.game.list_obstacles:
            for i in range(1, len(group)):
                if group[i].rect.left == x and group[i].rect.top == y:
                    exist = True

        return exist
