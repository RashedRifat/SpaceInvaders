import pygame 
import os 
import random 
from lasers import collide 

# Load special objects 
SPECIAL_1 = pygame.image.load(os.path.join("assets", "special_item_1.png"))
SPECIAL_2 = pygame.image.load(os.path.join("assets", "special_item_2.png"))

class SpecialItem:
    compendium = {'heart': SPECIAL_1,
                  'streak' : SPECIAL_2,            
    }

    def __init__(self, HEIGHT, WIDTH, FPS, type):
        self.type = type.lower().strip()
        self.img = self.compendium[type]
        self.x = random.randrange(50, WIDTH-100)
        self.y = random.randrange(100, HEIGHT-200)
        self.mask = pygame.mask.from_surface(self.img)
        self.counter = 3 * FPS
        self.expired = False
    
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def collision(self, obj):
        return collide(self, obj)

    def decrement(self):
        self.counter -= 1
        if self.counter < 0:
            self.expired = True
    
    def on_collision(self, player_ship):
        if self.type == "heart":
            player_ship.heal(10)
        elif self.type == "streak":
            player_ship.streak += 2
            player_ship.health -= 1
        elif self.type == 'speed':
            pass 
    
