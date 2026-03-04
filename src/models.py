import torch
import torch.nn as nn

class PolicyModel(nn.Module):
    def __init__(self, in_dim=8, hidden_dims=(25, 25), out_dim=1):
        super(PolicyModel, self).__init__()
        self.activation = nn.Tanh()

        self.shared_net = nn.Sequential(
            nn.Linear(in_dim, hidden_dims[0]),
            self.activation,
            nn.Linear(hidden_dims[0], hidden_dims[1]),
            self.activation,
        )

        self.mean_net = nn.Sequential(
            nn.Linear(hidden_dims[1], out_dim)
        )

        self.std_net = nn.Sequential(
            nn.Linear(hidden_dims[1], out_dim)
        )

        # self.softmax = nn.Softmax(dim=1)

    def forward(self, input):
        shared = self.shared_net(input)

        means = self.mean_net(shared)
        stds = torch.log(1 + torch.exp(self.std_net(shared)))
        
        return means, stds