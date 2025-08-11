import pygame
from settings import *
from entity import Entity
from support import import_folder, _resolve_asset_path

class Player(Entity):
	def __init__(self,pos,groups,obstacle_sprites,create_attack,destroy_attack,create_magic):
		super().__init__(groups)
		self.image = pygame.image.load(_resolve_asset_path('../graphics/test/player.png')).convert_alpha()
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0,-26)
		self.obstacle_sprites = obstacle_sprites

		# graphics setup
		self.import_player_assets()
		self.status = 'down'

		# movement
		self.speed = 5
		self.attacking = False
		self.attack_cooldown = 400
		self.attack_time = None

		# weapons
		self.weapon_index = 0
		self.weapon = list(weapon_data.keys())[self.weapon_index]
		self.create_attack = create_attack
		self.destroy_attack = destroy_attack
		try:
			self.weapon_attack_sound = pygame.mixer.Sound(_resolve_asset_path('../audio/sword.wav'))
			self.weapon_attack_sound.set_volume(0.4)
		except pygame.error:
			self.weapon_attack_sound = None

		# magic
		self.create_magic = create_magic
		self.magic_index = 0
		self.magic = list(magic_data.keys())[self.magic_index]

		# switch cooldowns (for UI overlay expectations)
		self.can_switch_weapon = True
		self.weapon_switch_time = None
		self.can_switch_magic = True
		self.magic_switch_time = None
		self.switch_duration_cooldown = 200

		# stats
		self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'magic': 4, 'speed': 5}
		self.max_stats = {'health': 300, 'energy': 140, 'attack': 20, 'magic': 10, 'speed': 10}
		self.upgrade_cost = {'health': 100, 'energy': 100, 'attack': 100, 'magic': 100, 'speed': 100}
		self.health = self.stats['health']
		self.energy = self.stats['energy']
		self.exp = 0
		self.speed = self.stats['speed']

		# damage timer
		self.vulnerable = True
		self.hurt_time = None
		self.invulnerability_duration = 500

	def import_player_assets(self):
		self.animations = {'up':[], 'down':[], 'left':[], 'right':[],
			'right_idle':[],'down_idle':[],'left_idle':[],'up_idle':[],
			'right_attack':[],'down_attack':[],'left_attack':[],'up_attack':[]}

		main_path = '../graphics/player/'
		for animation in self.animations.keys():
			self.animations[animation] = import_folder(main_path + animation)

	def input(self):
		keys = pygame.key.get_pressed()
		
		if not self.attacking:
			# movement input
			if keys[pygame.K_UP]:
				self.direction.y = -1
				self.status = 'up'
			elif keys[pygame.K_DOWN]:
				self.direction.y = 1
				self.status = 'down'
			else:
				self.direction.y = 0

			if keys[pygame.K_RIGHT]:
				self.direction.x = 1
				self.status = 'right'
			elif keys[pygame.K_LEFT]:
				self.direction.x = -1
				self.status = 'left'
			else:
				self.direction.x = 0

			# attack input
			if keys[pygame.K_z]:
				self.attacking = True
				self.attack_time = pygame.time.get_ticks()
				self.create_attack()
				if self.weapon_attack_sound:
					self.weapon_attack_sound.play()

			if keys[pygame.K_x]:
				self.attacking = True
				self.attack_time = pygame.time.get_ticks()
				style = list(magic_data.keys())[self.magic_index]
				strength = list(magic_data.values())[self.magic_index]['strength'] + self.stats['magic']
				cost = list(magic_data.values())[self.magic_index]['cost']
				self.create_magic(style,strength,cost)

			# switch weapon with lightweight cooldown to satisfy UI overlay
			if keys[pygame.K_a] and not self.attacking and self.can_switch_weapon:
				self.can_switch_weapon = False
				self.weapon_switch_time = pygame.time.get_ticks()
				self.weapon_index = (self.weapon_index + 1) % len(weapon_data.keys())
				self.weapon = list(weapon_data.keys())[self.weapon_index]

			# switch magic with lightweight cooldown to satisfy UI overlay
			if keys[pygame.K_s] and not self.attacking and self.can_switch_magic:
				self.can_switch_magic = False
				self.magic_switch_time = pygame.time.get_ticks()
				self.magic_index = (self.magic_index + 1) % len(magic_data.keys())

	def get_status(self):
		# idle status
		if self.direction.x == 0 and self.direction.y == 0:
			if not 'idle' in self.status and not 'attack' in self.status:
				self.status = self.status + '_idle'

		if self.attacking:
			self.direction.x = 0
			self.direction.y = 0
			if not 'attack' in self.status:
				if 'idle' in self.status:
					self.status = self.status.replace('_idle','_attack')
				else:
					self.status = self.status + '_attack'

	def cooldowns(self):
		current_time = pygame.time.get_ticks()
		if self.attacking:
			if current_time - self.attack_time >= self.attack_cooldown:
				self.attacking = False
				self.destroy_attack()

		# simple switch cooldown windows so UI overlay can blink
		if not self.can_switch_weapon and self.weapon_switch_time is not None:
			if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
				self.can_switch_weapon = True
				self.weapon_switch_time = None

		if not self.can_switch_magic and self.magic_switch_time is not None:
			if current_time - self.magic_switch_time >= self.switch_duration_cooldown:
				self.can_switch_magic = True
				self.magic_switch_time = None

	def animate(self):
		animation = self.animations[self.status]
		
		# loop over the frame index 
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0

		# set the image
		self.image = animation[int(self.frame_index)]
		self.rect = self.image.get_rect(center = self.hitbox.center)

		# flicker 
		if not self.vulnerable:
			alpha = self.wave_value()
			self.image.set_alpha(alpha)
		else:
			self.image.set_alpha(255)

	def get_full_weapon_damage(self):
		base_damage = self.stats['attack']
		weapon_damage = weapon_data[self.weapon]['damage']
		return base_damage + weapon_damage

	def get_full_magic_damage(self):
		base_damage = self.stats['magic']
		spell_damage = magic_data[self.magic]['strength']
		return base_damage + spell_damage

	def get_value_by_index(self,index):
		return list(self.stats.values())[index]

	def get_cost_by_index(self,index):
		return list(self.upgrade_cost.values())[index]

	def energy_recovery(self):
		if self.energy < self.stats['energy']:
			self.energy += 0.01 * self.stats['magic']
		else:
			self.energy = self.stats['energy']

	def update(self):
		self.input()
		self.cooldowns()
		self.get_status()
		self.animate()
		self.move(self.stats['speed'])
		self.energy_recovery()