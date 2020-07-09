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

    def run(self):
        #Game loop
        self.clock.tick(FPS)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        #update game loop
        self.player.update()
        self.all_sprites.update()

        #check self collision
        i = 5
        #can hit only third tile [h, s, c, s, c, s, s...]
        while i < len(self.player.tiles) and self.playing:
            if sqrt((self.player.tiles[0].rect.left - self.player.tiles[i].rect.left) ** 2 +
                    (self.player.tiles[0].rect.top - self.player.tiles[i].rect.top) ** 2) < PLAYER_SIZE:
                self.playing = False
                self.show_menu()
            else:
                i += 1

        #check collision with wall
        head = self.player.tiles[0]
        if head.rect.left < 0 \
        or head.rect.right > WIDTH \
        or head.rect.top < 0 \
        or head.rect.bottom > HEIGHT:
            self.playing = False
            self.show_menu()

        #check collision with fruit
        hits = pg.sprite.spritecollide(self.player.tiles[0], self.fruits, True)
        if hits:
            for hit in hits:
                self.new_bodies += 1
                if hit.type == "standard":
                    self.score += 1
                    Fruit(self, "standard")
                elif hit.type == "big":
                    self.score += 4
                    self.big_fruit_exist = False

        #spawn big fruit
        if not self.big_fruit_exist:
            create = randint(1, BIG_FR_SPAWN_PCT)
            if create == 1:
                Fruit(self, "big")
                self.big_fruit_exist = True

        #grow Snake, when there is space to grow


    def events(self):
        #events game loop
        turn_keys = [pg.K_UP, pg.K_DOWN, pg.K_RIGHT, pg.K_LEFT]
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.quitgame()
            if event.type == pg.KEYDOWN and event.key in turn_keys:
                self.player.select_next_tile(event.key)

    def draw(self):
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        self.draw_text('Score: ' + str(self.score), 22, WHITE, 40, 5)

        """
        #draw grid
        for i in range(1, WIDTH // PLAYER_SIZE):
            pg.draw.line(self.screen, RED, (PLAYER_SIZE * i, 0), (PLAYER_SIZE * i, HEIGHT))
        for j in range(1, HEIGHT // PLAYER_SIZE):
            pg.draw.line(self.screen, RED, (0, PLAYER_SIZE * j), (WIDTH, PLAYER_SIZE * j))
        """

        pg.display.flip()

    def new(self):
        self.score = 0
        self.new_bodies = 0
        self.big_fruit_exist = False
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.bodies = pg.sprite.Group()
        self.fruits = pg.sprite.Group()
        self.player = Player(self)
        self.player.tiles.append(Body(self, *HEAD_COORD, "head", (0, -1)))#, vec(0, -1) * SPEED)])
        for body in BODY_COORD:
            self.player.tiles.append(Body(self, *body, "standard", (0, -1)))
        Fruit(self, "standard")
        self.run()

    def show_menu(self):
    #    pg.mixer.music.load(path.join(self.snd_dir, 'Of Monsters And Men - Little Talks.ogg'))
    #    pg.mixer.music.set_volume(0.3)
    #    pg.mixer.music.play(loops=-1)
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
                if event.type == pg.KEYUP:
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

    def draw_text(self, text, size, color, x, y):
        #draw text on the screen
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

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


g = Game()
g.show_menu()
pg.quit()
quit()
