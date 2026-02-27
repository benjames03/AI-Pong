from collections import defaultdict
import gymnasium as gym
import numpy as np
from tqdm import tqdm

class PongAgent:
    def __init__(self, env, lr, init_epsilon, epsilon_decay, final_epsilon, discount=0.95):
        self.env = env
        self.q_values = defaultdict(lambda: np.zeros(env.action_space.n))
        self.lr = lr
        self.discount = discount
        self.epsilon = init_epsilon
        self.epsilon_decay = epsilon_decay
        self.final_epsilon = final_epsilon
        self.training_error = []

    def get_action(self, obs):
        if np.random.random() < self.epsilon:
            return self.env.action_space.sample()
        else:
            return int(np.argmax(self.q_values[obs]))

    def update(self, obs, action, reward, terminated, next_obs):
        future_q_value = (not terminated) * np.max(self.q_values[next_obs])
        target = reward + self.discount * future_q_value
        temporal_diff = target - self.q_values[obs][action]

        self.q_values[obs][action] = (self.q_values[obs][action] + self.lr * temporal_diff)
        self.training_error.append(temporal_diff)

    def decay_epsilon(self):
        self.epsilon = max(self.final_epsilon, self.epsilon - self.epsilon_decay)

if __name__ == "__main__":
    lr = 0.01
    n_episodes = 100
    start_epsilon = 1.0
    epsilon_decay = start_epsilon / (n_episodes / 2)
    final_epsilon = 0.1

    gym.register(id="Pong-v0", entry_point="game:GameEnv", max_episode_steps=100)
    env = gym.make("Pong-v0")
    env = gym.wrappers.RecordEpisodeStatistics(env, buffer_length=n_episodes)
    agent = PongAgent(env=env, lr=lr, init_epsilon=start_epsilon, epsilon_decay=epsilon_decay, final_epsilon=final_epsilon)

    print(agent.q_values)
    # for episode in tqdm(range(n_episodes)):
    #     obs, info = env.reset()
    #     done = False
    #     while not done:
    #         action = agent.get_action(obs)
    #         next_obs, reward, terminated, truncated, info = env.step(action)
    #         agent.update(obs, action, reward, terminated, next_obs)
    #         done = terminated or truncated
    #         obs = next_obs
    #     agent.decay_epsilon()

    env.close()