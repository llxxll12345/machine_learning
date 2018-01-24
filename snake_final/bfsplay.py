import random, pygame,sys
import snaky as game
import numpy as np
import queue
import time

inf = 10000
DOWN = 0
UP = 1
LEFT = 2
RIGHT = 3
HEAD = 0
DIRECTION = [DOWN, UP, LEFT, RIGHT]
OPP = [UP, DOWN, RIGHT, LEFT]
MOVE = [(0, -1), (0, 1), (-1, 0), (1, 0)]
dis = [] 
STA_FILE = "d:/codes/bfsplaystatus.txt"
DIR_FILE = "d:/codes/bfsplaydirections.txt"
FOOD_FILE = "d:/codes/food_list.txt"

class ca(object):
    def __init__(self, CELLWIDTH, CELLHEIGHT):
        self.CELLHEIGHT = CELLHEIGHT
        self.CELLWIDTH = CELLWIDTH
        self.count = 0
        self.epoch = 0
        self.episode = 0
        self.loops = 0
        self.time_cnt_bfs = 0
        self.time_cnt_dj = 0

    def init_dis(self):
        for x in range(self.CELLHEIGHT + 2):
            dis.append([])
            for y in range(self.CELLWIDTH + 2):
                dis[x].append(inf)

    def check_range(self, x, y):
        return x >= 0 and x < self.CELLWIDTH and y >= 0 and y < self.CELLHEIGHT
    
    def check_pt(self, grid, frontier, food):
        x = grid[0]
        y = grid[1]
        if (x, y) == (food['x'], food['y']):
            return False
        elif not self.check_range(x, y):
            return False
        elif grid in frontier:
            return False
        else:
            return True

    #can_move further
    def can_move(self, x, y, snake):
        if x < 0 or x >= self.CELLWIDTH:
            return False
        elif y < 0 or y >= self.CELLHEIGHT:
            return False
        elif self.is_snake(x, y,snake):
            return False
        elif (x, y) == (snake[HEAD]['x'], snake[HEAD]['y']):
            return False
        else:
            return True

    #is snake body
    def is_snake(self, x, y, snake):
        for body in snake:
            if body['x'] == x and body['y'] == y:
                return True
        return False

    def caldis_dijkstra(self,snake,food):
        self.loops += 1
        time_before = time.time()
        self.init_dis()
        found = False
        for x in range(self.CELLHEIGHT):
            for y in range(self.CELLWIDTH):
                dis[x][y] = inf
        vis = []
        dis[food['x']][food['y']] = 0
        for i in range(self.CELLHEIGHT * self.CELLWIDTH):
            minn = inf
            minnpos = (-1, -1)
            for j in range(self.CELLWIDTH * self.CELLHEIGHT):
                x = j // self.CELLHEIGHT
                y = j % self.CELLWIDTH
                if (x, y) not in vis and dis[x][y] < minn:
                    minn = dis[x][y]
                    minnpos = (x, y)
            if minnpos == (-1, -1):
                break;
            vis.append((minnpos[0], minnpos[1]))
            for j in range(4):
                xx = minnpos[0] + MOVE[j][0]
                yy = minnpos[1] + MOVE[j][1]
                if (xx, yy) == (snake[HEAD]['x'], snake[HEAD]['y']):
                    found = True
                if self.check_range(xx, yy):
                    if self.is_snake(xx, yy, snake) == False and dis[xx][yy] > dis[minnpos[0]][minnpos[1]] + 1:
                        dis[xx][yy] = dis[minnpos[0]][minnpos[1]] + 1
        time_after = time.time()
        self.time_cnt_dj += time_after - time_before
        return found

    def cal_dis(self,snake,food): 
        #SPFA
        self.loops += 1
        time_before = time.time()
        self.init_dis()
        frontier = [(food['x'], food['y'])]
        found = False
        for x in range(self.CELLHEIGHT):
            for y in range(self.CELLWIDTH):
                dis[x][y] = inf
        dis[food['x']][food['y']] = 0
        while len(frontier) != 0:
            head = frontier[0]
            frontier.pop(0)
            for i in range(4):
                grid = (head[0] + MOVE[i][0], head[1] + MOVE[i][1])
                if self.check_pt(grid, frontier, food):
                    if grid[0] == snake[HEAD]['x'] and grid[1] == snake[HEAD]['y']:
                        found = True
                    if not self.is_snake(grid[0], grid[1], snake) and dis[grid[0]][grid[1]] > dis[head[0]][head[1]] + 1:
                        frontier.append(grid)
                        dis[grid[0]][grid[1]] = dis[head[0]][head[1]] + 1
        time_after = time.time()
        self.time_cnt_bfs += time_after - time_before
        return found

    #update the position
    def update_loc(self, now, direc):
        loc = {'x' : 0,'y' : 0}
        for i in range(4):
            if direc == DIRECTION[i]:
                loc = {'x': now['x'] + MOVE[i][0], 'y': now['y'] + MOVE[i][1]}
        return loc

    #virtual run
    def vRun(self, snake_coords, food, direction):
        snake_coords = list(snake_coords)
        food_eated = False
        #make virtual MOVE
        while not food_eated: 
            self.cal_dis(snake_coords,food)   
            dis_dir = [inf] * 4
            # distance of 4 directions
            for i in range(4):
                # down up left right
                pos_x = snake_coords[HEAD]['x'] + MOVE[i][0]
                pos_y = snake_coords[HEAD]['y'] + MOVE[i][1]
                if self.can_move(pos_x, pos_y, snake_coords):
                    dis_dir[i] = dis[pos_x][pos_y]

            min_num = min(dis_dir)
            #choose direction for each move
            for i in range(4):
                pos_x = snake_coords[HEAD]['x'] + MOVE[i][0]
                pos_y = snake_coords[HEAD]['y'] + MOVE[i][1]
                if dis_dir[i] < inf and dis[pos_x][pos_y] == min_num and direction != OPP[i]:
                    direction = DIRECTION[i]
            #over
            #print(direction)
            pos_x = snake_coords[HEAD]['x']
            pos_y = snake_coords[HEAD]['y']
            if pos_x == -1 or pos_x == self.CELLWIDTH or pos_y == -1 or pos_y == self.CELLHEIGHT:
                return
            for body in snake_coords[1:]:
                if body['x'] == pos_x and body['y'] == pos_y:
                    return
            # make move
            for i in range(4):
                if direction == DIRECTION[i]:
                    new_head = {'x': pos_x + MOVE[i][0], 'y': pos_y + MOVE[i][1]}
                    #eaten
                    if new_head['x'] == food['x'] or new_head['y'] == food['y']:
                        food_eated = True
                        snake_coords.insert(0, new_head)
                    else:
                        del snake_coords[-1] # remove snake's tail segment
                        snake_coords.insert(0, new_head)
        #compare and select direction
        result = self.cal_dis(snake_coords, snake_coords[-1])
        for i in range(4):
            temp = self.update_loc(snake_coords[HEAD],DIRECTION[i])
            if temp['x'] == snake_coords[-1]['x'] and temp['y'] == snake_coords[-1]['y']:
                result = False
        #print("vrun_result", result)
        return result

    #random move

    def ca_operation(self, snake_coords,food,direction):
        #count = 0
        self.epoch += 1
        new_dir = None
        if self.cal_dis(snake_coords,food):
            if self.vRun(snake_coords, food, direction):
                self.cal_dis(snake_coords,food)
                dis_dir = [inf] * 4
                for i in range(4):
                # down up left right
                    pos_x = snake_coords[HEAD]['x'] + MOVE[i][0]
                    pos_y = snake_coords[HEAD]['y'] + MOVE[i][1]
                    if self.can_move(pos_x, pos_y, snake_coords):
                        dis_dir[i] = dis[pos_x][pos_y]

                min_num = min(dis_dir)
                #choose direction for each move
                for i in range(4):
                    pos_x = snake_coords[HEAD]['x'] + MOVE[i][0]
                    pos_y = snake_coords[HEAD]['y'] + MOVE[i][1]
                    if dis_dir[i] < inf and dis[pos_x][pos_y] == min_num and direction != OPP[i]:
                       new_dir = DIRECTION[i]
            else:
                self.count += 1
                dis_dir = [-1] * 4
                #print("SNAKE",snake_coords)
                self.cal_dis(snake_coords, snake_coords[-1])
                for i in range(4):
                # down up left right
                    pos_x = snake_coords[HEAD]['x'] + MOVE[i][0]
                    pos_y = snake_coords[HEAD]['y'] + MOVE[i][1]
                    if self.can_move(pos_x, pos_y, snake_coords):
                        dis_dir[i] = dis[pos_x][pos_y]

                max_num = 0
                for i in dis_dir:
                    if i != inf:
                        if i > max_num:
                            max_num = i

                for i in range(4):
                    pos_x = snake_coords[HEAD]['x'] + MOVE[i][0]
                    pos_y = snake_coords[HEAD]['y'] + MOVE[i][1]
                    if dis_dir[i] > -1 and dis[pos_x][pos_y] == max_num and direction != OPP[i]:
                        new_dir = DIRECTION[i]
                if self.count % 5 == 0 and self.count % 20 != 0 and new_dir == None:
                    new_dir = self.random_move(snake_coords, food, direction)
                elif self.count % 20 == 0:
                    print("suicide! Completely random move.")
                    new_dir = random.randint(0,3)

        else: 
            dis_dir = [-1] * 4
            self.cal_dis(snake_coords, snake_coords[-1])
            for i in range(4):
                    # down up left right
                    pos_x = snake_coords[HEAD]['x'] + MOVE[i][0]
                    pos_y = snake_coords[HEAD]['y'] + MOVE[i][1]
                    if self.can_move(pos_x, pos_y, snake_coords):
                        dis_dir[i] = dis[pos_x][pos_y]

            max_num = 0
            for i in dis_dir:
                if i != inf:
                    if i > max_num:
                        max_num = i

            for i in range(4):
                pos_x = snake_coords[HEAD]['x'] + MOVE[i][0]
                pos_y = snake_coords[HEAD]['y'] + MOVE[i][1]
                if dis_dir[i] > -1 and dis[pos_x][pos_y] == max_num and direction != OPP[i]:
                    new_dir = DIRECTION[i]

        if new_dir == None:
            direction = self.random_move(snake_coords, food, direction)
            return direction

        else:
            direction = new_dir
            return direction

    def random_move(self, snake, food, direction):
        tempdir = direction
        mindis = inf
        used = [0] * 4
        cnt = 0
        while True:
            cnt  = 0
            for i in range(4):
                cnt += used[i]
            if cnt == 4:
                return None
            while True:
                i = random.randint(0, 3)
                if used[i] == 0:
                    break
            used[i] = 1
            temp = self.update_loc(snake[0], DIRECTION[i])
            if  self.can_move(temp['x'],temp['y'],snake) and (self.check_dir(DIRECTION[i], direction)):
                    tempdir = DIRECTION[i]
                    break
        return tempdir

    #check direction conflict
    def check_dir(self, temp , direction):
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

class agent:
    def run(self):
        sp_agent = ca(game.CELLWIDTH, game.CELLHEIGHT)
        bfs_game = game.game_state()
        episode = 0
        sp_agent.epoch = 0
        average_move = 0
        while True:
            direction = sp_agent.ca_operation(bfs_game.snake_coords, bfs_game.food, bfs_game.direction)
            action  = np.zeros(4)
            action[direction] = 1
            sp_agent.epoch += 1
            _, _, done = bfs_game.frame_step(action)
            if done == True:
                sp_agent.episode += 1 
                score, episode = bfs_game.ret_score()
                print(score)
                sp_agent.epoch = 0

def main():
    run_agent = agent()
    run_agent.run()

if __name__ == '__main__':
    main()