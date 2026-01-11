import pygame
import math
import random
import copy
import matplotlib.pyplot as plt
import pickle

HeadlessMode =True

pygame.init()
WIDTH, HEIGHT = 1000, 1000
if not HeadlessMode:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
SENSOR_ANGLES = [-0.4, 0, 0.4]
min_w = len(SENSOR_ANGLES)+2

version = 6

old_best_brain = None
old_best_fitness = -float("inf")

# ---------- ROAD ----------
road_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
road_surface.fill((0, 0, 0, 0))

road_mask = pygame.mask.from_surface(road_surface)

# AGENTS

class agent():
    def __init__(self):
        self.w_throttle = [random.uniform(-1,1) for _ in range(min_w)]
        self.b_throttle = random.uniform(-0.5,0.5)
        
        self.w_steering = [random.uniform(-1,1) for _ in range(min_w)]
        self.b_steering = random.uniform(-0.5,0.5)
        
    def get_params(self):
        return {
            "w_throttle": self.w_throttle,
            "b_throttle": self.b_throttle,
            
            "w_steering": self.w_steering,
            "b_steering":self.b_steering
        }
        
    def set_params(self, params):
        self.w_throttle = params["w_throttle"]
        self.b_throttle = params["b_throttle"]
        self.w_steering = params["w_steering"]
        self.b_steering = params["b_steering"]
        
    def act(self, sensors):
        steering = self.b_steering
        throttle = self.b_throttle
        for i in range(len(sensors)):
            steering += self.w_steering[i]*sensors[i]
            throttle += self.w_throttle[i]*sensors[i]
            
        steering = math.tanh(steering)
        throttle = math.tanh(throttle)
        return steering, throttle
        
    def mutate(self,strength=0.2,chance=0.15):
        for i in range(len(self.w_steering)):
            if chance > random.random():
                self.w_steering[i] += random.uniform(-strength,strength)
        for i in range(len(self.w_throttle)):
            if chance > random.random():
                self.w_throttle[i] += random.uniform(-strength,strength)
        if chance > random.random():
            self.b_steering += random.uniform(-strength,strength)
        if chance > random.random():
            self.b_throttle += random.uniform(-strength,strength)
        
        
# ---------- CAR ----------
class Car():
    def __init__(self,pos,angle):
        self.car_radius = 10
        self.car_pos = pos if pos else [0,0]
        
        self.speed = 4
        self.maxspeed = 8
        self.minspeed = 1
        self.a = 0.2
        
        self.angle = angle if angle else 0
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
            
        sensors.append(((self.angle + math.pi) % (2*math.pi) - math.pi)/math.pi)
        sensors.append(self.speed/self.maxspeed)
        steering, throttle = self.brain.act(sensors)
        max_turn = 0.08
        
        self.angle += max_turn*steering* (self.speed / self.maxspeed)
        self.speed += self.a*throttle
        self.speed = max(self.minspeed, min(self.speed, self.maxspeed))
        
        self.car_pos[0] += math.cos(self.angle) * self.speed
        self.car_pos[1] += math.sin(self.angle) * self.speed
        
        x,y = self.car_pos[0], self.car_pos[1]
        
        if not (0 <= x < WIDTH) or not (0 <= y < HEIGHT):
            self.crashed = True
            self.fitness -= 5
        if not road_mask.get_at((int(x),int(y))):
            self.crashed = True
            self.fitness -= 5
            
        dx = x - self.last_pos[0]
        dy = y -self.last_pos[1]
        if not self.crashed:
            forward = math.cos(self.angle) * dx + math.sin(self.angle) * dy
            self.fitness += max(0, forward) * (self.speed - self.minspeed)
            self.fitness -= 0.0625
        self.last_pos = self.car_pos[:]
        
    def get_car_mask(self):
        surf = pygame.Surface((self.car_radius*2, self.car_radius*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 0, 0), (self.car_radius, self.car_radius), self.car_radius)
        return pygame.mask.from_surface(surf), surf
        
    def raycast(self, mask, start, angle, max_dist=200, step=8):
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
        c.draw()
        #for a in SENSOR_ANGLES:
        #      dist = c.raycast(road_mask, c.car_pos, c.angle + a)
        #      end_x = c.car_pos[0] + math.cos(c.angle + a) * dist
        #      end_y = c.car_pos[1] + math.sin(c.angle + a) * dist
        #      pygame.draw.line(screen, (0, 150, 255), c.car_pos, (end_x, end_y), 2)
    pygame.display.flip()
    
def compare():
    global HeadlessMode, screen
    HeadlessMode = False
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    replay_cars = []
    
    if old_best_brain:
        old_car = Car(points[0],starting_angle)
        old_car.brain = copy.deepcopy(old_best_brain)
        replay_cars.append((old_car, (255,0,0)))
        
    new_car = Car(points[0],starting_angle)
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
        
points = []
waves = {}

for i in range(3):
    waves[i] = {
        "freq": random.uniform(1,5),
        "phase": random.uniform(0,math.pi*2),
        "amp": random.uniform(1,30)
    }

def point_creator():
	left.clear()
	right.clear()
	
	n = len(points)
	for i in range(n):
		prev = points[i-1]
		curr = points[i]
		next = points[(i+1)%n]
		
		dx = next[0] - prev[0]
		dy = next[1] - prev[1]
		length = math.hypot(dx,dy)
		
		if length <= 0:
			continue
			
		dx /= len
		dy /= len
		
		nx = -dy
		ny = dx
		
		offset = 50
		
		left.append([
			curr[0]+nx*offset,
			curr[1]+ny*offset
		])
		right.append([
			curr[0]-nx*offset,
			curr[1]-ny*offset
		])

def road_draw(n):
    global road_mask
    road_surface.fill((0, 0, 0, 0))
    left, right = point_creator(n)
    pygame.draw.lines(
    road_surface,
    (255,255,255),
    True,
    points,
    100
    )
    road_mask = pygame.mask.from_surface(road_surface)
    
def road_create():
    global points
    points.clear()
    center = [WIDTH/2, HEIGHT/2]
    b_radius = 250
    n = 64
    for i in range(n):
        noise = 0
        angle = i / n * math.tau
        for w in waves.values():
            noise += math.sin(angle*w["freq"]+w["phase"])*w["amp"]
        radius = b_radius + noise
        x = center[0] + math.cos(angle) * radius
        y = center[1] + math.sin(angle) * radius
        points.append([x,y])
    road_draw(n)
    
best_brain = None
best_fitness = -1

# ---------- MAIN LOOP ----------
max_generations = 1
pop = 50
max_steps = 1500
avg_fitness_history = []
best_gen_history = []
best_history =[]
road_create()

px = points[1][0] - points[0][0]
py = points[1][1] - points[0][1]
starting_angle = math.atan2(py,px)

cars=[Car(points[0],starting_angle) for _ in range(pop)]

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
except FileNotFoundError:
    print("No previous best brain found — starting fresh")


for generation in range(max_generations):
    steps = 0
    while not all(c.crashed for c in cars) and steps < max_steps:
        for c in cars:
            c.update_car()
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
        c = Car(points[0],starting_angle)
        c.brain = copy.deepcopy(elite.brain)
        next_gen.append(c)
        
    while len(next_gen) < pop:
        parent = random.choice(elites)
        child = Car(points[0],starting_angle)
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