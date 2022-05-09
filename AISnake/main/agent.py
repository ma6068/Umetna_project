import torch
import random
import numpy as np
from collections import deque
from AISnake.main.game import ZmijaIgraAI, Nasoka, Tocka
from AISnake.main.model import Linearen_QNet, QTrener

Max_Memorija = 100_000
Blok_Golemina = 1000
LR = 0.001


class Agent:
    def __init__(self):
        self.broj_igri = 0
        self.epsilon = 0  
        self.gamma = 0.9  
        self.memorija = deque(maxlen=Max_Memorija) 
        self.model = Linearen_QNet(11, 256, 3)
        self.qtrainer = QTrener(self.model, lr=LR, gamma=self.gamma)

    def zemi_stanje(self, game):
        glava = game.zmija[0]
        tocka_levo = Tocka(glava.x - 20, glava.y)
        tocka_desno = Tocka(glava.x + 20, glava.y)
        tocka_gore = Tocka(glava.x, glava.y - 20)
        tocka_dole = Tocka(glava.x, glava.y + 20)

        nasoka_levo = game.nasoka == Nasoka.Levo
        nasoka_desno = game.nasoka == Nasoka.Desno
        nasoka_gore = game.nasoka == Nasoka.Gore
        nagoka_dole = game.nasoka == Nasoka.Dole

        stanje = [
            # Opasno pravo
            (nasoka_desno and game.ima_sudar(tocka_desno)) or
            (nasoka_levo and game.ima_sudar(tocka_levo)) or
            (nasoka_gore and game.ima_sudar(tocka_gore)) or
            (nagoka_dole and game.ima_sudar(tocka_dole)),

            # Opasno desno
            (nasoka_gore and game.ima_sudar(tocka_desno)) or
            (nagoka_dole and game.ima_sudar(tocka_levo)) or
            (nasoka_levo and game.ima_sudar(tocka_gore)) or
            (nasoka_desno and game.ima_sudar(tocka_dole)),

            # Opasno levo
            (nagoka_dole and game.ima_sudar(tocka_desno)) or
            (nasoka_gore and game.ima_sudar(tocka_levo)) or
            (nasoka_desno and game.ima_sudar(tocka_gore)) or
            (nasoka_levo and game.ima_sudar(tocka_dole)),

            # Nasoka na dvizenje
            nasoka_levo,
            nasoka_desno,
            nasoka_gore,
            nagoka_dole,

            # Lokacija na hrana
            game.hrana.x < game.glava.x,  # hrana levo
            game.hrana.x > game.glava.x,  # hrana desno
            game.hrana.y < game.glava.y,  # hrana gore
            game.hrana.y > game.glava.y   # hrana dole
        ]

        return np.array(stanje, dtype=int)

    def zapomni(self, stanje, akcija, nagrada, naredno_stanje, kraj):
        self.memorija.append((stanje, akcija, nagrada, naredno_stanje, kraj))

    def istreniraj_golema_memorija(self):
        if len(self.memorija) > Blok_Golemina:
            mini_sample = random.sample(self.memorija, Blok_Golemina)
        else:
            mini_sample = self.memorija
        stanja, akcii, nagradi, naredni_stanja, kraevi = zip(*mini_sample)
        self.qtrainer.treniraj_cekor(stanja, akcii, nagradi, naredni_stanja, kraevi)

    def istreniraj_mala_memorija(self, stanje, akcija, nagrada, naredno_stanje, kraj):
        self.qtrainer.treniraj_cekor(stanje, akcija, nagrada, naredno_stanje, kraj)

    def zemi_akcija(self, stanje):
        self.epsilon = 80 - self.broj_igri
        finalen_cekor = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            pokret = random.randint(0, 2)
            finalen_cekor[pokret] = 1
        else:
            state0 = torch.tensor(stanje, dtype=torch.float)
            predviduvanje = self.model(state0)
            pokret = torch.argmax(predviduvanje).item()
            finalen_cekor[pokret] = 1
        return finalen_cekor


def treniraj():
    rekord = 0
    agent = Agent()
    game = ZmijaIgraAI()
    while True:
        # zemi go staroto stanje
        staro_stanje = agent.zemi_stanje(game)
        # zemi go pokretot
        konecen_pokret = agent.zemi_akcija(staro_stanje)
        # izvrsi go cekorot i zemi go novoto stanje
        nagrada, kraj, rezultat = game.play_cekor(konecen_pokret)
        novo_stanje = agent.zemi_stanje(game)
        # train mala memorija
        agent.istreniraj_mala_memorija(staro_stanje, konecen_pokret, nagrada, novo_stanje, kraj)
        # zapomni
        agent.zapomni(staro_stanje, konecen_pokret, nagrada, novo_stanje, kraj)
        if kraj:
            # natreniraj golema memorija
            game.resetiraj()
            agent.broj_igri += 1
            agent.istreniraj_golema_memorija()
            if rezultat > rekord:
                rekord = rezultat
                agent.model.zacuvaj()
            print('Igra', agent.broj_igri, 'Rezultat', rezultat, 'Rekord:', rekord)


if __name__ == '__main__':
    treniraj()
