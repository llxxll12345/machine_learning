import random, pygame, sys
from pygame.locals import *

FPS = 20
WINDOWWIDTH = 200
WINDOWHEIGHT = 200
CELLSIZE = 40
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

            #R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
BRIGREEN  = (150, 255, 150)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0
pygame.init()
FPSCLOCK = pygame.time.Clock()
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
pygame.display.set_caption('Snake')
episode = 0
class game_state:
    def __init__(self):
    	# init the game
        global FPSCLOCK, DISPLAYSURF, BASICFONT, episode
        episode = episode + 1
        # starting point of the snake
        self.startx = random.randint(3, 4)
        self.starty = random.randint(3, 4)
        # starting coords
        self.snake_coords = [{'x': self.startx,     'y': self.starty},
                    {'x': self.startx - 1, 'y': self.starty},
                    {'x': self.startx - 2, 'y': self.starty}]
        # starting direction
        self.direction = RIGHT
        self.totalscore = 0
        # init food location
        self.food = self.get_random_location(self.snake_coords)
        
    def frame_step(self, action):
    	# get the current frame data of the game
        image_data, reward, done = self.run_game(action)

        return image_data, reward, done

    def full_screen(self, snake):
    	# if the snake eats to full screen
        return len(snake) >= 24

    def run_game(self, action):
        global episode
        for event in pygame.event.get():
            if event.type == QUIT:
                self.terminate()
        self.pre_direction = self.direction
        #action[0] up
        #action[1] down
        #action[2] left
        #action[3] right
        if self.full_screen(self.snake_coords):
            done = True
            reward = -1
            image_data = pygame.surfarray.array3d(pygame.display.get_surface())
            return image_data, reward, done

        # check if directions don't conflict with each other
        if (action[0] == 1) and self.direction != DOWN:
            self.direction = UP
        elif (action[1] == 1) and self.direction != UP:
            self.direction = DOWN
        elif (action[2] == 1) and self.direction != RIGHT:
            self.direction = LEFT
        elif (action[3] == 1) and self.direction != LEFT:
            self.direction = RIGHT
        
        reward = -0.1
        done = False

        # update the snake body
        if self.snake_coords[HEAD]['x'] == -1 or self.snake_coords[HEAD]['x'] == CELLWIDTH or self.snake_coords[HEAD]['y'] == -1 or self.snake_coords[HEAD]['y'] == CELLHEIGHT:
            done = True
            reward = -1
            image_data = pygame.surfarray.array3d(pygame.display.get_surface())
            return image_data, reward, done
        for self.wormBody in self.snake_coords[1:]:
            if self.wormBody['x'] == self.snake_coords[HEAD]['x'] and self.wormBody['y'] == self.snake_coords[HEAD]['y']:
                done = True
                reward = -1
                image_data = pygame.surfarray.array3d(pygame.display.get_surface())
                return image_data, reward, done

        # update food location and snake length
        if self.snake_coords[HEAD]['x'] == self.food['x'] and self.snake_coords[HEAD]['y'] == self.food['y']:
            self.food = self.get_random_location(self.snake_coords) # set a new food somewhere
            reward = 2
            self.totalscore = self.totalscore + 1
        else:
            del self.snake_coords[-1] 

        # get the location of the new head after the movement
        if not self.examine_direction(self.direction, self.pre_direction):
            self.direction = self.pre_direction
        if self.direction == UP:
            self.new_head = {'x': self.snake_coords[HEAD]['x'], 'y': self.snake_coords[HEAD]['y'] - 1}
        elif self.direction == DOWN:
            self.new_head = {'x': self.snake_coords[HEAD]['x'], 'y': self.snake_coords[HEAD]['y'] + 1}
        elif self.direction == LEFT:
            self.new_head = {'x': self.snake_coords[HEAD]['x'] - 1, 'y': self.snake_coords[HEAD]['y']}
        elif self.direction == RIGHT:
            self.new_head = {'x': self.snake_coords[HEAD]['x'] + 1, 'y': self.snake_coords[HEAD]['y']}
        self.snake_coords.insert(0, self.new_head)
        DISPLAYSURF.fill(BGCOLOR)
       
        self.draw_snake(self.snake_coords)
        self.draw_apple(self.food)
       
       	# refresh the screen
        image_data = pygame.surfarray.array3d(pygame.display.get_surface())
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        return image_data, reward, done

    def examine_direction(self, temp , direction):
    	# check if direction don't conflict
        if direction == UP:
            if temp == DOWN:
                return False
        elif direction == RIGHT:
            if temp == LEFT:
                return False
        elif direction == LEFT:
            if temp == RIGHT:
                return False
        elif direction == DOWN:
            if temp == UP:
                return False
        return True
    
    def ret_score(self):
    	# return score
        global episode
        tmp1 = self.totalscore
        tmp2 = episode
        self.__init__()
        return tmp1, tmp2 

    def terminate(self):
    	# terminate the game client
        pygame.quit()
        sys.exit()

    def get_random_location(self, worm):
    	# generate random location for general purpose
        temp = {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}
        while self.is_snake(temp, worm):
            temp = {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}
        return temp

    def is_snake(self, temp, worm):
    	# check if a bolck is occupied by the snake body
        for body in worm:
            if temp['x'] == body['x'] and temp['y'] == body['y']:
                return True
        return False


    def draw_snake(self, snake_coords):
    	# draw the snake body
        a = 0
        for coord in snake_coords:
            x = coord['x'] * CELLSIZE
            y = coord['y'] * CELLSIZE
            wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
            r = int(DARKGREEN[0] + (BRIGREEN[0] - DARKGREEN[0]) / len(snake_coords) * a)
            g = int(DARKGREEN[1] + (BRIGREEN[1] - DARKGREEN[1]) / len(snake_coords) * a)
            b = int(DARKGREEN[2] + (BRIGREEN[2] - DARKGREEN[2]) / len(snake_coords) * a)
            pygame.draw.rect(DISPLAYSURF, (r, g, b), wormSegmentRect)
            a += 1
            if a == 0:
                wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
                pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)


    def draw_apple(self, coord):
    	# draw the apple
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, RED, appleRect)


