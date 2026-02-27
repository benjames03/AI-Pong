from torch import nn

class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()
        self.activation = nn.ReLU()

        self.linear1 = nn.Linear(8, 10)
        self.linear2 = nn.Linear(10, 10)
        self.linear3 = nn.Linear(10, 2)

        self.softmax = nn.Softmax(dim=1)

    def forward(self, input):
        out = self.linear1(input)
        out = self.activation(out)
        out = self.linear2(out)
        out = self.activation(out)
        out = self.linear3(out)
        out = self.softmax(out)
        
        return out