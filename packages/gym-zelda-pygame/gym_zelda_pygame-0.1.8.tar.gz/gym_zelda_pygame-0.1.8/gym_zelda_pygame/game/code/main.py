import pygame, sys
from settings import *
from level import Level
from support import _resolve_asset_path

# Safely load main sound only if mixer is initialized
try:
	main_sound = pygame.mixer.Sound(_resolve_asset_path('../audio/main.ogg'))
	main_sound.set_volume(0.5)
except pygame.error:
	main_sound = None

class Game:
	def __init__(self):

		# general setup
		pygame.init()
		self.screen = pygame.display.set_mode((WIDTH,HEIGTH))
		pygame.display.set_caption('Zelda')
		self.clock = pygame.time.Clock()

		self.level = Level()

		# sound 
		if main_sound:
			main_sound.play(loops = -1)
	
	def run(self):
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_m:
						self.level.toggle_menu()

			self.screen.fill(WATER_COLOR)
			self.level.run()
			pygame.display.update()
			self.clock.tick(FPS)

if __name__ == '__main__':
	game = Game()
	game.run()