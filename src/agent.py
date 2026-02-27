import gymnasium as gym
import numpy as np
import pygame
import random
from gymnasium.utils.env_checker import check_env

OPPONENT = 0
AGENT = 1

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
        self.force = force

        self._agent_pos = np.array([0, 0], dtype=np.float64)
        self._agent_vel = 0
        self._opp_pos = np.array([0, 0], dtype=np.float64)
        self._opp_vel = 0
        self._ball_pos = np.array([0, 0], dtype=np.float64)
        self._ball_vel = np.array([0, 0], dtype=np.float64)
        self._reward = 0

        self.observation_space = gym.spaces.Dict(
            {
                "agent": gym.spaces.Box(0, self.height - self.pad_height, shape=(1,), dtype=np.float64),
                "opponent": gym.spaces.Box(0, self.height - self.pad_height, shape=(1,), dtype=np.float64),
                "ball_pos": gym.spaces.Box(np.array([self.ball_rad - self.width * 0.1, self.pad_height + self.ball_rad - self.height]), np.array([self.width - self.ball_rad, self.height - self.ball_rad]), shape=(2,), dtype=np.float64),
                "ball_vel": gym.spaces.Box(-self.init_speed, self.init_speed, shape=(2,), dtype=np.float64),
            }
        )

        self.action_space = gym.spaces.MultiBinary(2) #, seed=42)

    def _get_obs(self):
        return {"agent": self._agent_pos[1], "opponent": self._opp_pos[1], "ball_pos": self._ball_pos - self._agent_pos, "ball_vel": self._ball_vel}

    def _get_info(self):
        return {"distance": np.linalg.norm(self._agent_pos - self._ball_pos, ord=2)}

    def reset(self, options=None, seed=None):
        # IMPORTANT: Must call this first to seed the random number generator
        super().reset(seed=seed)

        self._agent_pos = self.np_random.uniform(np.array([self.width * 0.9, 0]), np.array([self.width * 0.9, self.height * 0.75]), size=2)
        self._opp_pos = self.np_random.uniform(np.array([self.width * 0.1, 0]), np.array([self.width * 0.1, self.height * 0.75]), size=2)
        # self._ball_pos = self.np_random.uniform(, np.array([self.width, self.height]), size=2)
        self._ball_pos = self.np_random.uniform(np.array([self.width * 0.1 + self.pad_width + self.ball_rad, self.ball_rad]), np.array([self.width * 0.9 - self.ball_rad, self.height - self.ball_rad]), size=2)
        self._ball_vel = self.np_random.uniform(-600.0, 600.0, size=2)

        observation = self._get_obs()
        print(observation)
        info = self._get_info()

        return observation, info

    def step(self, action):
        """Execute one timestep within the environment.

        Args:
            action: The action to take (0-1 for directions)

        Returns:
            tuple: (observation, reward, terminated, truncated, info)
        """

        result = self.update(dt=0.016, action=action)

        terminated = result != -1
        truncated = 1000
        observation = self._get_obs()
        info = self._get_info()

        return observation, self.reward, terminated, truncated, info

    def draw(self):
        self.screen.fill("white")
        pygame.draw.rect(self.screen, "black", self.players[0].rect)
        pygame.draw.rect(self.screen, "black", self.players[1].rect)
        pygame.draw.circle(self.screen, "black", self.ball.pos, self.ball.radius)
        pygame.display.flip()

    def check_collisions(self):
        cx = max(self._agent_pos[0], min(self._ball_pos[0], self._agent_pos[0] + self.pad_width))
        cy = max(self._agent_pos[1], min(self._ball_pos[1], self._agent_pos[1] + self.pad_height))
        
        dx = self._ball_pos[0] - cx
        dy = self._ball_pos[1] - cy
        
        if (dx**2 + dy**2) < self.ball_rad**2:
            if abs(dx) > abs(dy):
                v = np.linalg.norm(self._ball_vel, ord=2)
                self._ball_vel[0] *= -1
                self._ball_vel[1] += self._opp_vel * self.friction
                self._ball_vel = self._ball_vel * (min(self.max_speed, v + abs(self._agent_vel) * self.restitution / self.max_speed)) / np.linalg.norm(self._ball_vel, ord=2)
                self._ball_pos[0] = cx + (self.ball_rad if dx > 0 else -self.ball_rad)
                self._reward += 1
            else:
                self._ball_vel[1] *= -1
                self._ball_pos[1] = cy + (self.ball_rad if dy > 0 else -self.ball_rad)
                self._reward -= 1
            return AGENT

        cx = max(self._opp_pos[0], min(self._ball_pos[0], self._opp_pos[0] + self.pad_width))
        cy = max(self._opp_pos[1], min(self._ball_pos[1], self._opp_pos[1] + self.pad_height))
        
        dx = self._ball_pos[0] - cx
        dy = self._ball_pos[1] - cy
        
        if (dx**2 + dy**2) < self.ball_rad**2:
            if abs(dx) > abs(dy):
                v = np.linalg.norm(self._ball_vel, ord=2)
                self._ball_vel[0] *= -1
                self._ball_vel[1] += self._opp_vel * self.friction
                self._ball_vel = self._ball_vel * (min(self.max_speed, v + abs(self._opp_vel) * self.restitution / self.max_speed)) / np.linalg.norm(self._ball_vel, ord=2)
                self._ball_pos[0] = cx + (self.ball_rad if dx > 0 else -self.ball_rad)
            else:
                self._ball_vel[1] *= -1
                self._ball_pos[1] = cy + (self.ball_rad if dy > 0 else -self.ball_rad)
            return OPPONENT
        return -1

    def _move(self, dt, dir, player):
        if player == OPPONENT: # opponent
            self._opp_vel += dir * dt * self.force
            self._opp_vel = max(-self.max_speed, min(self._opp_vel, self.max_speed))

            self._opp_pos[1] += self._opp_vel * dt
            if self._opp_pos[1] < 0:
                self._opp_pos[1] = 0
                self._opp_vel = 0
            if self._opp_pos[1] > self.height * self.pad_height:
                self._opp_pos[1] = self.height * self.pad_height
                self._opp_vel = 0
        else: # agent
            self._agent_vel += dir * dt * self.force
            self._agent_vel = max(-self.max_speed, min(self._agent_vel, self.max_speed))

            self._agent_pos[1] += self._opp_vel * dt
            if self._agent_pos[1] < 0:
                self._agent_pos[1] = 0
                self._agent_vel = 0
            if self._agent_pos[1] > self.height * self.pad_height:
                self._agent_pos[1] = self.height * self.pad_height
                self._agent_vel = 0

    def update(self, dt, action):
        # bats
        if self._ball_pos[1] < self._opp_pos[1]:
            self._move(dt, -1, OPPONENT)
        if self._ball_pos[1] > self._opp_pos[1] + self.height * 0.25:
            self._move(dt, 1, OPPONENT)

        if action == 0:
            self._move(dt, -1, AGENT)
        else:
            self._move(dt, 1, AGENT)

        # ball
        self._ball_pos += self._ball_vel * dt
        if self._ball_pos[1] - self.ball_rad < 0:
            self._ball_pos[1] = 2 * self.ball_rad - self._ball_pos[1]
            self._ball_vel[1] *= -1
        if self._ball_pos[1] + self.ball_rad > self.height:
            self._ball_pos[1] = 2 * self.height - self._ball_pos[1] - 2 * self.ball_rad
            self._ball_vel[1] *= -1

        # score
        if self._ball_pos[0] - self.ball_rad < 0:
            self._reward += 5
            return AGENT
        if self._ball_pos[0] + self.ball_rad > self.width:
            self._reward -= 5
            return OPPONENT
        
        self.check_collisions()
        return -1

if __name__ == "__main__":
    gym.register(
        id="Pong-v0",
        entry_point="agent:GameEnv",
        max_episode_steps=1000,
    )
    gym.pprint_registry()

    env = gym.make("Pong-v0")
    try:
        check_env(env.unwrapped)
        print("Environment passes all checks!")
    except Exception as e:
        print(f"Environment has issues: {e}")