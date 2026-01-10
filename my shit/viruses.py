import matplotlib.pyplot as plt
import pygame
import random
import math

pygame.init()
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 16)

class Rabbit:
    
    def __init__(self, speed=None, sight = None, hunger = None, life=None, adult=None):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.targetX = random.randint(0,WIDTH)
        self.targetY = random.randint(0, HEIGHT)
        self.pause = 0
        
        hunger_threshold = hunger if hunger else random.randint(10, 80)
        
        repro = hunger_threshold + random.randint(5,20)
		
        self.traits = {
        	"speed": speed if speed else random.uniform(0.2,2),
        	"sight": sight if sight else random.uniform(15,150),
        	"threshold": hunger_threshold,
        	"repro": repro,
        	"adult": adult if adult else random.uniform(360, 720)
        }
        
        self.base_traits = {
        	"speed": self.traits["speed"],
        	"sight": self.traits['sight'],
        	"repro": self.traits["repro"]
        }
        
        self.stats = {
        	"food": 100,
        	"water": 100,
        	"state": 0,
        	#state 0 - neutral
        	#state 1 - thirsty
        	#state 2 - hungry
        	#state 3 - searching for mate
        	"age": 0
        }
        
    def update_rabbit(self):
    	self.age_stuff()
    	state = self.update_state()
    	if state == 2:
    		self.detect(food)
    	elif state == 3:
    		potential_mates = []
    		for c in population:
    			if c.stats["state"] == 3 and c is not self:
    				potential_mates.append(c)
    		if potential_mates:
    			self.detect(potential_mates)
    	self.move_towards()
    	if state == 2:
    		self.eat_food()
    	self.stats["food"] -= 0.05*self.traits["speed"]
    	
    	if (self.stats["food"] or self.stats["water"]) <= 0:
    		population.remove(self)
    
    def age_stuff(self):
    	self.stats["age"] += 1
    	if self.stats["age"] <= self.traits["adult"]:
    		factor = self.stats["age"]/self.traits["adult"]
    		self.traits["speed"] = self.base_traits["speed"] * factor
    		self.traits["sight"] = self.base_traits["sight"] * factor
    		self.traits["repro"] = self.base_traits["repro"] / factor**2
    	
    
    def update_state(self):
    	if self.stats["food"] < self.traits["threshold"]:
    		self.stats["state"] = 2
    	elif self.stats["food"] > self.traits["repro"]:
    		self.stats["state"] = 3
    	else:
    		self.stats["state"] = 0
    		
    	return self.stats["state"]
    	
    def detect(self, list):
    	n_dist = float('inf')
    	nearest = None
    	for f in list:
    		dx = f[0] - self.x
    		dy = f[1] - self.y
    		dist = math.hypot(dx,dy)
    		if dist <= self.traits["sight"] and dist < n_dist:
    			n_dist = dist
    			nearest = f
    	if nearest:
    		self.targetX = nearest[0]
    		self.targetY = nearest[1]
    		
    def eat_food(self):
    	for f in food[:]:
    		dx = f[0] - self.x
    		dy = f[1] - self.y
    		dist = math.hypot(dx,dy)
    		if dist < 5:
    			food.remove(f)
    			self.pause = random.randint(30, 60)
    			self.targetX = random.randint(0, WIDTH)
    			self.targetY = random.randint(0, HEIGHT)
    			self.stats["food"] = min(100, self.stats["food"]+50)
    			return
    	
    def move_towards(self):
        if self.pause > 0:
        	self.pause -= 1
        	return
        
        dx = self.targetX - self.x
        dy = self.targetY - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.x += dx / dist * self.traits["speed"]
            self.y += dy / dist * self.traits["speed"]
            
        if dist < 5:
        	self.pause += random.randint(30,60)
        	self.targetX = random.randint(0, WIDTH)
        	self.targetY = random.randint(0, HEIGHT)

    def draw(self):
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), 8)
        
    def draw_stats(self):
    	food = int(self.stats["food"])
    	energy = int(self.stats["water"])
    	state = self.stats["state"]
    	age = self.stats["age"]

    	text = f"F:{food} E:{energy} S:{state} A: {age}"

    # Color based on state
    	if state == 2:      # hungry
        	color = (255, 0, 0)
    	elif state == 1:    # exhausted
        	color = (255, 165, 0)
    	elif state == 3:    # mating
        	color = (255, 0, 255)
    	else:               # neutral
        	color = (200, 200, 200)

    # Render the text
    	surf = font.render(text, True, color)

    # Draw above the rabbit
    	screen.blit(surf, (int(self.x) - 20, int(self.y) - 25))

population = [Rabbit() for _ in range(1)]
food = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(20)]

def generate_food():
	if random.uniform(0,1) < 0.1 and len(food) < 20:
		food.append((random.randint(0, WIDTH), random.randint(0, HEIGHT)))
		
def update_all():
	generate_food()
	for c in population[:]:
		c.update_rabbit()

def detect_quit():
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			return False
	return True

def render():
	screen.fill((30,30,30))
	for c in population:
		c.draw()
		c.draw_stats()
	for f in food:
		pygame.draw.circle(screen, (0, 255, 0), f, 4)
	pygame.display.flip()

running = True
while running:
    running = detect_quit()
    update_all()
    render()
    clock.tick(60)
    

pygame.quit()
