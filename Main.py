import pygame as pg
from Settings import *
from Sprites import *
from math import sqrt
from random import randint

class Game:
    def __init__(self):
        #initialize
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.font_name = pg.font.match_font(FONT_NAME)

    #main loop
    def run(self):
        #Game loop
        self.clock.tick(FPS)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    #react on pressed key
    def events(self):
        #events game loop
        turn_keys = [pg.K_UP, pg.K_DOWN, pg.K_RIGHT, pg.K_LEFT]
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.playing = False
                self.quitgame()
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.playing = False
                self.show_menu()
            if event.type == pg.KEYDOWN and event.key in turn_keys:
                self.player.next_dir = self.select_next_direction(event.key, self.player.tiles[0].dir)

    #update game loop
    def update(self):
        #update game loop
        self.player.update()
        self.all_sprites.update()

        #check if dead
        if self.player.tiles == []:
            self.playing = False
            self.show_menu()

        #check self collision
        i = 5
        #can hit only third tile [h, s, c, s, c, s, s...]
        while i < len(self.player.tiles) and self.playing:
            head = self.player.tiles[0].rect.center
            tile = self.player.tiles[i].rect.center
            if self.distance(head, tile) < PLAYER_SIZE:
                self.playing = False
                self.show_menu()
            else:
                i += 1

        #check collision with wall
        head = self.player.tiles[0]
        if head.rect.left < 0 \
        or head.rect.right > WIDTH \
        or head.rect.top < OFFSET \
        or head.rect.bottom > HEIGHT:
            self.playing = False
            self.show_menu()

        #check collision with fruit
        hits = pg.sprite.spritecollide(self.player.tiles[0], self.fruits, True)
        if hits:
            for hit in hits:
                if hit.type == "standard":
                    self.score += 1
                    self.grow()
                    Fruit(self, "standard")
                    if self.player.starve_time < pg.time.get_ticks() + TIME_TO_STARVE:
                        self.player.starve_time = pg.time.get_ticks() + TIME_TO_STARVE
                        self.player.last_food_type = "standard"
                elif hit.type == "big":
                    self.score += 4
                    self.grow()
                    self.grow()
                    self.big_fruit_exist = False
                    self.player.starve_time = pg.time.get_ticks() + 2 * TIME_TO_STARVE
                    self.player.last_food_type = "big"

        #spawn big fruit
        if not self.big_fruit_exist:
            create = randint(1, BIG_FR_SPAWN_PCT)
            if create == 1:
                Fruit(self, "big")
                self.big_fruit_exist = True

        #spawn obstacle
        if OBSTACLE_NUMBER > len(self.list_obstacles):
            self.list_obstacles.append([randint(MIN_OBSTACLE, MAX_OBSTACLE)])
            self.list_obstacles[len(self.list_obstacles) - 1].append(Obstacle(self))
            for i in range(self.list_obstacles[-1:][0][0] - 1):
                self.list_obstacles[len(self.list_obstacles) - 1].append(Obstacle(self, False))

        #check collision with obstacle
        hits = pg.sprite.spritecollide(self.player.tiles[0], self.obstacles, False)
        if hits:
            self.playing = False
            self.show_menu()

    #draw all sprites, score
    def draw(self):
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        pg.draw.rect(self.screen, RAISIN_BLACK, (0, 0, WIDTH, OFFSET))
        self.draw_text('Score: ' + str(self.score), 22, WHITE, 40, 5)
        if self.player.last_food_type == "standard":
            pg.draw.rect(self.screen, RED, \
                        (WIDTH / 2 - 100, 5, 200 * (self.player.starve_time - pg.time.get_ticks()) / TIME_TO_STARVE, 15))
        elif self.player.last_food_type == "big":
            pg.draw.rect(self.screen, RED, \
                        (WIDTH / 2 - 100, 5, 200 * (self.player.starve_time - pg.time.get_ticks()) / 2 / TIME_TO_STARVE, 15))
        pg.draw.rect(self.screen, GREY, (WIDTH / 2 - 100, 5, 200, 15) , 1)
        if self.big_fruit_exist:
            pg.draw.rect(self.screen, GREEN, \
                         (WIDTH / 2 - 100, 25, 200 - 200 * (pg.time.get_ticks() - self.find_bf_time()) / BIG_FR_TIME, 15))
            pg.draw.rect(self.screen, GREY, (WIDTH / 2 - 100, 25, 200, 15) , 1)

        pg.display.flip()

    #create new game
    def new(self):
        self.dirname = path.dirname(__file__)
        self.tile_image = pg.transform.scale(pg.image.load(path.join(self.dirname, "square.png")).convert(), (25, 25))
        self.score = 0
        self.big_fruit_exist = False
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.fruits = pg.sprite.Group()
        self.obstacles = pg.sprite.Group()
        self.list_obstacles = []
        self.player = Player(self)
        self.player.tiles.append(Body(self, *HEAD_COORD, (0, -1), "head"))
        for body in BODY_COORD:
            self.player.tiles.append(Body(self, *body, (0, -1)))
        Fruit(self, "standard")
        self.run()

    #shows default menu: New game, Settings, Resources, Quit
    def show_menu(self):
        #pg.mixer.music.load(path.join(self.snd_dir, 'Of Monsters And Men - Little Talks.ogg'))
        #pg.mixer.music.set_volume(0.3)
        #pg.mixer.music.play(loops=-1)
        self.screen.fill(BGCOLOR)
        self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 6)
        self.waiting = True
        mouse = pg.mouse.get_pos()
        while self.waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.waiting = False
                    self.quitgame()
                if event.type == pg.KEYUP and event.key != pg.K_ESCAPE:
                    self.waiting = False
                    self.new()

            self.button("New Game", 32, WIDTH / 2, HEIGHT / 3, 100, 50, BGCOLOR, BGCOLOR, DARK_GREEN, GREEN, self.new)
            self.button("Settings", 32, WIDTH / 2, HEIGHT / 2, 100, 50, BGCOLOR, BGCOLOR, DARK_GREEN, GREEN)
            self.button("Resources", 32, WIDTH / 2, HEIGHT * 2 / 3, 100, 50, BGCOLOR, BGCOLOR, DARK_GREEN, GREEN)
            self.button("Quit", 32, WIDTH / 2, HEIGHT * 5 / 6, 100, 50, BGCOLOR, BGCOLOR, DARK_GREEN, GREEN, self.quitgame)
            pg.display.flip()
    #    pg.mixer.music.fadeout(500)

    def quitgame(self):
        pg.quit()
        quit()

    #draws text
    def draw_text(self, text, size, color, x, y):
        #draw text on the screen
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    #creates button
    def button(self, text, size, x, y, w, h, ic, ac, tic, tac, action = None):
        #x,y=midtop, ic/ac=inactive/active color
        mouse = pg.mouse.get_pos()
        click = pg.mouse.get_pressed()

        if x - w/2 < mouse[0] < x + w/2 and y < mouse[1] < y + h:
            pg.draw.rect(self.screen, ac, (x - w/2, y, w, h))
            self.draw_text(text, size, tac, x, y)
            if click[0] == 1 and action != None:
                self.waiting = False
                action()
        else:
            pg.draw.rect(self.screen, ic, (x - w/2, y, w, h))
            self.draw_text(text, size, tic, x, y)

    #finds time when big fruit was created
    def find_bf_time(self):
        for f in self.fruits:
            if f.type == "big":
                return f.create_time

    #checks if tile is in the body
    def exist(self, x, y):
        answer = False
        for tile in self.player.tiles:
            if tile.rect.left == x and tile.rect.top == y:
                answer = True
        return answer

    #return next direction based on pressed key
    def select_next_direction(self, key, h_dir):
        result_dir = h_dir
        turn_keys = [pg.K_UP, pg.K_DOWN, pg.K_RIGHT, pg.K_LEFT]
        directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]
        for i in range(len(turn_keys)):
            if key == turn_keys[i] and h_dir * -1 != vec(directions[i]):
                result_dir = vec(directions[i])
        return result_dir

    #returns distance btw two points
    def distance(self, a, b):
        return sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    #add a tile
    def grow(self):
        last = self.player.tiles[-1:][0]
        x = last.rect.left
        y = last.rect.top
        self.player.floating.append(Body(self, x,  y, last.dir))



g = Game()
g.show_menu()
pg.quit()
quit()
