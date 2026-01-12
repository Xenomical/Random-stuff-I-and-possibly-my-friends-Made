import pygame
import random
import math

pygame.init()
screen = pygame.display.set_mode((1200,1000))
clock = pygame.time.Clock()

def get_triangle_points(x, y, angle, size=10):
    # Tip of the triangle (forward)
    tip_x = x + math.cos(math.radians(angle)) * size
    tip_y = y + math.sin(math.radians(angle)) * size

    # Base of the triangle (behind the tip)
    back_distance = size * 0.01 # how far back the base is
    side_offset = size *2  # how wide the triangle is

    # Base points
    left_x = x + math.cos(math.radians(angle + 150)) * side_offset - math.cos(math.radians(angle)) * back_distance
    left_y = y + math.sin(math.radians(angle + 150)) * side_offset - math.sin(math.radians(angle)) * back_distance

    right_x = x + math.cos(math.radians(angle - 150)) * side_offset - math.cos(math.radians(angle)) * back_distance
    right_y = y + math.sin(math.radians(angle - 150)) * side_offset - math.sin(math.radians(angle)) * back_distance

    return [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)]


boids = []


for _ in range(50):
	boids.append({
	"x": random.randint(0,1000),
	"y": random.randint(0,800),
	"angle": random.randint(0,360)
	})
	
def angle_diff(target, current, max_turn):
    # compute shortest rotation (-180..180)
    diff = (target - current + 180) % 360 - 180
    # clamp by max_turn
    diff = max(-max_turn, min(max_turn, diff))
    return diff

	
def separation(b,ns):
	sdx = 0
	sdy = 0
	c = 0
	
	for n in ns:
		dx = n["x"] - b["x"]
		dy = n["y"] - b["y"]
		
		if dx*dx + dy*dy <= 2500:
			sdx += b["x"] - n["x"]
			sdy += b["y"] - n["y"]
			c += 1
		
	if c > 0:
		sdx /= c
		sdy /= c
		sa = math.degrees(math.atan2(sdy, sdx))
			
		max_turn = 5
		ad = (sa - b["angle"] + 180) % 360 - 180
		ad = max(-max_turn, min(ad, max_turn))
		return ad
	elif c == 0:
			return 0
			
def alignment(b,ns):
	 sum = 0
	 for n in ns:
	 	sum += n["angle"]
	 target_angle = sum / len(ns)
	 return angle_diff(target_angle, b["angle"], 5)
	 
def cohesion(b,ns):
	avg_x = sum(n["x"] for n in ns) / len(ns)
	avg_y = sum(n["y"] for n in ns) / len(ns)
	target_angle = math.degrees(math.atan2(avg_y - b["y"], avg_x - b["x"]))
	return angle_diff(target_angle, b["angle"], 5)

	 
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
	
	screen.fill((0, 0, 0))
	for b in boids:
	       color = (0, 0, 255)
	       speed = 5
	       neighbors = []
	       
	       for n in boids:
	       	if n == b:
	       		continue
	       	dx = n["x"] - b["x"]
	       	dy = n["y"] - b["y"]
	       	
	       	if dx**2+dy**2 <= 150*150:
	       		neighbors.append(n)
	       
	       if len(neighbors) > 0:
	       	b["angle"] += (separation(b,neighbors) *1.5 + alignment(b, neighbors) *0.5 + cohesion(b,neighbors) * 0.2)
	       	
	       b["x"] += math.cos(math.radians(b["angle"])) * speed
	       b["y"] += math.sin(math.radians(b["angle"])) * speed
	       
	       if b["x"]  > 1200:
	       	b["x"] = 0
	       elif b["x"] < 0:
	       	b["x"] = 1200
	       
	       if b["y"] > 1000:
	       	b["y"] = 0
	       elif b["y"] < 0:
	       	b["y"] = 1000

	       points = get_triangle_points(b["x"], b["y"], b["angle"],10)
	       pygame.draw.polygon(screen, color, points)
		
	pygame.display.flip()
	clock.tick(60)
	
pygame.quit()
