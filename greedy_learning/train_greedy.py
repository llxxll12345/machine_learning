import snakedqn 
import numpy as np
import random, pygame, sys
import cv2
import greedy1
import time

UP = 0
DOWN = 1
RIGHT = 2
LEFT = 3

HEAD = 0

START_TIME = 0
rest = []
qv_list = []

def apmax(a, b):
    if a > b:
        return a
    return b

class dqn_operator(object):
    def __init__(self, snakeCoords, food, dqn, WINDOWWIDTH, WINDOWHEIGHT, CELLSIZE, image_data):
        self.snakeCoords = snakeCoords
        self.food = food
        self.episode = 1 
        self.dqn = dqn 
        self.direction = RIGHT
        self.WINDOWWIDTH = WINDOWWIDTH
        self.WINDOWHEIGHT = WINDOWHEIGHT
        self.CELLSIZE = CELLSIZE
        self.CELLWIDTH = self.WINDOWWIDTH // self.CELLSIZE
        self.CELLHEIGHT = self.WINDOWHEIGHT // self.CELLSIZE
        #self.a0 = np.array([1, 0, 0, 0])
        sc, re, done = self.frameStep(0, image_data)
        sc = cv2.cvtColor(cv2.resize(sc, (84, 84)), cv2.COLOR_BGR2GRAY)
        #cv2.imshow('image', sc)
        _, sc = cv2.threshold(sc, 1, 255, cv2.THRESH_BINARY)
        #cv2.imshow('image1', sc)
        #print(sc)
        self.dqn.initState(sc)

    def screen_handle(self, sc):
        res_sc = cv2.cvtColor(cv2.resize(sc, (84, 84)), cv2.COLOR_BGR2GRAY)
        _, bin_sc = cv2.threshold(res_sc, 1, 255, cv2.THRESH_BINARY)
        bin_sc = np.reshape(bin_sc, (84, 84, 1))
        
        return bin_sc
        
    def dqn_operate(self, image_data):
        direction = self.dqn.getAction()
        sc1, re, done = self.frameStep(direction, image_data)
        sc1 = self.screen_handle(sc1)
        cv2.imshow('image', sc1)
        ts, qv = self.dqn.addReplay(sc1, direction, re, done)
        if done == True:
            return -1
        else:
            return self.direction
            # for Summary

    def frameStep(self, action, image_data):
        image_data, reward, done = self.runGame(action, image_data)
        return image_data, reward, done

    def runGame(self, action, image_data):
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
        if self.snakeCoords[HEAD]['x'] < 0 or self.snakeCoords[HEAD]['x'] >= self.CELLWIDTH or self.snakeCoords[HEAD]['y'] < 0 or self.snakeCoords[HEAD]['y'] >= self.CELLHEIGHT:
            done = True
            reward = -1
            image_data = pygame.surfarray.array3d(pygame.display.get_surface())[self.WINDOWWIDTH:self.WINDOWWIDTH * 2]
            return image_data, reward, done
        for self.wormBody in self.snakeCoords[1:]:
            if self.wormBody['x'] == self.snakeCoords[HEAD]['x'] and self.wormBody['y'] == self.snakeCoords[HEAD]['y']:
                done = True
                reward = -1
                image_data = pygame.surfarray.array3d(pygame.display.get_surface())[self.WINDOWWIDTH:self.WINDOWWIDTH * 2]
                return image_data, reward, done

        # check if worm has eaten an food
        # remove worm's tail segment

        res = play_update(self.snakeCoords, self.food, self.direction, )
        self.snakeCoords = res[0]
        self.food = res[1]
        image_data = pygame.surfarray.array3d(pygame.display.get_surface())[self.WINDOWWIDTH:self.WINDOWWIDTH * 2]
        return image_data, reward, done

def put_text(content, x, y, game_screen, size):
    font = pygame.font.Font('freesansbold.ttf', size)
    Surf = font.render(content, True, (1, 1, 1))
    Rect = Surf.get_rect()
    Rect.topleft = (x, y)
    game_screen.blit(Surf, Rect)
    
def judge(num, limit):
    if num < limit:
        return 1
    return num // limit

def play_update(snakeCoords,food,direction):
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
        food = greedy1.getRandomLocation(snakeCoords)
    else:
        del snakeCoords[-1]
    return (snakeCoords, food)

def show_Statistics(res, game_screen, num_move, out_put):
    #print(len(res))
    scale_n = [1, 1e3, 1e6, 1e9]
    scale_w = {'1000000000': 'b', '1000000': 'm', '1000': 'k', '1': ' '}

    max_y = -10
    for j in res:
        if max_y < j:
            max_y = j
            last_x = 20
   
    last_x = 20
    last_y = 280
    inter_pt = 260 // (len(res) + 1)
    for i in range(len(res)):
        x = i * inter_pt + last_x
        y = last_y - int((260 / 25) * res[i])
        pygame.draw.circle(game_screen, (0, 0, 255), (x, y), 0, 0)
        #pygame.draw.line(game_screen, (255, 0, 0), (x, y), (last_x, last_y), 1)
        
    last_x = 20
    last_y = 580
    inter_pt = 260 // (len(out_put) + 1)
    for i in range(len(out_put)):
        x = i * inter_pt + last_x
        print(list(out_put))
        y = last_y - int((260 / 100) * out_put[i])
        pygame.draw.circle(game_screen, (0, 0, 255), (x, y), 0, 0)
        #pygame.draw.line(game_screen, (255, 0, 0), (x, y), (last_x, last_y), 1)

    pygame.draw.line(game_screen, (0, 0, 0), (20, 20), (20, 280), 2)
    pygame.draw.line(game_screen, (0, 0, 0), (20, 280), (280,280), 2)
    pygame.draw.line(game_screen, (0, 0, 0), (20, 320), (20, 580), 2)
    pygame.draw.line(game_screen, (0, 0, 0), (20, 580), (280,580), 2)

 
    put_text("max score: " + str(max_y), 600, 20, game_screen, 30)
    put_text(str(max_y), 10, 10, game_screen, 10)
    index = -1
    for scale in scale_n:
        if scale > len(res):
            break
        index += 1
    put_text("episodes: " + str(round(len(res) / scale_n[index] , 2)) + scale_w[str(int(scale_n[index]))] , 600, 70, game_screen, 30)
    print("episodes" + str(round(len(res) / scale_n[index] , 2)))
    index = -1
    for scale in scale_n:
        if scale > num_move:
            break
        index += 1
    put_text("total moves: " + str(round(num_move / scale_n[index], 2)) + scale_w[str(int(scale_n[index]))], 600, 120, game_screen, 30)
    print("total moves" + str(num_move))
    put_text("recent output: " + str(np.argmax(output)), 600, 170, game_screen, 30)
    current_time = round(time.clock(), 2) - START_TIME
    put_text("Time elapsed: " + str(int(current_time) // 3600) + " : " + str((int(current_time) % 3600) //60) + " : " + str((int(current_time) % 3600) % 60), 600, 220, game_screen, 20)
    print("time now is:" + str(current_time))
    '''
        for i in range(0, max_y, interval):
            put_text(str(i), 0, 280 - i * 26, game_screen)
        for i in range(0, len_rep, inter_res):
            put_text(str(i * inter_res), 20 + i * 26 , 290, game_screen)
    '''



def run(dqn):
    pygame.init()
    pygame.init()
    dqn.episode += 1
    game_screen = pygame.display.set_mode((greedy1.WINDOWWIDTH * 3, greedy1.WINDOWHEIGHT))
    dqn_over = False
    startx = random.randint(0, greedy1.CELLWIDTH - 3)
    starty = random.randint(0, greedy1.CELLHEIGHT - 3)
    dqn_snakeCoords = [{'x': startx, 'y': starty}, {'x': startx - 1, 'y': starty}, {'x': startx - 2, 'y': starty}]
    dqn_direction = RIGHT
    is_running = True
    dqn_food = greedy1.getRandomLocation(dqn_snakeCoords)
    greedy1. drawSnaky(game_screen, dqn_snakeCoords, greedy1.player_dqn)
    image_data = pygame.surfarray.array3d(pygame.display.get_surface())[greedy1.WINDOWWIDTH:greedy1.WINDOWWIDTH * 2]
    #print(image_data)
    op = dqn_operator(dqn_snakeCoords, dqn_food, dqn, greedy1.WINDOWWIDTH, greedy1.WINDOWHEIGHT, greedy1.CELLSIZE, image_data)
    START_TIME = round(time.clock(), 2)
    while True:
        #print(len(rest))
        #pressed = greedy1.checkForKeyPress()
        
        if greedy1.full(game_screen, dqn_snakeCoords, dqn_food) == True:
            dqn_over = True
        #print("run")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        if dqn_over == False:
            image_data = pygame.surfarray.array3d(pygame.display.get_surface())[greedy1.WINDOWWIDTH:greedy1.WINDOWWIDTH * 2]
            res = op.dqn_operate(image_data)
            if res == -1:
                dqn_over = True
            else:
                dqn_direction = res

        game_screen.fill(greedy1.BGCOLOR)
        #draw
        if dqn_over:
            rest.append(len(dqn_snakeCoords) - 3)
            return
        
        greedy1.drawSnaky(game_screen, dqn_snakeCoords, greedy1.player_dqn)
        greedy1.drawFood(game_screen, dqn_food, greedy1.player_dqn)
        #greedy1.drawScore(game_screen, len(dqn_snakeCoords) - 3, greedy1.player_dqn)
        qv_list.append(dqn.qv)
        show_Statistics(rest, game_screen, len(dqn.repmem), qv_list)

        pygame.draw.line(game_screen, (0, 0, 0), (300, 0), (300, 300), 2)
        pygame.draw.line(game_screen, (0, 0, 0), (600, 0), (600, 300), 2)

        pygame.display.update()
        #pygame.time.wait(10 + len(ca_snakeCoords))

def main():
    dqn = snakedqn.DQN(0.99, 0, 1, 0.001, 50000, 32, 4)
    while True:
        run(dqn)

if __name__ == "__main__":
    main()