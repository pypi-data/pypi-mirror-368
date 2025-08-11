import numpy as np
import pygame
import gymnasium as gym
from gymnasium import spaces
from typing import Optional, Dict, Any
import os

from gym_zelda_pygame.adapter import GameAdapter

class ZeldaEnv(gym.Env):
    """
    A Gymnasium environment for the Clear Code Pygame Zelda tutorial.
    This provides a standalone, ROM-free Zelda-like RL environment.
    """
    
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}
    
    def __init__(self, render_mode: Optional[str] = None, custom_reward_fn: Optional[callable] = None):
        super().__init__()
        
        # Store render mode and custom reward function
        self.render_mode = render_mode
        self.custom_reward_fn = custom_reward_fn
        self._owns_pygame = False
        
        # Screen dimensions from Clear Code tutorial
        self.screen_width = 1280
        self.screen_height = 720
        
        # Headless safety: use dummy drivers when not rendering to human window
        if render_mode != "human":
            os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
            os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
            os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
        
        # Initialize Pygame if needed
        if not pygame.get_init():
            pygame.init()
            self._owns_pygame = True
        
        # Create screen surface
        if render_mode == "human":
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            pygame.display.set_caption("Zelda RL Environment")
        else:
            # Create off-screen surface for rgb_array mode, but also ensure display exists
            self.screen = pygame.Surface((self.screen_width, self.screen_height))
            # Ensure there's a pygame display surface (required by the game code)
            if pygame.display.get_surface() is None:
                pygame.display.set_mode((self.screen_width, self.screen_height), pygame.HIDDEN)
        
        # Initialize game adapter
        self.game_adapter = GameAdapter()
        
        # Define action space
        # Actions: 0=nothing, 1=up, 2=down, 3=left, 4=right, 5=attack, 6=magic, 7=menu
        self.action_space = spaces.Discrete(8)
        
        # Define observation space - RGB image of the game screen
        self.observation_space = spaces.Box(
            low=0, high=255,
            shape=(self.screen_height, self.screen_width, 3),
            dtype=np.uint8
        )
        
        # Episode tracking
        self.episode_steps = 0
        
        # Game state tracking for rewards
        self.previous_player_health = 100
        self.previous_player_exp = 0
        self.previous_enemy_count = 0
    
    def _get_observation(self) -> np.ndarray:
        """Convert the pygame screen to numpy array observation."""
        # Get the pixel array from pygame surface
        obs = pygame.surfarray.array3d(self.screen)
        # Pygame uses (width, height, channels), we need (height, width, channels)
        obs = np.transpose(obs, (1, 0, 2))
        return obs.astype(np.uint8)
    
    def _get_action_keys(self, action: int) -> Dict[str, bool]:
        """Convert discrete action to key press dictionary."""
        keys = {
            'up': False,
            'down': False, 
            'left': False,
            'right': False,
            'attack': False,
            'magic': False,
            'menu': False
        }
        
        if action == 1:  # up
            keys['up'] = True
        elif action == 2:  # down
            keys['down'] = True
        elif action == 3:  # left
            keys['left'] = True
        elif action == 4:  # right
            keys['right'] = True
        elif action == 5:  # attack
            keys['attack'] = True
        elif action == 6:  # magic
            keys['magic'] = True
        elif action == 7:  # menu
            keys['menu'] = True
        # action == 0 is no action (all keys False)
        
        return keys
    
    def _calculate_reward(self) -> float:
        """Calculate reward based on game state changes."""
        # Get current game state
        current_state = self.game_adapter.get_game_state()
        
        # Use custom reward function if provided
        if self.custom_reward_fn is not None:
            reward = self.custom_reward_fn(
                current_state=current_state,
                previous_state={
                    'player_health': self.previous_player_health,
                    'player_exp': self.previous_player_exp,
                    'enemy_count': self.previous_enemy_count
                },
                episode_steps=self.episode_steps
            )
        else:
            # Default reward calculation
            reward = self._default_reward_calculation(current_state)
        
        # Update tracking variables
        self.previous_player_health = current_state['player_health']
        self.previous_player_exp = current_state['player_exp']
        self.previous_enemy_count = current_state['enemy_count']
            
        return reward
    
    def _default_reward_calculation(self, current_state: Dict[str, Any]) -> float:
        """Default reward calculation logic."""
        reward = 0.0
        
        # Small negative reward for each step to encourage efficiency
        reward -= 0.001
        
        # Health changes
        health_change = current_state['player_health'] - self.previous_player_health
        if health_change < 0:
            # Lost health - penalty
            reward += health_change * 0.1  # Small penalty per health lost
        elif health_change > 0:
            # Gained health - small reward
            reward += health_change * 0.05
        
        # Experience changes
        exp_change = current_state['player_exp'] - self.previous_player_exp
        if exp_change > 0:
            # Gained experience - reward
            reward += exp_change * 0.001  # Small reward per exp point
        
        # Enemy count changes
        enemy_change = self.previous_enemy_count - current_state['enemy_count']
        if enemy_change > 0:
            # Defeated enemies - big reward
            reward += enemy_change * 10.0
        
        # Death penalty
        if current_state['player_health'] <= 0:
            reward -= 100.0
            
        return reward
    
    def _is_terminated(self) -> bool:
        """Check if episode should terminate due to environment terminal states."""
        current_state = self.game_adapter.get_game_state()
        # Terminal if player died or all enemies defeated
        if current_state['player_health'] <= 0:
            return True
        if current_state['enemy_count'] == 0:
            return True
        return False
    
    def reset(self, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None):
        """Reset the environment to initial state."""
        super().reset(seed=seed)
        
        # Reset episode tracking
        self.episode_steps = 0
        
        # Reset game state (propagate seed)
        self.game_adapter.reset(seed=seed)
        
        # Clear screen
        self.screen.fill((113, 221, 238))  # WATER_COLOR from settings
        
        # Get initial observation
        observation = self._get_observation()
        
        # Reset tracking variables from actual game state
        initial_state = self.game_adapter.get_game_state()
        self.previous_player_health = initial_state['player_health']
        self.previous_player_exp = initial_state['player_exp']
        self.previous_enemy_count = initial_state['enemy_count']
        
        return observation, {}
    
    def step(self, action: int):
        """Execute one step in the environment."""
        # Convert action to key presses
        keys = self._get_action_keys(action)
        
        # Update game state
        self.game_adapter.update(keys)
        
        # Draw game to screen
        self.game_adapter.draw(self.screen)
        
        # Get observation
        observation = self._get_observation()
        
        # Calculate reward
        reward = self._calculate_reward()
        
        # Termination flags
        terminated = self._is_terminated()
        truncated = False  # TimeLimit wrapper handles truncation via registration
        
        # Update episode step counter
        self.episode_steps += 1
        
        # Info dict with useful diagnostics
        state = self.game_adapter.get_game_state()
        info = {
            'episode_steps': self.episode_steps,
            'player_health': state['player_health'],
            'player_exp': state['player_exp'],
            'enemy_count': state['enemy_count'],
            'player_pos': state['player_pos'],
        }
        
        return observation, reward, terminated, truncated, info
    
    def render(self):
        """Render the environment."""
        if self.render_mode == "human":
            # Update the display and throttle FPS
            pygame.display.flip()
            if hasattr(self.game_adapter, 'clock'):
                self.game_adapter.clock.tick(self.metadata['render_fps'])
        elif self.render_mode == "rgb_array":
            # Return the screen as numpy array
            return self._get_observation()
    
    def close(self):
        """Clean up environment resources."""
        # Only close pygame if we initialized it here
        if self._owns_pygame and pygame.get_init():
            try:
                if pygame.mixer.get_init():
                    pygame.mixer.quit()
                pygame.display.quit()
            finally:
                pygame.quit()
            self._owns_pygame = False