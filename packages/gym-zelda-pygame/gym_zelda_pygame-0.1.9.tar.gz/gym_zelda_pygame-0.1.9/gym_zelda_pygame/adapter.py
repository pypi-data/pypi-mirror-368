import os
import pygame
from typing import Dict, Any, Optional
import sys
from pathlib import Path
import random
import numpy as np

# Add the game code directory to the path
game_dir = Path(__file__).parent / "game" / "code"
sys.path.insert(0, str(game_dir))

# Change working directory to game folder for asset loading
original_cwd = os.getcwd()
os.chdir(str(Path(__file__).parent / "game" / "code"))

try:
    from level import Level
    from settings import *
except ImportError as e:
    print(f"Failed to import game modules: {e}")
    # Restore original working directory
    os.chdir(original_cwd)
    raise

# Restore original working directory
os.chdir(original_cwd)

class GameAdapter:
    """Adapter to wrap the Clear Code Pygame Zelda game for RL training."""
    
    def __init__(self, seed: Optional[int] = None):
        if not pygame.get_init():
            pygame.init()
        
        # Store original directory
        self.original_cwd = os.getcwd()
        self.game_dir = str(Path(__file__).parent / "game" / "code")
        
        # Initialize game components
        self.screen = None
        self.clock = pygame.time.Clock()
        self.level = None
        self.running = True
        
        # Game state tracking
        self.player_health = 100
        self.player_exp = 0
        self.enemy_count = 0
        
        # Seeding
        self.seed = seed
        
        # Initialize the level
        self.reset(seed=seed)
    
    def _change_to_game_dir(self):
        """Change to game directory for asset loading."""
        os.chdir(self.game_dir)
    
    def _restore_original_dir(self):
        """Restore original working directory."""
        os.chdir(self.original_cwd)
    
    def reset(self, seed: Optional[int] = None):
        """Reset the game to initial state."""
        if seed is not None:
            self.seed = seed
            random.seed(seed)
            np.random.seed(seed)
        
        self._change_to_game_dir()
        try:
            # Create new level instance
            self.level = Level()
            
            # Reset game state tracking
            if hasattr(self.level, 'player'):
                self.player_health = getattr(self.level.player, 'health', 100)
                self.player_exp = getattr(self.level.player, 'exp', 0)
            
            # Count initial enemies
            if hasattr(self.level, 'visible_sprites'):
                from enemy import Enemy
                self.enemy_count = len([sprite for sprite in self.level.visible_sprites 
                                      if isinstance(sprite, Enemy)])
            
        finally:
            self._restore_original_dir()
    
    def update(self, keys: Dict[str, bool]):
        """Update game state based on input keys."""
        if not self.level:
            return
        
        self._change_to_game_dir()
        try:
            # Handle input keys by simulating pygame events and key states
            events = []
            
            # Create key press events for actions
            if keys.get('attack', False):
                # Simulate space key press for attack
                events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
            
            if keys.get('magic', False):
                # Simulate left ctrl for magic
                events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LCTRL))
                
            if keys.get('menu', False):
                # Simulate 'm' key for menu
                events.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m))
            
            # Handle player actions directly since we can't easily override pygame input
            if hasattr(self.level, 'player'):
                player = self.level.player
                
                # Handle movement - set direction and status
                if not player.attacking:
                    direction_x, direction_y = 0, 0
                    
                    if keys.get('up', False):
                        direction_y = -1
                        player.status = 'up'
                    elif keys.get('down', False):
                        direction_y = 1
                        player.status = 'down'
                    else:
                        direction_y = 0
                    
                    if keys.get('right', False):
                        direction_x = 1
                        player.status = 'right'
                    elif keys.get('left', False):
                        direction_x = -1
                        player.status = 'left'
                    else:
                        direction_x = 0
                    
                    player.direction.x = direction_x
                    player.direction.y = direction_y
                
                # Handle attack
                if keys.get('attack', False) and not player.attacking:
                    player.attacking = True
                    player.attack_time = pygame.time.get_ticks()
                    if hasattr(player, 'create_attack'):
                        player.create_attack()
                    if hasattr(player, 'weapon_attack_sound') and player.weapon_attack_sound:
                        player.weapon_attack_sound.play()
                
                # Handle magic
                if keys.get('magic', False) and not player.attacking:
                    player.attacking = True
                    player.attack_time = pygame.time.get_ticks()
                    if hasattr(player, 'create_magic'):
                        style = list(magic_data.keys())[player.magic_index] if hasattr(player, 'magic_index') else 'flame'
                        strength = magic_data[style]['strength'] + player.stats['magic'] if hasattr(player, 'stats') else 5
                        cost = magic_data[style]['cost']
                        player.create_magic(style, strength, cost)
            
            # Process events
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m and hasattr(self.level, 'toggle_menu'):
                        self.level.toggle_menu()
            
            # Update the level
            if hasattr(self.level, 'run'):
                self.level.run()
            
            # Update game state tracking
            if hasattr(self.level, 'player'):
                self.player_health = getattr(self.level.player, 'health', self.player_health)
                self.player_exp = getattr(self.level.player, 'exp', self.player_exp)
            
            # Count current enemies
            if hasattr(self.level, 'visible_sprites'):
                from enemy import Enemy
                self.enemy_count = len([sprite for sprite in self.level.visible_sprites 
                                      if isinstance(sprite, Enemy)])
                
        finally:
            self._restore_original_dir()
    
    def draw(self, surface: pygame.Surface):
        """Draw the game to the provided surface."""
        if not self.level:
            return
            
        self._change_to_game_dir()
        try:
            # Fill with background color
            surface.fill(WATER_COLOR if 'WATER_COLOR' in globals() else (113, 221, 238))
            
            # Set the display surface for the level to draw on
            if hasattr(self.level, 'display_surface'):
                original_surface = self.level.display_surface
                self.level.display_surface = surface
            
            # Draw all visible sprites
            if hasattr(self.level, 'visible_sprites'):
                if hasattr(self.level.visible_sprites, 'custom_draw'):
                    self.level.visible_sprites.custom_draw(self.level.player if hasattr(self.level, 'player') else None)
                else:
                    # Fallback to regular draw if custom_draw not available
                    self.level.visible_sprites.draw(surface)
            
            # Draw UI
            if hasattr(self.level, 'ui') and hasattr(self.level, 'player'):
                if hasattr(self.level.ui, 'display'):
                    self.level.ui.display(self.level.player)
            
            # Draw upgrade menu if active
            if hasattr(self.level, 'game_paused') and self.level.game_paused:
                if hasattr(self.level, 'upgrade') and hasattr(self.level.upgrade, 'display'):
                    self.level.upgrade.display()
            
            # Restore original surface reference
            if hasattr(self.level, 'display_surface'):
                self.level.display_surface = original_surface
                
        except Exception as e:
            print(f"Error during draw: {e}")
            # Fill with error color
            surface.fill((255, 0, 0))
        finally:
            self._restore_original_dir()
    
    def get_game_state(self) -> Dict[str, Any]:
        """Get current game state for reward calculation."""
        if not self.level or not hasattr(self.level, 'player'):
            return {
                'player_health': 0,
                'player_exp': 0,
                'enemy_count': 0,
                'player_pos': (0, 0)
            }
        
        player = self.level.player
        return {
            'player_health': getattr(player, 'health', 0),
            'player_exp': getattr(player, 'exp', 0),
            'enemy_count': self.enemy_count,
            'player_pos': (getattr(player, 'rect', pygame.Rect(0,0,0,0)).centerx, 
                          getattr(player, 'rect', pygame.Rect(0,0,0,0)).centery)
        }
