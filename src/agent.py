import gymnasium as gym
import torch
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import random
from models import PolicyModel

class REINFORCE:
    def __init__(self, obs_dims, action_dims):
        self.lr = 5e-4
        self.gamma = 0.99
        self.eps = 1e-6

        self.probs = []
        self.rewards = []

        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        self.net = PolicyModel(in_dim=obs_dims, hidden_dims=(30, 30), out_dim=action_dims).to(device)
        self.optimiser = torch.optim.Adam(self.net.parameters(), lr=self.lr, eps=self.eps)

    def sample_action(self, state):
        state = torch.tensor(state)
        probs = self.net(state)

        dist = torch.distributions.Categorical(probs)
        action = dist.sample()
        prob = dist.log_prob(action)

        action = action.numpy()

        self.probs.append(prob)

        return action

    def update(self):
        running_g = 0
        gs = []

        for R in self.rewards[::-1]:
            running_g = R + self.gamma * running_g
            gs.insert(0, running_g)

        deltas = torch.tensor(gs)
        log_probs = torch.stack(self.probs).squeeze()
        loss = -torch.sum(log_probs * deltas)

        self.optimiser.zero_grad()
        loss.backward()
        self.optimiser.step()

        self.probs = []
        self.rewards = []

    def save_net(self, filepath):
        torch.save(self.net.state_dict(), filepath)
        print(f"Saved PyTorch Model State to {filepath}")

def plot(data):
    plt.rcParams["figure.figsize"] = (10, 5)
    df1 = pd.DataFrame(data).melt()
    df1.rename(columns={"variable": "episodes", "value": "reward"}, inplace=True)
    sns.set_style("darkgrid")
    sns.set_context("talk")
    sns.set_palette("rainbow")
    sns.lineplot(x="episodes", y="reward", data=df1).set(title="REINFORCE for Pong")
    plt.show()

if __name__ == "__main__":
    n_episodes = 100
    max_steps = 500

    gym.register(id="Pong-v0", entry_point="game:GameEnv", max_episode_steps=max_steps)
    env = gym.make("Pong-v0")
    wrapped_env = gym.wrappers.RecordEpisodeStatistics(env, buffer_length=n_episodes)

    obs_dims = 6 # env.observation_space.shape[0]
    action_dims = 2 # env.action_space.shape[0]
    rewards_over_seeds = []

    for seed in [3]:
        torch.manual_seed(seed)
        random.seed(seed)
        np.random.seed(seed)

        agent = REINFORCE(obs_dims, action_dims)
        reward_over_episodes = []

        for episode in range(n_episodes):
            obs, info = wrapped_env.reset(seed=seed)

            done = False
            while not done:
                action = agent.sample_action(obs)

                obs, reward, terminated, truncated, info = wrapped_env.step(action)
                agent.rewards.append(reward)

                done = terminated or truncated

            reward_over_episodes.append(wrapped_env.return_queue[-1])
            agent.update()

            if episode % 25 == 0:
                avg_reward = int(np.mean(wrapped_env.return_queue))
                print("Episode:", episode, "Average Reward:", avg_reward)

        rewards_over_seeds.append(reward_over_episodes)
        agent.save_net("../models/test.pth")
    plot(rewards_over_seeds)