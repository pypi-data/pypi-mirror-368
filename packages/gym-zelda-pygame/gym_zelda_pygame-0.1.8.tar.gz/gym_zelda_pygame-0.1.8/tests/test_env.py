#!/usr/bin/env python3
import os

# Ensure headless operation for CI/servers
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import gymnasium as gym
import gym_zelda_pygame
import numpy as np


def test_basic_functionality_rgb_array():
    env = gym.make("ZeldaCC-v0", render_mode="rgb_array")
    try:
        obs, info = env.reset(seed=123)
        assert isinstance(info, dict)
        assert obs.dtype == np.uint8 and obs.ndim == 3
        assert obs.shape[-1] == 3  # RGB

        action = env.action_space.sample()
        obs2, reward, terminated, truncated, info = env.step(action)
        assert obs2.shape == obs.shape
        assert isinstance(reward, float)
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert "episode_steps" in info
        # info may include game stats if available
    finally:
        env.close()


def test_pixels84_wrapper_registered():
    env = gym.make("ZeldaCC-Pixels84-v0", render_mode="rgb_array")
    try:
        obs, _ = env.reset(seed=0)
        # FrameStack returns LazyFrames; convert to ndarray to check shape
        arr = np.array(obs)
        # Should be (stack, 84, 84)
        assert arr.ndim == 3
        assert arr.shape[0] == 4 and arr.shape[1:] == (84, 84)
        assert arr.dtype == np.uint8
        # Step works
        obs2, r, term, trunc, info = env.step(env.action_space.sample())
        assert np.array(obs2).shape == arr.shape
        assert isinstance(r, float)
        assert isinstance(term, bool)
        assert isinstance(trunc, bool)
    finally:
        env.close()