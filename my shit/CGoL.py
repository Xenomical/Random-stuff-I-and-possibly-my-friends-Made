import pygame
import random
import math

pygame.init()
WIDTH, HEIGHT = 1000, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

grid_size = 10
grid = [[1 for _ in range(grid_size)] for _ in range(grid_size)]

def draw_cells():
	for i in range(grid_size):
		for j in range(grid_size):
			if grid[i][j] == 1:
				pygame.draw.rect(screen, (255,255,255), ((100*i,100*(1+i)),(100*j,100*(j+1))))
			
def detect_quit():
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			return False
	return True

def render():
	screen.fill((30,30,30))
	draw_cells()
	pygame.display.flip()
				
			
running = True
while running:
	detect_quit()
	render()
	clock.tick