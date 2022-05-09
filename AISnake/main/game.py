import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('fontovi.ttf', 25)


class Nasoka(Enum):
    Desno = 1
    Levo = 2
    Gore = 3
    Dole = 4


Tocka = namedtuple('Tocka', 'x, y')

Bela = (255, 255, 255)
Zolta = (219, 223, 21)
Zelena1 = (0, 255, 0)
Zelena2 = (0, 255, 50)
Crna = (0, 0, 0)

Blok_Golemina = 20
Brzina = 40


class ZmijaIgraAI:
    def __init__(self, w=640, h=480):
        self.sirina = w
        self.visina = h
        # inicializiran display
        self.display = pygame.display.set_mode((self.sirina, self.visina))
        pygame.display.set_caption('Snake')
        self.saat = pygame.time.Clock()
        self.resetiraj()

    def resetiraj(self):
        # inicializiraj pocetno stanje vo igrata
        self.nasoka = Nasoka.Desno
        self.glava = Tocka(self.sirina / 2, self.visina / 2)
        self.zmija = [self.glava,
                      Tocka(self.glava.x - Blok_Golemina, self.glava.y),
                      Tocka(self.glava.x - (2 * Blok_Golemina), self.glava.y)]
        self.rezultat = 0
        self.hrana = None
        self._lokacija_hrana()
        self.frame_iteracija = 0

    def _lokacija_hrana(self):
        x = random.randint(0, (self.sirina - Blok_Golemina) // Blok_Golemina) * Blok_Golemina
        y = random.randint(0, (self.visina - Blok_Golemina) // Blok_Golemina) * Blok_Golemina
        self.hrana = Tocka(x, y)
        if self.hrana in self.zmija:
            self._lokacija_hrana()

    def play_cekor(self, action):
        self.frame_iteracija += 1
        # vidi dali korisnikot ja isklucil igrata
        for nastan in pygame.event.get():
            if nastan.type == pygame.QUIT:
                pygame.quit()
                quit()
        # mrdni
        self._pomesti(action)  # updatiraj ja glavata
        self.zmija.insert(0, self.glava)
        # proveri dali igrata e zavrsena
        nagrada = 0
        igra_kraj = False
        if self.ima_sudar() or self.frame_iteracija > 100 * len(self.zmija):
            igra_kraj = True
            nagrada = -10
            return nagrada, igra_kraj, self.rezultat
        # stavi hrana na nova lokacija ili samo pomesti ja zmijata
        if self.glava == self.hrana:
            self.rezultat += 1
            nagrada = 10
            self._lokacija_hrana()
        else:
            self.zmija.pop()
        # updejtiraj UI i saatot
        self._updatejtiraj_ui()
        self.saat.tick(Brzina)
        # vrni dali e kraj i rezultat
        return nagrada, igra_kraj, self.rezultat

    def ima_sudar(self, tc=None):
        if tc is None:
            tc = self.glava
        # zmijata udri zid
        if tc.x > self.sirina - Blok_Golemina or tc.x < 0 or tc.y > self.visina - Blok_Golemina or tc.y < 0:
            return True
        # zmijata se udri sama
        if tc in self.zmija[1:]:
            return True
        return False

    def _updatejtiraj_ui(self):
        self.display.fill(Crna)
        for pt in self.zmija:
            pygame.draw.rect(self.display, Zelena1, pygame.Rect(pt.x, pt.y, Blok_Golemina, Blok_Golemina))
            pygame.draw.rect(self.display, Zelena2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))
        pygame.draw.rect(self.display, Zolta, pygame.Rect(self.hrana.x, self.hrana.y, Blok_Golemina, Blok_Golemina))
        text = font.render("Score: " + str(self.rezultat), True, Bela)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _pomesti(self, akcija):
        # [pravo, desno, levo]
        saat_smer = [Nasoka.Desno, Nasoka.Dole, Nasoka.Levo, Nasoka.Gore]
        idx = saat_smer.index(self.nasoka)
        if np.array_equal(akcija, [1, 0, 0]):
            nova_nasoka = saat_smer[idx]
        elif np.array_equal(akcija, [0, 1, 0]):
            nov_index = (idx + 1) % 4
            nova_nasoka = saat_smer[nov_index]
        else:  # [0, 0, 1]
            nov_index = (idx - 1) % 4
            nova_nasoka = saat_smer[nov_index]
        self.nasoka = nova_nasoka
        x = self.glava.x
        y = self.glava.y
        if self.nasoka == Nasoka.Desno:
            x += Blok_Golemina
        elif self.nasoka == Nasoka.Levo:
            x -= Blok_Golemina
        elif self.nasoka == Nasoka.Dole:
            y += Blok_Golemina
        elif self.nasoka == Nasoka.Gore:
            y -= Blok_Golemina
        self.glava = Tocka(x, y)
