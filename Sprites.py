from Settings import *
import pygame as pg
import random
from copy import deepcopy
from math import ceil


vec = pg.math.Vector2

class Player(pg.sprite.Sprite):

    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.last_update = 0
        self.changed_dir = False
        self.tiles = [[]]
        self.next_tile = (-1, -1) #x, y, coordinates of the tile to turn to

    def update(self):
        head = self.tiles[0][0]

        #move every tile
        for link in self.tiles:
            for i in range(1, len(link)):
                link[i].rect.center += link[0].vel
        head.rect.center += head.vel

        #if at the center move bodies to the next link
        if abs((head.rect.top // PLAYER_SIZE) * PLAYER_SIZE - head.rect.top) < SPEED and \
           abs((head.rect.left // PLAYER_SIZE) * PLAYER_SIZE - head.rect.left) < SPEED:
           print("move")
           self.print_tiles()
           for i in range(len(self.tiles) - 1):
               self.tiles[i].append(self.tiles[i+1].pop(1))

        #delete last link if empty
        if self.tiles[len(self.tiles) - 1] == []:
            self.tiles.pop()

        #turn if needed and in the center of the tile:
        if self.next_tile != (-1, -1):
            if (head.dir == "U" and head.rect.centery >= self.next_tile[1]) \
            or (head.dir == "D" and head.rect.centery <= self.next_tile[1]) \
            or (head.dir == "R" and head.rect.centerx >= self.next_tile[0]) \
            or (head.dir == "L" and head.rect.centerx <= self.next_tile[0]):
                print("turn")
                self.print_tiles()
                self.center_tiles()
                new_head = Body(self.game, head.rect.left, head.rect.top, "head", (0,0))
                self.tiles.insert(0, [new_head])
                self.tiles[0][0].vel = vec((self.next_tile[0] - head.rect.centerx) // PLAYER_SIZE, \
                                           (self.next_tile[1] - head.rect.centery) // PLAYER_SIZE)
                self.tiles[1][0].type = "point"
                self.next_tile = (-1, -1)
                self.print_tiles()

    def check_turn(self, key):
        #keys: 273-U; 274-D; 275-R; 276-L
        i = -1
        j = -1
        print(self.tiles[0][0].rect.left, self.tiles[0][0].rect.top)
        #don't turn if it's only head and it's not far enough
        if (len(self.tiles[0]) != 1) or \
           (len(self.tiles) >= 1 and sqrt((selt.tiles[0][0].rect.centerx - self.tiles[1][0].rect.centerx) ^ 2 + (selt.tiles[0][0].rect.centery - self.tiles[1][0].rect.centery) ^ 2) > PLAYER_SIZE * 0.25):
            if self.tiles[0][0].dir == "U" and (key == 275 or key == 276):
                j = ceil((self.tiles[0][0].rect.top + 0.25 * PLAYER_SIZE) / PLAYER_SIZE)
                if key == 275:
                    i = ceil(self.tiles[0][0].rect.right / PLAYER_SIZE) + 1
                if key == 276:
                    i = ceil(self.tiles[0][0].rect.right / PLAYER_SIZE) - 1
            if self.tiles[0][0].dir == "D" and (key == 275 or key == 276):
                j = ceil((self.tiles[0][0].rect.bottom - 0.25 * PLAYER_SIZE) / PLAYER_SIZE)
                if key == 275:
                    i = ceil(self.tiles[0][0].rect.right / PLAYER_SIZE) + 1
                if key == 276:
                    i = ceil(self.tiles[0][0].rect.right / PLAYER_SIZE) - 1
            if self.tiles[0][0].dir == "R" and (key == 273 or key == 274):
                i = ceil((self.tiles[0][0].rect.right - 0.25 * PLAYER_SIZE) / PLAYER_SIZE)
                if key == 273:
                    j = ceil(self.tiles[0][0].rect.bottom / PLAYER_SIZE) - 1
                if key == 274:
                    j = ceil(self.tiles[0][0].rect.bottom / PLAYER_SIZE) + 1
            if self.tiles[0][0].dir == "L" and (key == 273 or key == 274):
                i = ceil((self.tiles[0][0].rect.left + 0.25 * PLAYER_SIZE) / PLAYER_SIZE)
                if key == 273:
                    j = ceil(self.tiles[0][0].rect.bottom / PLAYER_SIZE) - 1
                if key == 274:
                    j = ceil(self.tiles[0][0].rect.bottom / PLAYER_SIZE) + 1
        self.next_tile = (i * PLAYER_SIZE - PLAYER_SIZE / 2, j * PLAYER_SIZE - PLAYER_SIZE / 2)

    def center_tiles(self):
        #align every tile with grid
        for link in self.tiles:
            for tile in link:
                tile.rect.left = ceil(tile.rect.left // PLAYER_SIZE) * PLAYER_SIZE
                tile.rect.top = ceil(tile.rect.top // PLAYER_SIZE) * PLAYER_SIZE

    def print_tiles(self):
        for link in self.tiles:
            a = []
            for tile in link:
                a.append([tile.rect.left, tile.rect.top, tile.type])
            print(a)

class Body(pg.sprite.Sprite):

    def __init__(self, game, x, y, type = "standard", vel = vec(0, 0)):
        self.groups = game.all_sprites, game.bodies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.type = type
        self.image = pg.Surface((PLAYER_SIZE, PLAYER_SIZE))
        if self.type == "head":
            self.image.fill(RED)
        elif self.type == "point":
            self.image.fill(BLUE)
        else:
            self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.number = len(self.game.player.tiles)
        self.vel = vel
        if self.type == "standard" or self.game.player.tiles == [[]]:
            self.game.player.tiles[len(self.game.player.tiles) - 1].append(self)
        else:
            self.game.player.tiles.append([self])

    def update(self):
        if self.type == "head":
            self.image.fill(RED)
        elif self.type == "point":
            self.image.fill(BLUE)
        else:
            self.image.fill(GREEN)

        if self.type == "head":
            if self.vel[0] == 0 and self.vel[1] > 0:
                self.dir = "D"
            elif self.vel[0] == 0 and self.vel[1] < 0:
                self.dir = "U"
            elif self.vel[0] > 0 and self.vel[1] == 0:
                self.dir = "R"
            elif self.vel[0] < 0 and self.vel[1] == 0:
                self.dir = "L"

class Fruit(pg.sprite.Sprite):

    def __init__(self, game):
        self.groups = game.all_sprites, game.fruits
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.create_time = pg.time.get_ticks()
        type = random.randint(1, BIG_FR_SPAWN_PCT)
        if type == 1:
            self.type = "big"
            self.image = pg.Surface((2 * PLAYER_SIZE, 2 * PLAYER_SIZE))
            self.image.fill(YELLOW)
        else:
            self.type = "normal"
            self.image = pg.Surface((PLAYER_SIZE, PLAYER_SIZE))
            self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        (self.rect.left, self.rect.top) = self.spawn(self.game.player.tiles, self.type)

    def spawn(self, tiles, type):
        board = []
        for i in range (0, WIDTH, PLAYER_SIZE):
            for j in range (0, HEIGHT, PLAYER_SIZE):
                board.append([i, j])
        if type == "normal":
            for body_tile in tiles:
                try:
                    board.remove([body_tile[0], body_tile[1]])
                except:
                    print(board)
                    print(body_tile)
                    print(tiles)
        elif type == "big":
            for body_tile in tiles:
                try:
                    board.remove([body_tile[0], body_tile[1]])
                    board.remove([body_tile[0] - PLAYER_SIZE, body_tile[1]])
                    board.remove([body_tile[0], body_tile[1] - PLAYER_SIZE])
                    board.remove([body_tile[0] - PLAYER_SIZE, body_tile[1] - PLAYER_SIZE])

                except:
                    pass
        fruit_tile = random.choice(board)
        return (fruit_tile[0], fruit_tile[1])

    def update(self):
        if self.type == "big" and \
           pg.time.get_ticks() - self.create_time > BIG_FR_TIME:
            self.kill()
