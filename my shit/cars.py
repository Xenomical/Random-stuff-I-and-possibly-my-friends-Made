import pygame
import math
import random
import copy
import matplotlib.pyplot as plt
import pickle

HeadlessMode = True

pygame.init()
WIDTH, HEIGHT = 1000, 1000
if not HeadlessMode:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
SENSOR_ANGLES = [-0.8, -0.4, -0.2, 0, 0.2, 0.4, 0.8]
min_w = len(SENSOR_ANGLES)+2

version = 12
hidden = 6

old_best_brain = None
old_best_fitness = -float("inf")

# ---------- ROAD ----------
road_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
road_surface.fill((0, 0, 0, 0))
pygame.draw.ellipse(road_surface, (255,255,255), ((0,0),(1000,random.randint(400,1000))),100)

road_mask = pygame.mask.from_surface(road_surface)

# AGENTS

class agent():
    def __init__(self):
        self.w1 = [
        	[random.uniform(-1,1) for _ in range(min_w)]
        	for _ in range(hidden)
        ]
        self.b1 = [random.uniform(-0.5,0.5) for _ in range(hidden)]
        
        self.w2 = [
        	[random.uniform(-1,1) for _ in range(hidden)]
        	for _ in range(3)
        ]
        self.b2 = [random.uniform(-0.5,0.5) for _ in range(3)]
        
    def get_params(self):
        return {
            "w1": self.w1,
            "b1": self.b1,
            
            "w2": self.w2,
            "b2":self.b2
        }
        
    def set_params(self, params):
        self.w1 = params["w1"]
        self.b1 = params["b1"]
        self.w2 = params["w2"]
        self.b2 = params["b2"]
        
    def act(self, sensors):
        h_outputs = []
        for i in range(hidden):
        	s = self.b1[i]
        	for j in range(len(sensors)):
        		s += self.w1[i][j] *sensors[j]
        	h_outputs.append(math.tanh(s))
        	
        outputs = []
        for i in range(3):
        	s = self.b2[i]
        	for j in range(hidden):
        		s += self.w2[i][j] * h_outputs[j]
        	if i==0:
        		outputs.append(math.tanh(s))
        	else:
        		outputs.append((math.tanh(s)+1)*0.5)
        	
        steering, acc, brake = outputs
        return steering, acc, brake
        
    def mutate(self,strength=0.1,chance=0.1):
        for i in range(hidden):
            for j in range(min_w):
            	if chance > random.random():
            		self.w1[i][j] += random.uniform(-strength, strength)
            		self.w1[i][j] = max(-3, min(3, self.w1[i][j]))
            if chance > random.random():
            	self.b1[i] += random.uniform(-strength, strength)
            	self.b1[i] = max(-3, min(3, self.b1[i]))
        for i in range(3):
        	for j in range(hidden):
        		if chance > random.random():
        			self.w2[i][j] += random.uniform(-strength, strength)
        			self.w2[i][j] = max(-3, min(3, self.w2[i][j]))
        	if chance > random.random():
        		self.b2[i] += random.uniform(-strength, strength)
        		self.b2[i] = max(-3, min(3, self.b2[i]))
        
# ---------- CAR ----------
class Car():
    def __init__(self):
        self.car_radius = 10
        self.car_pos = [500,50]
        
        self.speed = 5
        self.maxspeed = 10
        self.minspeed = 1
        self.a = 0.4
        self.brake = 0.5
        
        self.angle = 0
        self.crashed = False
        self.fitness = 0
        self.brain = agent()
        self.last_pos = self.car_pos[:]
        
    def update_car(self):
        if self.crashed:
            return
            
        sensors = []
        for a in SENSOR_ANGLES:
        
            d = self.raycast(road_mask, self.car_pos,self.angle+a)
            sensors.append(min(1.0,d/200))
            
        l_sum = sum(sensors[:len(sensors)//2])
        r_sum = sum(sensors[len(sensors)//2+1:])
        
        sensors.append((l_sum-r_sum) / len(sensors))
        sensors.append(self.speed/self.maxspeed)
        steering, acc, brake = self.brain.act(sensors)
        max_turn = 0.08
        
        self.angle += max_turn*steering* (self.speed / self.maxspeed)
        self.speed += self.a*acc
        self.speed -= self.brake*brake
        self.speed = max(self.minspeed, min(self.speed, self.maxspeed))
        
        self.car_pos[0] += math.cos(self.angle) * self.speed
        self.car_pos[1] += math.sin(self.angle) * self.speed
        
        x,y = self.car_pos[0], self.car_pos[1]
        
        if not (0 <= x < WIDTH) or not (0 <= y < HEIGHT):
            self.crashed = True
            self.fitness -= 5
            return
            
        if not road_mask.get_at((int(x),int(y))):
            self.crashed = True
            self.fitness -= 5
            return
            
        dx = x - self.last_pos[0]
        dy = y -self.last_pos[1]
        if not self.crashed:
            forward = math.cos(self.angle) * dx + math.sin(self.angle) * dy
            self.fitness += max(0, forward) * (self.speed - self.minspeed)
            self.fitness -= 0.025
        self.last_pos = self.car_pos[:]
        
    def get_car_mask(self):
        surf = pygame.Surface((self.car_radius*2, self.car_radius*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 0, 0), (self.car_radius, self.car_radius), self.car_radius)
        return pygame.mask.from_surface(surf), surf
        
    def raycast(self, mask, start, angle, max_dist=200, step=2):
        dx = math.cos(angle)
        dy = math.sin(angle)

        for d in range(0, max_dist, step):
            x = int(start[0] + dx * d)
            y = int(start[1] + dy * d)

            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                if not mask.get_at((x, y)):
                    return d
        return max_dist
    
    def draw(self,color):
        x,y = self.car_pos[0], self.car_pos[1]
        pygame.draw.circle(screen, color, (x,y), self.car_radius)
        
        dir_x = math.cos(self.angle)
        dir_y = math.sin(self.angle)
        scaled_speed = self.speed / self.maxspeed*40
        end_x = x+dir_x*scaled_speed
        end_y = y+dir_y*scaled_speed
        
        pygame.draw.line(screen, color,(x,y),(end_x,end_y),2)
        
# ---- OTHER FUNCTIONS ----

def draw_all():
    if HeadlessMode:
        return
    screen.fill((30, 30, 30))
    screen.blit(road_surface, (0, 0))
    for c in cars:
        c.draw((0,255,0))
        for a in SENSOR_ANGLES:
            dist = c.raycast(road_mask, c.car_pos, c.angle + a)
            end_x = c.car_pos[0] + math.cos(c.angle + a) * dist
            end_y = c.car_pos[1] + math.sin(c.angle + a) * dist
            pygame.draw.line(screen, (0, 150, 255), c.car_pos, (end_x, end_y), 2)
    pygame.display.flip()
    
def compare():
    global HeadlessMode, screen
    HeadlessMode = False
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    replay_cars = []
    
    if old_best_brain:
        old_car = Car()
        old_car.brain = copy.deepcopy(old_best_brain)
        replay_cars.append((old_car, (255,0,0)))
        
    new_car = Car()
    new_car.brain = copy.deepcopy(best_brain)
    replay_cars.append((new_car, (0,255,0)))
    
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
        screen.fill((30,30,30))
        screen.blit(road_surface, (0,0))
        for car, color in replay_cars:
            car.update_car()
            car.draw(color)
        
        pygame.display.flip()
        clock.tick(60)
    
best_brain = None
best_fitness = -1

# ---------- MAIN LOOP ----------
max_generations = 25
pop = 50
max_steps = 600
avg_fitness_history = []
best_gen_history = []
best_history =[]

cars=[Car() for _ in range(pop)]

try:
    with open("old_best.pkl", "rb") as f:
        old_best_params, old_best_fitness, old_version = pickle.load(f)
        if version != old_version:
            print(f"The previous best brain is too old — starting fresh")
            old_best_brain = None
            old_best_fitness = -float("inf")
        else:
            print(f"Loaded previous best brain (fitness={old_best_fitness:.2f})")
            old_best_brain = agent()
            old_best_brain.set_params(old_best_params)
except (FileNotFoundError,EOFError,pickle.UnpicklingError):
    print("No previous best brain found — starting fresh")


for generation in range(max_generations):
    steps = 0
    while not all(c.crashed for c in cars) and steps < max_steps:
        for c in cars:
            c.update_car()
        draw_all()
        steps += 1
            
    avg = sum(c.fitness for c in cars) / len(cars)
    avg_fitness_history.append((generation,avg))
            
    gen_best = max(cars, key=lambda c: c.fitness)
    best_gen_history.append((generation,gen_best.fitness))
    
    if gen_best.fitness > best_fitness:
        best_brain = copy.deepcopy(gen_best.brain)
        best_fitness = gen_best.fitness
        best_history.append((generation, best_fitness))
        
    cars.sort(key=lambda c: c.fitness, reverse=True)
    elites = cars [:5]
    
    next_gen = []
    
    for elite in elites:
        c = Car()
        c.brain = copy.deepcopy(elite.brain)
        next_gen.append(c)
        
    while len(next_gen) < pop:
        parent = random.choice(elites)
        child = Car()
        child.brain = copy.deepcopy(parent.brain)
        child.brain.mutate()
        next_gen.append(child)
        
    print(f"Generation {generation} completed!\nTime taken: {steps}\nBest Generational Fitness: {gen_best.fitness}\nBest Fitness:{best_fitness}\nAverage Fitness: {avg}")
        
    cars = next_gen

# ====== AFTER TRAINING ======
import matplotlib.pyplot as plt

gens = [g for g,_ in avg_fitness_history]
avg = [f for _,f in avg_fitness_history]
best_gen = [f for _,f in best_gen_history]

plt.figure(figsize=(8,5))
plt.plot(gens, avg, label="Average fitness")
plt.plot(gens, best_gen, label="Best of generation")
plt.xlabel("Generation")
plt.ylabel("Fitness")
plt.legend()
plt.grid(True)
plt.show()

    
if best_fitness > old_best_fitness:
    with open("old_best.pkl", "wb") as f:
        pickle.dump((best_brain.get_params(), best_fitness, version), f)
    print("Saved new all-time best brain")
else:
    print("Current run did not beat previous best")
    
compare()

pygame.quit()
