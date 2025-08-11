# gym-zelda-pygame

A **Gymnasium** environment that wraps the Clear Code Pygame “Zelda” game into a **ROM-free**, modern RL playground. It exposes a pixel-observation interface, discrete actions, sensible rewards, and familiar wrappers (skip-frames, gray-scale resize to 84×84, frame-stack, normalize, channel-first) so you can train DQN/PPO/IMPALA-style agents without touching emulators or legacy Gym.

## Motivation

I recently finished a playthrough of **_The Legend of Zelda: Breath of the Wild_** and wanted to experiment with applying **reinforcement learning** to a Zelda-style world. Most existing environments either:
- rely on **ROMs/emulators**, or
- are tangled up with **deprecated `gym` + NumPy compatibility issues**.

## Installation
gym-zelda-pygame is published on **PyPI**. Install with:

```bash
pip install gym-zelda-pygame
```

## Environment Details

### Spaces

- **Action Space**: `Discrete(8)`
    0) no-op
    1) move up
    2) move down
    3) move left
    4) move right
    5) attack
    6) magic
    7) menu
  
- **Observation Space**: `Box(low=0, high=255, shape=(720, 1280, 3), dtype=uint8)` by default  
(Typically wrap this 84×84 grayscale and stack frames for learning)

### Rendering

- `render_mode="human"`: Pygame window (60 FPS throttle)
- `render_mode="rgb_array"`: returns the current frame as a numpy array
- Headless safety: when not using `"human"`, SDL dummy drivers are used automatically.

### Episode Termination

- Episode ends when:
- Player health ≤ 0, or
- All enemies defeated

### Reward

Default (configurable) reward shaping in `ZeldaEnv`:
- Small step penalty: `-0.001` per step (encourage efficiency)
- Health changes: penalty for loss, small reward for gain
- Experience gain: small positive reward
- Enemy defeats: large positive reward (`+10.0` per enemy)
- Death penalty: `-100.0`

You can pass a **custom reward function** via `custom_reward_fn`:
```python
def my_reward_fn(current_state, previous_state, episode_steps):
  # current_state: dict with keys shown below
  # previous_state: same keys for previous step
  # return float
  ...
env = ZeldaEnv(render_mode="rgb_array", custom_reward_fn=my_reward_fn)
```

### Info Dict

Each step() returns an info dict with: 
```python
{
  'episode_steps': int,
  'player_health': int,
  'player_exp': int,
  'enemy_count': int,
  'player_pos': (x: int, y: int),
}
```

## Credit

- **Game code** adapted from Clear Code’s Zelda tutorial: [clear-code-projects/Zelda](https://github.com/clear-code-projects/Zelda)
- **Graphics and audio assets** courtesy of Pixel-boy/AAA under CC0: [Ninja Adventure asset pack](https://pixel-boy.itch.io/ninja-adventure-asset-pack)

Respect the original projects’ licenses and assets. This environment is an RL wrapper around their codebase to support education.
