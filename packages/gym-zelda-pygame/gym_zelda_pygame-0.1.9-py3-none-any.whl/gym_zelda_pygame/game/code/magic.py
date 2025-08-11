import pygame
from settings import *
from entity import Entity
from support import _resolve_asset_path

class MagicPlayer:
	def __init__(self,animation_player):
		self.animation_player = animation_player
		# preload sounds safely
		try:
			self.sounds = {
				'heal': pygame.mixer.Sound(_resolve_asset_path('../audio/heal.wav')),
				'flame': pygame.mixer.Sound(_resolve_asset_path('../audio/Fire.wav'))
			}
			for s in self.sounds.values():
				s.set_volume(0.6)
		except pygame.error:
			self.sounds = {'heal': None, 'flame': None}

	def heal(self,player,strength,cost,groups):
		if player.energy >= cost:
			player.energy -= cost
			player.health += strength
			if player.health >= player.stats['health']:
				player.health = player.stats['health']

			self.animation_player.create_particles('aura',player.rect.center,groups)
			self.animation_player.create_particles('heal',player.rect.center + pygame.math.Vector2(0,-60),groups)
			if self.sounds['heal']:
				self.sounds['heal'].play()

	def flame(self,player,cost,groups):
		if player.energy >= cost:
			player.energy -= cost

			self.animation_player.create_particles('flame',player.rect.center + pygame.math.Vector2(0,-16),groups)
			if self.sounds['flame']:
				self.sounds['flame'].play()