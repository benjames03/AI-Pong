import gymnasium as gym
import numpy as np
import pygame
from gymnasium.utils.env_checker import check_env

"""
Reward system:
    Hitting ball = +1 (-1 for top/bottom)
    Scoring      = +5 (-5 for conceding)
"""

class GameEnv(gym.Env):
    def __init__(self, init_speed=600, max_speed=3000, friction=1, restitution=15, force=10000):
        self.width = 1280
        self.height = 720
        self.pad_width = self.width * 0.04
        self.pad_height = self.height * 0.25
        self.ball_rad = self.width * 0.02
        self.init_speed = init_speed
        self.max_speed = max_speed
        self.friction = friction
        self.restitution = restitution

        self.agent = np.array([self.width * 0.9, 0], dtype=np.float64)
        self.agent_vy = 0
        self.opp = np.array([self.width * 0.1 - self.pad_width, 0], dtype=np.float64)
        self.opp_vy = 0
        self.ball_pos = np.array([0, 0], dtype=np.float64)
        self.ball_vel = np.array([0, 0], dtype=np.float64)
        self.reward = 0

        self.observation_space = gym.spaces.Dict(
            {
                "agent": gym.spaces.Box(0, self.height - self.pad_height, shape=(1,), dtype=np.float64),
                "opponent": gym.spaces.Box(0, self.height - self.pad_height, shape=(1,), dtype=np.float64),
                "ball_pos": gym.spaces.Box(np.array([self.ball_rad - self.agent[0], self.pad_height + self.ball_rad - self.height]), np.array([self.width - self.agent[0] - self.ball_rad, self.height - self.ball_rad]), dtype=np.float64),
                "ball_vel": gym.spaces.Box(-self.max_speed, self.max_speed, shape=(2,), dtype=np.float64),
            }
        )
        self.action_space = gym.spaces.Discrete(2) #, seed=42)

    def _get_obs(self):
        return {"agent": np.array([self.agent[1]]), "opponent": np.array([self.opp[1]]), "ball_pos": self.ball_pos - self.agent, "ball_vel": self.ball_vel}

    def _get_info(self):
        return {"distance": np.linalg.norm(self.ball_pos - self.agent, ord=2)}

    def reset(self, options=None, seed=None):
        super().reset(seed=seed)

        self.agent[1] = self.np_random.uniform(0, self.height - self.pad_height)
        self.opp[1] = self.np_random.uniform(0, self.height - self.pad_height)
        self.ball_pos = self.np_random.uniform(np.array([self.opp[0] + self.pad_width + self.ball_rad, self.ball_rad]), np.array([self.agent[0] - self.ball_rad, self.height - self.ball_rad]), size=2)
        self.ball_vel = self.np_random.uniform(-self.init_speed, self.init_speed, size=2)

        return self._get_obs(), self._get_info()

    def step(self, action):
        result = self.update(dt=0.016, action=action)
        terminated = result != -1
        truncated = False
        observation = self._get_obs()
        info = self._get_info()
        return observation, self.reward, terminated, truncated, info

    def render(self):
        pygame.init()
        pygame.display.set_caption("Pong")
        screen = pygame.display.set_mode((self.width, self.height))
        screen.fill("white")
        pygame.draw.rect(screen, "black", pygame.Rect(self.opp[0], self.opp[1], self.pad_width, self.pad_height))
        pygame.draw.rect(screen, "black", pygame.Rect(self.agent[0], self.agent[1], self.pad_width, self.pad_height))
        pygame.draw.circle(screen, "black", self.ball_pos, self.ball_rad)
        pygame.display.flip()
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    running = False

    def check_collisions(self):
        cx = max(self.agent[0], min(self.ball_pos[0], self.agent[0] + self.pad_width))
        cy = max(self.agent[1], min(self.ball_pos[1], self.agent[1] + self.pad_height))
        
        dx = self.ball_pos[0] - cx
        dy = self.ball_pos[1] - cy
        
        if (dx**2 + dy**2) < self.ball_rad**2:
            if abs(dx) > abs(dy):
                v = np.linalg.norm(self.ball_vel, ord=2)
                self.ball_vel[0] *= -1
                self.ball_vel[1] += self.opp_vy * self.friction
                self.ball_vel = self.ball_vel * (min(self.max_speed, v + abs(self.agent_vy) * self.restitution / self.max_speed)) / np.linalg.norm(self.ball_vel, ord=2)
                self.ball_pos[0] = cx + (self.ball_rad if dx > 0 else -self.ball_rad)
                self.reward += 1
            else:
                self.ball_vel[1] *= -1
                self.ball_pos[1] = cy + (self.ball_rad if dy > 0 else -self.ball_rad)
                self.reward -= 1
            return 1 # agent

        cx = max(self.opp[0], min(self.ball_pos[0], self.opp[0] + self.pad_width))
        cy = max(self.opp[1], min(self.ball_pos[1], self.opp[1] + self.pad_height))
        
        dx = self.ball_pos[0] - cx
        dy = self.ball_pos[1] - cy
        
        if (dx**2 + dy**2) < self.ball_rad**2:
            if abs(dx) > abs(dy):
                v = np.linalg.norm(self.ball_vel, ord=2)
                self.ball_vel[0] *= -1
                self.ball_vel[1] += self.opp_vy * self.friction
                self.ball_vel = self.ball_vel * (min(self.max_speed, v + abs(self.opp_vy) * self.restitution / self.max_speed)) / np.linalg.norm(self.ball_vel, ord=2)
                self.ball_pos[0] = cx + (self.ball_rad if dx > 0 else -self.ball_rad)
            else:
                self.ball_vel[1] *= -1
                self.ball_pos[1] = cy + (self.ball_rad if dy > 0 else -self.ball_rad)
            return 0 # opponent
        return -1

    def _move(self, dt, dir, player):
        if player == 0: # opponent
            self.opp_vy = dir * self.init_speed
            self.opp[1] += self.opp_vy * dt
            if self.opp[1] < 0:
                self.opp[1] = 0
                self.opp_vy = 0
            if self.opp[1] > self.height * self.pad_height:
                self.opp[1] = self.height * self.pad_height
                self.opp_vy = 0
        else: # agent
            self.agent_vy = dir * self.init_speed
            self.agent[1] += self.agent_vy * dt
            if self.agent[1] < 0:
                self.agent[1] = 0
                self.agent_vy = 0
            if self.agent[1] > self.height * self.pad_height:
                self.agent[1] = self.height * self.pad_height
                self.agent_vy = 0

    def update(self, dt, action):
        # opponent
        if self.ball_pos[1] < self.opp[1]:
            self._move(dt, -1, 0)
        if self.ball_pos[1] > self.opp[1] + self.pad_height:
            self._move(dt, 1, 0)

        # agent
        if action == 0:
            self._move(dt, -1, 1)
        else:
            self._move(dt, 1, 1)

        # ball
        self.ball_pos += self.ball_vel * dt
        if self.ball_pos[1] - self.ball_rad < 0:
            self.ball_pos[1] = 2 * self.ball_rad - self.ball_pos[1]
            self.ball_vel[1] *= -1
        if self.ball_pos[1] + self.ball_rad > self.height:
            self.ball_pos[1] = 2 * self.height - self.ball_pos[1] - 2 * self.ball_rad
            self.ball_vel[1] *= -1

        # score
        if self.ball_pos[0] - self.ball_rad < 0:
            self.reward += 5
            return 1 # agent
        if self.ball_pos[0] + self.ball_rad > self.width:
            self.reward -= 5
            return 0 # opponent
        
        self.check_collisions()
        return -1
    
def test_env():
    gym.register(
        id="Pong-v0",
        entry_point="agent:GameEnv",
        max_episode_steps=1000,
    )
    env = gym.make("Pong-v0")
    try:
        check_env(env.unwrapped)
        print("Environment passes all checks!")
        obs, info = env.reset(seed=201)
        print(f"Starting positions\nAgent: {obs['agent']}\nOpponent: {obs['opponent']}\nBall position: {obs['ball_pos']}\nBall velocity: {obs['ball_vel']}")
        actions = [0, 1, 1]
        for action in actions:
            old_pos = obs["agent"].copy()
            obs, reward, terminated, truncated, info = env.step(action)
            new_pos = obs["agent"]
            print(f"Action {action}: {old_pos} -> {new_pos}, reward={reward}")
        env.render()
        env.close()
    except Exception as e:
        print(f"Environment has issues: {e}")

if __name__ == "__main__":
    test_env()