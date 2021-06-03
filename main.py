import pygame
import os
import random
import math
from ships import Ship, Player, Enemey
from lasers import Laser, collide
from special import SpecialItem

# Load the display 
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders!")

# Background and fonts
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))
pygame.font.init()

def main():
    ''' Main function that handles the logic of the game. '''

    # Create the fonts
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 70)

    # Set game variables 
    run = True
    FPS = 60
    level = 0
    lives = 5
    
    # Set enemy variables 
    wave_length = 5
    enemies = []
    enemy_vel = 1
    special_items = []

    # Set level/lost variables 
    lost = False
    lost_count = 0

    new_level = False
    new_level_counter = 0
    heal_amount = 0

    # Set player variables 
    player_vel = 5
    laser_vel = 5

    player = Player(300, 630, health=100)
    clock = pygame.time.Clock()

    def redraw_window():
        ''' Redraws the window to update the game. '''

        WIN.blit(BG, (0,0))

        # Draw text 
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        streak_label = main_font.render(f"Streak: {player.streak}", 1, (255,255,255))

        WIN.blit(lives_label, (10,10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() -10,10))
        WIN.blit(streak_label, (10, lives_label.get_height() + 10))

        # Draw the enemies and player 
        for enemy in enemies:
            enemy.draw(WIN)
        for item in special_items:
            item.draw(WIN)
        player.draw(WIN)

        # If you lost the game, set the ending screen 
        if lost:
            lost_label = lost_font.render("You Lost!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))
        
        # If you passed a new level, display message 
        if new_level:
            new_level_label = main_font.render(f"Level {level}", 1, (255,255,255))
            energy_label = main_font.render(f"Your ship regains {heal_amount} units of energy.", 1, (255,255,255))
            WIN.blit(new_level_label, (WIDTH/2 - new_level_label.get_width()/2, 350))
            WIN.blit(energy_label, (WIDTH/2 - energy_label.get_width()/2, 350 + new_level_label.get_height() + 10))
        
            if level == 3:
                upgrade_label = main_font.render(f"You manage to find an upgrade...", 1, (255,255,255))
                WIN.blit(upgrade_label, (WIDTH/2 - upgrade_label.get_width()/2, 360 + (new_level_label.get_height() * 2)))

        pygame.display.update()

    # Main loop to run the code 
    while run:
        clock.tick(FPS)
        redraw_window()

        # Handle player losing 
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        
        if lost:
            if lost_count > FPS * 5:
                 run = False
            else:
                continue
        
        # If a new level, let the player know. 
        if new_level:
            if new_level_counter > 0:
                new_level_counter -= 1
                continue
            else:
                new_level = False
                heal_amount = 0
        

        # Increment the level and wavelength depending on enemy disappearance 
        if len(enemies) == 0:
            level += 1
            wave_length += 3

            # Heal the user based on the current streak
            if level > 1:
                heal_amount = 20 + (math.floor(player.streak / 5) * 10)
                player.heal(heal_amount)
                new_level = True
                new_level_counter = FPS * 2

            for i in range(wave_length):
                enemy = Enemey(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        # Spawn special items randomly 
        if random.randrange(0, 2000) == 1:
            item = SpecialItem(HEIGHT, WIDTH, FPS, random.choice(["streak", "heart"]))
            special_items.append(item)

        # Close the game 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        # Process user input and move the player
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player.x - player_vel > 0: # move left 
            player.x -= player_vel
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player.x + player.get_width() + player_vel < WIDTH: # move right 
            player.x += player_vel
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and player.y - player_vel > 0: # move up 
            player.y -= player_vel
        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player.y + player.get_height() + player_vel < HEIGHT: # move down 
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot(level)
        
        # Move the enemies and handle collisions
        for enemy in enemies:
            enemy.move(enemy_vel, WIDTH)
            enemy.move_lasers(laser_vel, player, HEIGHT)

            if random.randrange(0, 2 * FPS) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
                player.streak = 0

            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
                player.streak = 0
        
        # Handle expiring special items:
        for sitem in special_items:
            if sitem.expired:
                special_items.remove(sitem)
            elif collide(player, sitem):
                sitem.on_collision(player)
                special_items.remove(sitem)
            else:
                sitem.decrement()


        # Move player lasers on the screen 
        player.move_lasers(-1 * laser_vel, enemies, special_items, HEIGHT)

        # Set a multiplier for the streak 
        multiplier = math.floor(player.streak / 5)
        if multiplier == 0:
            player_vel = 5
        else:
            multiplier = 4 if multiplier > 4 else multiplier
            player_vel = 5 + (multiplier * 2)


def main_menu():
    ''' Creates the title screen for the game. '''

    title_font = pygame.font.SysFont("comicsans", 70)
    subtitle_font = pygame.font.SysFont("comicsans", 50)
    run = True
    while run:

        # Render the title screen 
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Welcome to Space Invaders!", 1, (255,255,255))
        subtitle_label = subtitle_font.render("Click anywhere to begin playing!", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        WIN.blit(subtitle_label, (WIDTH/2 - subtitle_label.get_width()/2, 350 + title_label.get_height() + 10))
        pygame.display.update()

        # Process user input and either start the game or close it. 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()