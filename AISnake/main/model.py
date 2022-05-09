import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os


class Linearen_QNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x

    def zacuvaj(self, ime_datoteka='model.pth'):
        model_datoteka_pat = './model'
        if not os.path.exists(model_datoteka_pat):
            os.makedirs(model_datoteka_pat)
        ime_datoteka = os.path.join(model_datoteka_pat, ime_datoteka)
        torch.save(self.state_dict(), ime_datoteka)


class QTrener:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def treniraj_cekor(self, stanje, akcija, nagrada, naredno_stanje, kraj):
        stanje = torch.tensor(stanje, dtype=torch.float)
        naredno_stanje = torch.tensor(naredno_stanje, dtype=torch.float)
        akcija = torch.tensor(akcija, dtype=torch.long)
        nagrada = torch.tensor(nagrada, dtype=torch.float)

        if len(stanje.shape) == 1:
            stanje = torch.unsqueeze(stanje, 0)
            naredno_stanje = torch.unsqueeze(naredno_stanje, 0)
            akcija = torch.unsqueeze(akcija, 0)
            nagrada = torch.unsqueeze(nagrada, 0)
            kraj = (kraj,)

        # predvideni Q vrednost so momentalno stanje
        pred = self.model(stanje)

        meta = pred.clone()
        for idx in range(len(kraj)):
            Q_nov = nagrada[idx]
            if not kraj[idx]:
                Q_nov = nagrada[idx] + self.gamma * torch.max(self.model(naredno_stanje[idx]))
            meta[idx][torch.argmax(akcija[idx]).item()] = Q_nov
        self.optimizer.zero_grad()
        greska = self.criterion(meta, pred)
        greska.backward()
        self.optimizer.step()
