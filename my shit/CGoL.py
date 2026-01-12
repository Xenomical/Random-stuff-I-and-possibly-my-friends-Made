import pygame
import random
import math

pygame.init()
WIDTH, HEIGHT = 1000, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

grid_size = 20
square_size = 1000/grid_size
b_grid = [[random.randint(0,1)for _ in range(grid_size)] for _ in range(grid_size)]

def draw_cells():
	for i in range(grid_size):
		for j in range(grid_size):
			if b_grid[i][j] == 1:
				pygame.draw.rect(screen, (255,255,255), ((square_size*i,square_size*j),(square_size,square_size)))

def grid_checker(grid,r,c):
        count = 0
        rows = len(grid)
        cols = len(grid[0])
        
        for ar in (-1,0,1):
                for ac in (-1,0,1):
                        if ar==0 and ac==0:
                                continue
                        nr = r + ar
                        nc = c + ac
                        if 0 <= nr < rows and 0 <= nc < cols:
                                if grid[nr][nc]:
                                        count += 1
        return count
        

def rule_follower():
        global b_grid
        n_grid = [row[:] for row in b_grid]
        for i in range(grid_size):
                for j in range(grid_size):
                        n = grid_checker(b_grid,i,j)
                        print(f"Position's {i},{j} neighbors {n}")
                        if b_grid[i][j]:
                                if n < 2:
                                        n_grid[i][j] = 0
                                if n > 3:
                                        n_grid[i][j] = 0
                        if not b_grid[i][j]:
                                if n == 3:
                                        n_grid[i][j] = 1
        b_grid = [row[:] for row in n_grid]
			
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
	running = detect_quit()
	rule_follower()
	render()
	clock.tick(10)

pygame.quit()
