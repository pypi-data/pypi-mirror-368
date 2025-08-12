import torch.nn as nn

class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.hidden1 = nn.Linear(8, 1024)
        self.act = nn.ReLU()
        self.hidden2 = nn.Linear(1024, 8)
        self.output = nn.Linear(8, 1)
        self.act_output = nn.Sigmoid()

    def forward(self, x):
        x = self.act(self.hidden1(x))
        x = self.act(self.hidden2(x))
        x = self.act_output(self.output(x))
        return x

