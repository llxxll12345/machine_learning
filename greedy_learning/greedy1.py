import random, pygame, sys
from pygame import *
import human as hu
import numpy as np
import snakedqn
import ca
import cv2
#from dqn import *
#initialization
clock = pygame.time.Clock()
FPS = 1

WINDOWWIDTH = 300
WINDOWHEIGHT = 300
CELLSIZE = 60
assert WINDOWHEIGHT % CELLSIZE == 0, "Window width must be a multiple of cell size!"
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size!"

CELLWIDTH = WINDOWWIDTH // CELLSIZE
CELLHEIGHT = WINDOWHEIGHT // CELLSIZE

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
BLUE     = (   0,  0,   255)
DARKBLUE = (   0,  0,   155)
DARKGRAY  = ( 100,  100,  100)
BGCOLOR = WHITE


UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

player_ca = 0
player_dqn = 1
player_human = 2
player_list = ['CA', 'CN', 'HU']

ca_direction = UP
DIRECTION = [UP,DOWN,LEFT,RIGHT]

HEAD = 0 # syntactic sugar: index of the snake's head

class dqn_operator(object):
    def __init__(self, snakeCoords, food, dqn, image_data, food_list):
        self.snakeCoords = snakeCoords
        self.food = food
        self.episode = 1 
        self.dqn = dqn 
        self.direction = RIGHT
        #self.a0 = np.array([1, 0, 0, 0])
        sc, re, done = self.frameStep(0, image_data, food_list)
        sc = cv2.cvtColor(cv2.resize(sc, (84, 84)), cv2.COLOR_BGR2GRAY)
        _, sc = cv2.threshold(sc, 200, 255, cv2.THRESH_BINARY)
        print(sc)
        self.dqn.initState(sc)

    def screen_handle(self, sc):
        res_sc = cv2.cvtColor(cv2.resize(sc, (84, 84)), cv2.COLOR_BGR2GRAY)
        _, bin_sc = cv2.threshold(res_sc, 200, 255, cv2.THRESH_BINARY)
        bin_sc = np.reshape(bin_sc, (84, 84, 1))
        return bin_sc
        
    def dqn_operate(self, image_data, food_list):
        direction = self.dqn.getAction()
        sc1, r, done = self.frameStep(direction, image_data, food_list)
        sc1 = self.screen_handle(sc1)
        ts, qv = self.dqn.addReplay(sc1, direction, r, done)
        if done == True:
            return -1
        else:
            return self.direction
            # for Summary

    def frameStep(self, action, image_data, food_list):
        image_data, reward, done = self.runGame(action, image_data, food_list)
        return image_data, reward, done

    def runGame(self, action, image_data, food_list):
        if action == UP and self.direction != DOWN:
            self.direction = UP
        elif action == DOWN and self.direction != UP:
            self.direction = DOWN
        elif action == RIGHT and self.direction != RIGHT:
            self.direction = LEFT
        elif action == LEFT and self.direction != LEFT:
            self.direction = RIGHT
        
        # check if the worm has hit itself or the edge
        reward = -0.1
        done = False
        if self.snakeCoords[HEAD]['x'] < 0 or self.snakeCoords[HEAD]['x'] >=  CELLWIDTH or self.snakeCoords[HEAD]['y'] < 0 or self.snakeCoords[HEAD]['y'] >= CELLHEIGHT:
            done = True
            reward = -1
            image_data = pygame.surfarray.array3d(pygame.display.get_surface())[WINDOWWIDTH:WINDOWWIDTH * 2]
            return image_data, reward, done
        for self.wormBody in self.snakeCoords[1:]:
            if self.wormBody['x'] == self.snakeCoords[HEAD]['x'] and self.wormBody['y'] == self.snakeCoords[HEAD]['y']:
                done = True
                reward = -1
                image_data = pygame.surfarray.array3d(pygame.display.get_surface())[WINDOWWIDTH:WINDOWWIDTH * 2]
                return image_data, reward, done

        res = player_update(self.snakeCoords, self.food, self.direction, food_list)
        self.snakeCoords = res[0]
        self.food = res[1]
        image_data = pygame.surfarray.array3d(pygame.display.get_surface())
        #print(image_data)
        return image_data, reward, done

def player_update(snakeCoords,food,direction, food_list):
    if direction == UP:
        newHead = {'x': snakeCoords[HEAD]['x'], 'y': snakeCoords[HEAD]['y'] - 1}
    elif direction == DOWN:
        newHead = {'x': snakeCoords[HEAD]['x'], 'y': snakeCoords[HEAD]['y'] + 1}
    elif direction == LEFT:
        newHead = {'x': snakeCoords[HEAD]['x'] - 1, 'y': snakeCoords[HEAD]['y']}
    elif direction == RIGHT:
        newHead = {'x': snakeCoords[HEAD]['x'] + 1, 'y': snakeCoords[HEAD]['y']}
    snakeCoords.insert(0, newHead) 
    if snakeCoords[HEAD]['x'] == food['x'] and snakeCoords[HEAD]['y'] == food['y']:
        #food = getRandomLocation(snakeCoords)
        food = food_list[len(snakeCoords) - 2]
    else:
        del snakeCoords[-1]
    return (snakeCoords, food)

#run the game
def runGame():
    global is_running,DIRECTION, ca_over, human_over
    ca_player = ca.ca(CELLWIDTH, CELLHEIGHT)
    ca_over = False
    human_over = False
    dqn_over = False
    cnn = snakedqn.DQN(0.99, 0, 0.001, 0.001, 50000, 32, 4)
    # Set a random start point.
    startx = random.randint(0, CELLWIDTH - 5)
    starty = random.randint(0, CELLHEIGHT - 5)
    ca_snakeCoords = [{'x': startx, 'y': starty}, {'x': startx - 1, 'y': starty}, {'x': startx - 2, 'y': starty}]
    hu_snakeCoords = [{'x': startx, 'y': starty}, {'x': startx - 1, 'y': starty}, {'x': startx - 2, 'y': starty}]
    dqn_snakeCoords = [{'x': startx, 'y': starty}, {'x': startx - 1, 'y': starty}, {'x': startx - 2, 'y': starty}]
    ca_direction = RIGHT
    hu_direction = RIGHT
    is_running = True

    #food = getRandomLocation(ca_snakeCoords)
    food_list = get_food_list()
    hu_food = food_list[0]
    food = food_list[0]
    dqn_food = food_list[0]
    drawSnaky(game_screen, dqn_snakeCoords, player_dqn)
    image_data = pygame.surfarray.array3d(pygame.display.get_surface())[WINDOWWIDTH:WINDOWWIDTH * 2]
    op = dqn_operator(dqn_snakeCoords, food, cnn, image_data, food_list)

    while True:
        if human_over == False:
            clock.tick(FPS + len(hu_snakeCoords) - 3)
        else:
            clock.tick(10)
        pressed = checkForKeyPress()
        if ca_over and human_over and dqn_over:
            if pressed != None:
                return
        if full(game_screen, ca_snakeCoords, food) == True:
            ca_over = True
        if full(game_screen, hu_snakeCoords, hu_food) == True:
            human_over = True
        if full(game_screen, dqn_snakeCoords, dqn_food) == True:
            dqn_over = True
        #print("run")
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
        
        if ca_over == False:
            ca_direction = ca_player.ca_operation(ca_snakeCoords, food, ca_direction)
            if ca_direction == -1 or ca_direction == None:
                ca_over = True
            #make move
            else:
                coords = player_update(ca_snakeCoords, food, ca_direction, food_list)
                ca_snakeCoords = coords[0]
                food = coords[1]
            

        if human_over == False:
            hu_direction = hu.human_operation(hu_direction, hu_snakeCoords, pressed, CELLWIDTH, CELLHEIGHT)
            if hu_direction == -1:
                human_over = True
            else:
                coords = player_update(hu_snakeCoords, hu_food, hu_direction, food_list)
                hu_snakeCoords = coords[0]
                hu_food = coords[1]

        if dqn_over == False:
            image_data = pygame.surfarray.array3d(pygame.display.get_surface())[WINDOWWIDTH:WINDOWWIDTH * 2]
            res = op.dqn_operate(image_data, food_list)
            if res == -1:
                dqn_over = True
            else:
                dqn_direction = res

        game_screen.fill(BGCOLOR)
        #draw
        if ca_over == False:
            drawSnaky(game_screen, ca_snakeCoords, player_ca)
            drawFood(game_screen, food, player_ca)  
            drawScore(game_screen, len(ca_snakeCoords) - 3, player_ca)
        else:
            showOver(game_screen, player_ca)

        if human_over == False:
            drawSnaky(game_screen, hu_snakeCoords, player_human)
            drawFood(game_screen, hu_food, player_human)
            drawScore(game_screen, len(hu_snakeCoords) - 3, player_human)
        else:
            showOver(game_screen, player_human)

        if dqn_over == False:
            drawSnaky(game_screen, dqn_snakeCoords, player_dqn)
            drawFood(game_screen, op.food, player_dqn)
            drawScore(game_screen, len(dqn_snakeCoords) - 3, player_dqn)
        else:
            showOver(game_screen, player_dqn)

        pygame.draw.line(game_screen, (0, 0, 0), (300, 0), (300, 300), 2)
        pygame.draw.line(game_screen, (0, 0, 0), (600, 0), (600, 300), 2)

        pygame.display.update()
        #pygame.time.wait(10 + len(ca_snakeCoords))

#main
def main():
    global  game_screen, FONT

    pygame.init()
    game_screen = pygame.display.set_mode((WINDOWWIDTH * 4, WINDOWHEIGHT))
    #FONT = pygame.font.Font('freesansbold.ttf', 18)

    showStartScreen(game_screen)
    while True:
        runGame()

def checkForKeyPress():
    #ok
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    #print("keyupeventlist : ", keyUpEvents)
    if len(keyUpEvents) == 0:
        return None
    pressed = keyUpEvents[0].key
    #print("key pressed : ", pressed)
    if pressed == K_ESCAPE:
        terminate()
    if pressed == K_UP:
        return UP
    elif pressed == K_DOWN:
        return DOWN
    elif pressed == K_LEFT:
        return LEFT
    elif pressed == K_RIGHT:
        return RIGHT
    return keyUpEvents[0].key


def get_food_list():
    food_list = []
    for i in range(CELLWIDTH):
        for j in range(CELLHEIGHT):
            food_list.append({'x': i, 'y': j})

    for i in range(len(food_list)):
        index = random.randint(0, len(food_list) - 1)
        while index == i:
            index = random.randint(0, len(food_list) - 1)
        temp = food_list[index]
        food_list[index] = food_list[i]
        food_list[i] = temp

    return food_list

def showStartScreen(game_screen):
    while True:
        game_screen.fill(BGCOLOR)
        FONT = pygame.font.Font('freesansbold.ttf', 30)
        pressKeySurf = FONT.render('Press a key to start.', True, DARKGRAY)
        pressKeyRect = pressKeySurf.get_rect()
        pressKeyRect.topleft = (300, 150)
        game_screen.blit(pressKeySurf, pressKeyRect)

        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return
        pygame.display.update()


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation(snake):
    temp = {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}
    while testStuck(temp, snake):
        temp = {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}
    return temp


def testStuck(temp, snake):
    for body in snake:
        if temp['x'] == body['x'] and temp['y'] == body['y']:
            return True
    return False


def full(game_screen, snake, food):
    length = len(snake)
    x = food['x']
    y = food['y']
    if ([x - 1, y] in snake and [x + 1, y] in snake and[x, y + 1] in snake and [x, y - 1] in snake) or (length == CELLWIDTH * CELLHEIGHT - 1):
        print("full screen!")
        gameOverFont = pygame.font.Font('freesansbold.ttf', 30)
        gameSurf = gameOverFont.render('FULL SCREEN!', True, RED)
        gameRect = gameSurf.get_rect()
        gameRect.midtop = (WINDOWWIDTH / 2, 200)

        game_screen.blit(gameSurf, gameRect)
        pygame.display.update()
        pygame.time.wait(500)
        return True
    return False


def showOver(game_screen, player):
    gameOverFont = pygame.font.Font('freesansbold.ttf', 75)
    gameSurf = gameOverFont.render('Opps!', True, BLACK)
    gameRect = gameSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH * (player + 0.5), 10)
    game_screen.blit(gameSurf, gameRect)
    pygame.display.update()
    #checkForKeyPress() # clear out any key presses in the event queue


def drawScore(game_screen, score, player):
    FONT = pygame.font.Font('freesansbold.ttf', 18)
    scoreSurf = FONT.render(player_list[player] + ' Score: ' + str(score), True, BLACK)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH * (player + 1) - 120 , 10)
    game_screen.blit(scoreSurf, scoreRect)


def drawSnaky(game_screen, ca_snakeCoords, player):
    cnt = 0
    for coord in ca_snakeCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        snakeRect = pygame.Rect(x + WINDOWWIDTH * player, y, CELLSIZE, CELLSIZE)
        r = DARKGRAY[0]
        g = DARKGRAY[1]
        b = DARKGRAY[2]
        if player == 0:
            rr = int(r + 100/len(ca_snakeCoords) * cnt) % 256
            gg = int(g + 100/len(ca_snakeCoords) * cnt) % 256
            bb = int(b - 100/len(ca_snakeCoords) * cnt + 256) % 256
        elif player == 1:
            '''
            rr = int(r - 100/len(ca_snakeCoords) * cnt + 256) % 256
            gg = int(g + 100/len(ca_snakeCoords) * cnt) % 256
            bb = int(b + 100/len(ca_snakeCoords) * cnt) % 256
            '''
            rr = 0
            gg = 255
            bb = 0
        elif player == 2:
            rr = int(r + 100/len(ca_snakeCoords) * cnt) % 256
            gg = int(g - 100/len(ca_snakeCoords) * cnt + 256) % 256
            bb = int(b + 100/len(ca_snakeCoords) * cnt) % 256

        pygame.draw.rect(game_screen, (rr, gg, bb), snakeRect)
        cnt += 1


def drawFood(game_screen, coord, player):
    #ok
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    foodRect = pygame.Rect(x + WINDOWWIDTH * player, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(game_screen, RED, foodRect)
    

'''
def drawGrid():
    #ok
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(game_screen, WHITE, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(game_screen, WHITE, (0, y), (WINDOWWIDTH, y))

is_running = True
'''

if __name__ == '__main__':
    main()