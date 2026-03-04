import torch
import torch.nn as nn

class PolicyModel(nn.Module):
    def __init__(self, in_dim=6, hidden_dims=(25, 25), out_dim=2):
        super(PolicyModel, self).__init__()
        self.activation = nn.Tanh()

        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden_dims[0]),
            self.activation,
            nn.Linear(hidden_dims[0], hidden_dims[1]),
            self.activation,
            nn.Linear(hidden_dims[1], out_dim),
            nn.Softmax(dim=-1)
        )

    def forward(self, input):
        output = self.net(input)
        return output