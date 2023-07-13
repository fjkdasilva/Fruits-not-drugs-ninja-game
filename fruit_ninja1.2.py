# based on https://pythondex.com/create-fruit-ninja-game-in-python-with-code.  Downloaded on 7/11/2023
# I added:
# Sound
# Fruit fragment projectile animations based on fruit colors.
# Improved physics.
# Added skull-and-bones and exploding bombs
# Drug images instead of bobms

import pygame, sys
from pygame.locals import *
import os
import random
from os import listdir

player_lives = 3                                                #keep track of lives
score = 0                                                       #keeps track of score
fruits = ['melon', 'orange', 'pomegranate', 'guava', 'bomb1', 'bomb2', 'bomb4']  #entities in the game.  "Bombs" are drug images.
#fruits = ['orange'] 
# initialize pygame and create window
WIDTH = 800
HEIGHT = 500
FPS = 30                                                 #controls how often the gameDisplay should refresh. In our case, it will refresh every 1/12th second
pygame.init()
pygame.display.set_caption('Fruits-Not-Drugs Ninja Game - Neurotype')
gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT))   #setting game display size
clock = pygame.time.Clock()

# Define colors
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
ORANGE = (255,153,51)
YELLOW = (255,255,51)
GREEN = (0,255,0)
BLUE = (0,0,255)

background = pygame.image.load('back.jpg')                                  #game background
font = pygame.font.Font(os.path.join(os.getcwd(), 'comic.ttf'), 42)
score_text = font.render('Score : ' + str(score), True, (255, 255, 255))    #score display
lives_icon = pygame.image.load('images/white_lives.png')                    #images that shows remaining lives
gravity = 15
# Generalized structure of the fruit Dictionary
def generate_random_fruits(fruit):
    fruit_path = "images/" + fruit + ".png"
    
    image = pygame.image.load(fruit_path)
    height = image.get_height()
    #print(height)
    data[fruit] = {
        'img': pygame.image.load(fruit_path),
        'x' : random.randint(100,700),          #where the fruit should be positioned on x-coordinate
        'y' : 0,
        'scrny':800,
        'vel_y': random.randint(60,130),        #control the speed of fruits in y-directionn ( UP )
        'vel_x': random.randint(-15,15),        #how fast the fruit should move in x direction. Controls the diagonal movement of fruits
        'throw': False,                         #determines if the generated coordinate of the fruits is outside the gameDisplay or not. If outside, then it will be discarded
        'hit': False,
        'img_height': height
    }

    if random.random() >= 0.25:     #25% probability that a fruit will be displayed.
        data[fruit]['throw'] = True
    else:
        data[fruit]['throw'] = False

def generate_fruit_fragments(i,fruit,curx,cury,vel_x,vel_y):
    if 'bomb' in fruit: fruit = 'skull'
    colors = {'skull':(WHITE,BLACK),'orange':(ORANGE,YELLOW),'pomegranate':(RED,WHITE),'guava':(GREEN,RED,YELLOW),'melon':(GREEN,RED)}
    fragments[i] = {
        'x' : curx,          #where the fruit should be positioned on x-coordinate
        'y' : cury,
        'scrny':800,
        'vel_y': random.randint(-30,30)+vel_y,        #control the speed of fruits in y-directionn ( UP )
        'vel_x': random.randint(-30,30)+vel_x,       #how fast the fruit should move in x direction. Controls the diagonal movement of fruits
        'r':random.randint(1,5),
        'cols':colors[fruit]
    }

def load_sounds():
    # set up the mixer
    pygame.mixer.init()
    #pygame.mixer.init(freq, bitsize, channels, buffer)
    soundList = listdir('sounds/')
    #print (soundList)
    swishes = []
    hits = []
    ughs = []
    for sound_name in soundList :
        print (sound_name)
        snd = pygame.mixer.Sound(os.path.join('sounds/', sound_name))
        if 'ugh' in sound_name:
            ughs.append(snd)
        elif 'hit' in sound_name:
            hits.append(snd)
        elif 'swish'in sound_name:
            swishes.append(snd)
    return swishes, hits, ughs

# Load SOUNDS
swishes, hits, ughs = load_sounds()
# Dictionary to hold the data from the random fruit generation
data = {}
# Dictionary to hold the fruit fragments from hit fruit
fragments={}

for fruit in fruits:
    generate_random_fruits(fruit)

def hide_cross_lives(x, y):
    gameDisplay.blit(pygame.image.load("images/red_lives.png"), (x, y))

# Generic method to draw fonts on the screen
font_name = pygame.font.match_font('comic.ttf')
def draw_text(display, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    gameDisplay.blit(text_surface, text_rect)

# draw players lives
def draw_lives(display, x, y, lives, image) :
    for i in range(lives) :
        img = pygame.image.load(image)
        img_rect = img.get_rect()       #gets the (x,y) coordinates of the cross icons (lives on the the top rightmost side)
        img_rect.x = int(x + 35 * i)    #sets the next cross icon 35pixels awt from the previous one
        img_rect.y = y                  #takes care of how many pixels the cross icon should be positioned from top of the screen
        display.blit(img, img_rect)

# show game over display & front display
def show_gameover_screen():
    gameDisplay.blit(background, (0,0))
    draw_text(gameDisplay, "FRUITS-NOT-DRUGS", 90, WIDTH / 2, HEIGHT / 4 -50)
    draw_text(gameDisplay, "NINJA!", 90, WIDTH / 2, HEIGHT / 4 + 50)
    if not game_over :
        draw_text(gameDisplay,"Score : " + str(score), 40, WIDTH / 2, HEIGHT /2 +20)

    draw_text(gameDisplay, "Press a key to begin!", 64, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False

                
def draw_mouse(mouse_locations):
    radius = 1
    color = 130
    for pos in mouse_locations:
        pygame.draw.circle(gameDisplay, (color,color,color), pos, int(radius))
        radius += 1
        color += 10
        
# Game Loop
time =0
first_round = True
game_over = True        #terminates the game While loop if more than 3-Bombs are cut
game_running = True     #used to manage the game loop
mouse_locations = []
current_position =(0,0)
mouse_locations.append(current_position)
while game_running :
    time +=1

    if game_over :
        if first_round :
            show_gameover_screen()
            first_round = False
        game_over = False
        player_lives = 3
        draw_lives(gameDisplay, 690, 5, player_lives, 'images/red_lives.png')
        score = 0

    for event in pygame.event.get():
        # checking for closing window
        if event.type == pygame.QUIT:
            game_running = False

    # Move Fruit        
    if time % 800 == 0:# This determins framerate of falling fruit (position updated every 800 passes through game loop)
        gameDisplay.blit(background, (0, 0))
        gameDisplay.blit(score_text, (0, 0))
        draw_lives(gameDisplay, 690, 5, player_lives, 'images/red_lives.png')
    
        for key, value in data.items():
            if value['throw']:
                value['x'] += value['vel_x']        # moving the fruits in x-coordinates
                value['vel_y'] -= gravity           # decreasing speed due to gravity (note "t" is always 1. One loop through code)
                value['y'] += value['vel_y']        # moving the fruits in y-coordinate
                value['scrny'] = 500-int(value['y'])# invert y-coord (zero aat top, 500 at bottom)
                if value['scrny'] <= 500 and value['scrny'] >= 0:
                    gameDisplay.blit(value['img'], (value['x'], value['scrny']))    #displaying the fruit inside screen dynamically

                else:
                    generate_random_fruits(key) 
                    #print("out of bounds")
        #Move fragments
        for key,value in fragments.items():
                value['x'] += value['vel_x']        # moving the fruit fragments in x-coordinates
                value['vel_y'] -= gravity           # decreasing speed due to gravity (note "t" is always 1. One loop through code)
                value['y'] -= value['vel_y']        # moving the fruit fragments in y-coordinate
                if value['y'] <= 500 and value['y'] >= 0:
                    color = random.choice(value['cols'])
                    pygame.draw.circle(gameDisplay, color, (value['x'],value['y']),value['r'],0)  #displaying the fruit inside screen dynamically

                else:pass
                    
    # End If


    # mouse (updated on every game loop)
    current_position = pygame.mouse.get_pos()   #gets the current coordinate (x, y) in pixels of the mouse
    mouse_locations.append(current_position)
            
    if len(mouse_locations) > 10:  #Keep only last 10 mouse locations (to draw streak instead of a single mousr point.
        mouse_locations.pop(0)

    # Find mouse/fruit overlaps (HITS)
    for key, value in data.items():
        if value['throw']:
            # Check for hit (if not already hit)
            for pos in mouse_locations:
                if  not value['hit'] and pos[0] > value['x'] and pos[0] < value['x']+60 \
                        and pos[1] > value['scrny'] and pos[1] < value['scrny']+60: # HIT
                    
                    if 'bomb' in key: # Bomb hit
                        half_fruit_path = "images/skullLarge.png"

                        for fragment in range(20):
                            generate_fruit_fragments(fragment,key,pos[0],pos[1],value['vel_x'],value['vel_y'])

                        randsnd = random.randint(0, len(ughs)-1)
                        ughs[randsnd].play() # also pygame.mixer.Sound.play(mysounds[randsnd])
                        
                        player_lives -= 1
                        if player_lives == 0:
                            
                            hide_cross_lives(690, 15)
                        elif player_lives == 1 :
                            hide_cross_lives(725, 15)
                        elif player_lives == 2 :
                            hide_cross_lives(760, 15)
                            
                        #if the user clicks bombs for three time, GAME OVER message should be displayed and the window should be reset
                        if player_lives < 0 :
                            show_gameover_screen()
                            game_over = True

                    else: # Fruit hit
                        # Create fruit fragments
                        for fragment in range(20):
                            generate_fruit_fragments(fragment,key,pos[0],pos[1],value['vel_x'],value['vel_y'])

                        half_fruit_path = "images/" + "half_" + key + ".png"
                        # Selec a sound to play
                        randsnd = random.randint(0, len(hits)-1)
                        hits[randsnd].play() # also pygame.mixer.Sound.play(mysounds[randsnd])                        

                    value['img'] = pygame.image.load(half_fruit_path)
                    
                    if key != 'bomb' : #Fruit hit, so set it to hit
                        score += 1
                    score_text = font.render('Score : ' + str(score), True, (255, 255, 255))
                    value['hit'] = True
        else:
            generate_random_fruits(key)

    
    #print(mouse_locations)
    draw_mouse(mouse_locations)

    pygame.display.update()
                        

pygame.quit()
