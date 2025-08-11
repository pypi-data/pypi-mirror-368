import numpy as np
from typing import Tuple, Any, Deque
import gymnasium as gym
from gymnasium import spaces
from PIL import Image
from collections import deque


class SkipFrame(gym.Wrapper):
    """Repeat the same action for `num_skip` frames and sum rewards."""

    def __init__(self, env: gym.Env, num_skip: int = 4):
        super().__init__(env)
        assert num_skip >= 1
        self.num_skip = num_skip

    def step(self, action: Any) -> Tuple[np.ndarray, float, bool, bool, dict]:
        total_reward = 0.0
        last_observation = None
        terminated = False
        truncated = False
        info = {}

        for _ in range(self.num_skip):
            observation, reward, terminated, truncated, info = self.env.step(action)
            total_reward += float(reward)
            last_observation = observation
            if terminated or truncated:
                break
        return last_observation, total_reward, terminated, truncated, info


class GrayscaleResize84(gym.ObservationWrapper):
    """Convert RGB observations to grayscale and resize to 84x84, returning uint8."""

    def __init__(self, env: gym.Env):
        super().__init__(env)
        self._target_size = (84, 84)
        self.observation_space = spaces.Box(
            low=0,
            high=255,
            shape=self._target_size,
            dtype=np.uint8,
        )

    def observation(self, observation: np.ndarray) -> np.ndarray:
        # Observation is expected to be H x W x C uint8
        if observation.ndim == 3 and observation.shape[-1] in (3, 4):
            img = Image.fromarray(observation)
        elif observation.ndim == 2:
            img = Image.fromarray(observation)
        else:
            # Fallback: attempt to reshape if transposed
            if observation.ndim == 3 and observation.shape[0] in (3, 4):
                observation = np.transpose(observation, (1, 2, 0))
                img = Image.fromarray(observation)
            else:
                raise ValueError(f"Unsupported observation shape for GrayscaleResize84: {observation.shape}")

        img = img.convert("L").resize(self._target_size[::-1], resample=Image.BILINEAR)
        out = np.array(img, dtype=np.uint8)
        return out


class FrameStack(gym.Wrapper):
    """Stack the last N observations along the last axis.
    Works for 2D (H, W) or 3D (H, W, C) observations.
    """

    def __init__(self, env: gym.Env, num_stack: int = 4):
        super().__init__(env)
        assert num_stack >= 1
        self.num_stack = num_stack
        self.frames: Deque[np.ndarray] = deque(maxlen=num_stack)

        old_space = self.observation_space
        if not isinstance(old_space, spaces.Box):
            raise ValueError("FrameStack expects Box observation space")
        if len(old_space.shape) == 2:
            h, w = old_space.shape
            new_shape = (h, w, num_stack)
        elif len(old_space.shape) == 3:
            h, w, c = old_space.shape
            new_shape = (h, w, c * num_stack)
        else:
            raise ValueError("FrameStack expects 2D or 3D observation shapes")
        # Conservatively set bounds to 0..255
        self.observation_space = spaces.Box(low=0, high=255, shape=new_shape, dtype=old_space.dtype)

    def reset(self, **kwargs):
        obs, info = self.env.reset(**kwargs)
        self.frames.clear()
        for _ in range(self.num_stack):
            self.frames.append(obs)
        return self._get_observation(), info

    def step(self, action: Any):
        obs, reward, terminated, truncated, info = self.env.step(action)
        self.frames.append(obs)
        return self._get_observation(), reward, terminated, truncated, info

    def _get_observation(self) -> np.ndarray:
        frames_list = list(self.frames)
        if frames_list[0].ndim == 2:
            return np.stack(frames_list, axis=-1)
        else:
            # (H, W, C) -> concat along channel dim
            return np.concatenate(frames_list, axis=-1)


class Normalize01(gym.ObservationWrapper):
    """Normalize observations to [0, 1] float32."""

    def __init__(self, env: gym.Env):
        super().__init__(env)
        low = np.zeros(self.observation_space.shape, dtype=np.float32)
        high = np.ones(self.observation_space.shape, dtype=np.float32)
        self.observation_space = spaces.Box(low=low, high=high, dtype=np.float32)

    def observation(self, observation: np.ndarray) -> np.ndarray:
        if observation.dtype != np.float32:
            observation = observation.astype(np.float32)
        observation /= 255.0
        return observation


class ChannelFirst(gym.ObservationWrapper):
    """Move channel axis from last to first: (H, W, C) -> (C, H, W).
    If input is grayscale (H, W), it becomes (1, H, W).
    """

    def __init__(self, env: gym.Env):
        super().__init__(env)
        old_space = self.observation_space
        if not isinstance(old_space, spaces.Box) or len(old_space.shape) not in (2, 3):
            raise ValueError("ChannelFirst expects 2D or 3D observations")
        if len(old_space.shape) == 2:
            h, w = old_space.shape
            c = 1
        else:
            h, w, c = old_space.shape
        self.observation_space = spaces.Box(
            low=0,
            high=255,
            shape=(c, h, w),
            dtype=old_space.dtype,
        )

    def observation(self, observation: np.ndarray) -> np.ndarray:
        if observation.ndim == 2:
            observation = observation[None, ...]  # (1, H, W)
        elif observation.ndim == 3:
            observation = np.moveaxis(observation, -1, 0)
        else:
            raise ValueError(f"Expected 2D or 3D observation, got {observation.shape}")
        return observation 