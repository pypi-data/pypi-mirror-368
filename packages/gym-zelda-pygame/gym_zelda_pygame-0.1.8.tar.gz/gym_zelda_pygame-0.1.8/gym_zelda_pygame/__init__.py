from gymnasium.envs.registration import register
from typing import Optional

# Keep registration for gym.make("ZeldaCC-v0")
register(
    id="ZeldaCC-v0",
    entry_point="gym_zelda_pygame.envs.zelda_env:ZeldaEnv",
    kwargs={"render_mode": None},
    max_episode_steps=3000,
)

# Register a convenience wrapped variant with 84x84 grayscale stacked frames
register(
    id="ZeldaCC-Pixels84-v0",
    entry_point="gym_zelda_pygame:make_zelda_pixels84",
    kwargs={"render_mode": None, "num_skip": 4, "num_stack": 4},
    max_episode_steps=3000,
)

from .envs import ZeldaEnv  # noqa: E402

def make_zelda_pixels84(
    render_mode: Optional[str] = None,
    num_skip: int = 4,
    num_stack: int = 4,
):
    """
    Convenience constructor that returns a pixel-based RL-ready environment:
    - Base env returns raw RGB frames (H,W,3)
    - Wrapped with SkipFrame -> GrayscaleResize84 -> FrameStack -> ChannelFirst
    - Final observation space is (num_stack, 84, 84) uint8
    """
    import gymnasium as gym
    # Use local wrappers to avoid cross-version issues
    from .wrappers import SkipFrame, GrayscaleResize84, ChannelFirst, FrameStack

    env = ZeldaEnv(render_mode=render_mode)
    env = SkipFrame(env, num_skip=num_skip)
    env = GrayscaleResize84(env)
    env = FrameStack(env, num_stack=num_stack)
    env = ChannelFirst(env)
    return env
