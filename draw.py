import pygame
from pygame.locals import *
from sys import exit
 
from random import *
from math import pi
 
pygame.init()
screen = pygame.display.set_mode((640, 480), 0, 32)
points = []

class Color:
    def __init__(self, R, G, B):
        self.R = R
        self.G = G
        self.B = B        

def draw_circle(color, x, y, radius):
    rc = (color.R, color.G, color.B)
    rp = (x, y)
    rr = radius
    pygame.draw.circle(screen, rc, rp, rr)

class Point_creature:
    def __init__(self, color, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
    def draw(self):
        draw_circle(self.color, self.x, self.y, self.size)


creatures = []
RED = Color(255, 0, 0)

def create_creatures(num_of_creatures, color, x, y, size):
    for i in range(num_of_creatures):
        creature = Point_creature(color, x, y, size)
        creatures.append(creature)
def create_creatures_random(num_of_creatures, color = None, x = None, y = None, size = None):
    random_color = True
    random_x = True
    random_y = True
    random_size = True

    if color is not None:
        random_color = False
    if x is not None:
        random_x = False
    if y is not None:
        random_y = False
    if size is not None:
        random_size = False

    for i in range(num_of_creatures):
        if random_color:
            color = Color(randint(0, 255), randint(0, 255), randint(0, 255))
        if random_x:
            x = randint(1, 100)
        if random_y:
            y = randint(1, 100)
        if random_size:
            size = randint(1, 20)
        creature = Point_creature(color, x, y, size)
        creatures.append(creature)

def draw_creatures():
    global creatures
    for creature in creatures:
        creature.draw()

create_creatures_random(10, size = 10)
for creature in creatures:
    print(creature.x)


while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        if event.type == KEYDOWN:
            # 按任意键可以清屏并把点回复到原始状态
            points = []
            screen.fill((255,255,255))
        if event.type == MOUSEBUTTONDOWN:
            screen.fill((255,255,255))
            x = 200
            y = 200
            size = 10
            color = Color(255, 0, 0)
            draw_creatures()
            #creature = Point_creature(color, x, y, size)
            #creature.draw()

    pygame.display.update()
