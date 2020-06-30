from Settings import *
import pygame as pg
import random

vec = pg.math.Vector2

class Head(pg.sprite.Sprite):

    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.last_update = 0
        self.changed_dir = False
        self.image = pg.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.vel = vec(0, PLAYER_SIZE)
        self.tiles = [(self.rect.left, self.rect.top)]

    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_update > MOVING_TIME:
            self.last_update = now
            self.changed_dir = False
            self.rect.center += self.vel
            self.tiles.pop()
            self.tiles.insert(0, (self.rect.left, self.rect.top))
        #print(self.tiles)

    def turn(self, key):
        if not self.changed_dir:
            if key == 273 and self.vel != (0, PLAYER_SIZE):
                self.vel = vec(0, -PLAYER_SIZE) #go up
                self.changed_dir = True
            if key == 274 and self.vel != (0, -PLAYER_SIZE):
                self.vel = vec(0, PLAYER_SIZE)  #go down
                self.changed_dir = True
            if key == 275 and self.vel != (-PLAYER_SIZE, 0):
                self.vel = vec(PLAYER_SIZE, 0)  #go right
                self.changed_dir = True
            if key == 276 and self.vel != (PLAYER_SIZE, 0):
                self.vel = vec(-PLAYER_SIZE, 0)  #go left
                self.changed_dir = True

class Body(pg.sprite.Sprite):

    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.bodies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.number = len(self.game.player.tiles)
        self.game.player.tiles.append((x, y))

    def update(self):
        (self.rect.left, self.rect.top) = self.game.player.tiles[self.number]

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
