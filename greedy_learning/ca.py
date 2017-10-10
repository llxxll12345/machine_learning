import random, pygame,sys


inf = 10000
UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3
HEAD = 0
DIRECTION = [UP,DOWN,LEFT,RIGHT]
dis = [] 

class ca(object):
    def __init__(self, CELLWIDTH, CELLHEIGHT):
        self.CELLHEIGHT = CELLHEIGHT
        self.CELLWIDTH = CELLWIDTH
        self.count = 0

    def init_dis(self):
        for y in range(self.CELLHEIGHT + 2):
            dis.append([])
            for x in range(self.CELLWIDTH + 2):
                dis[y].append(inf)
    #check for bfs
    def check(self,gd, queue, visited, snake, food):
        x = gd[0]
        y = gd[1]
        if (x, y) == (food['x'],food['y']):
            return False
        elif x < 0 or x >= self.CELLWIDTH or y < 0 or y >= self.CELLHEIGHT:
            return False
        elif (x, y) in queue or (x, y) in visited:
            return False
        else:
            return True

    #canmove further
    def canmove(self, x, y, snake):
        if x < 0 or x >= self.CELLWIDTH:
            return False
        elif y < 0 or y >= self.CELLHEIGHT:
            return False
        elif self.isSnake(x, y,snake):
            return False
        elif (x, y) == (snake[HEAD]['x'], snake[HEAD]['y']):
            return False
        else:
            return True

    #isSnakebody
    def isSnake(self, x, y, snake):
        for body in snake:
            if body['x'] == x and body['y'] == y:
                return True
        return False

    #bfs
    def caldis(self,snake,food):
        self.init_dis()
        queue = [(food['x'], food['y'])]
        visited = []
        found = False
        for y in range(self.CELLHEIGHT):
            for x in range(self.CELLWIDTH):
                dis[y][x] = inf

        dis[food['y']][food['x']] = 0

        while len(queue) != 0:
            head = queue[0]
            visited.append(head)
            up_grid = head[0], head[1] - 1
            down_grid = head[0], head[1] + 1
            left_grid = head[0] - 1, head[1]
            right_grid = head[0] + 1, head[1]

            for grid in [up_grid, down_grid, left_grid, right_grid]:
                if self.check(grid, queue, visited, snake, food):
                    if grid[0] == snake[HEAD]['x'] and grid[1] == snake[HEAD]['y']:
                        found = True
                    if not self.isSnake(grid[0], grid[1], snake):
                        queue.append(grid)
                        dis[grid[1]][grid[0]] = dis[head[1]][head[0]] + 1
            queue.pop(0)
        return found

    #return the next direction
    def dirCheck(self, now, direc):
        loc = {'x':0,'y':0}
        if direc == UP:
            loc = {'x':now['x'],'y':now['y'] - 1}
        elif direc == DOWN:
            loc = {'x':now['x'],'y':now['y'] + 1}
        elif direc == RIGHT:
            loc = {'x':now['x'] + 1,'y':now['y']}
        elif direc == LEFT:
            loc = {'x':now['x'] - 1,'y':now['y']}
        return loc

    #calculate distance between two points
    def fdis(self, x,y):
        return abs(x['x']-y['x']) + abs(x['y'] - x['y'])

    #virtual run
    def vRun(self, snakeCoords, food,direction):
        snakeCoords = list(snakeCoords)
        food_eated = False
        #make virtual moves
        while not food_eated:
            self.caldis(snakeCoords,food)
            disDir = [inf] * 4
            # distance of 4 directions
            if self.canmove(snakeCoords[HEAD]['x'], snakeCoords[HEAD]['y'] - 1, snakeCoords):
                disDir[0] = dis[snakeCoords[HEAD]['y'] - 1][snakeCoords[HEAD]['x']]
            if self.canmove(snakeCoords[HEAD]['x'] + 1, snakeCoords[HEAD]['y'], snakeCoords):
                disDir[1] = dis[snakeCoords[HEAD]['y']][snakeCoords[HEAD]['x'] + 1]
            if self.canmove(snakeCoords[HEAD]['x'], snakeCoords[HEAD]['y'] + 1, snakeCoords):
                disDir[2] = dis[snakeCoords[HEAD]['y'] + 1][snakeCoords[HEAD]['x']]
            if self.canmove(snakeCoords[HEAD]['x'] - 1, snakeCoords[HEAD]['y'], snakeCoords):
                disDir[3] = dis[snakeCoords[HEAD]['y']][snakeCoords[HEAD]['x'] - 1]

            minNum = min(disDir)
            #choose direction for each move
            if disDir[0] < inf and dis[snakeCoords[HEAD]['y'] - 1][snakeCoords[HEAD]['x']] == minNum and direction != DOWN:
                direction = UP
            elif disDir[1] < inf and dis[snakeCoords[HEAD]['y']][snakeCoords[HEAD]['x'] + 1] == minNum and direction != LEFT:
                direction = RIGHT
            elif disDir[2] < inf and dis[snakeCoords[HEAD]['y'] + 1][snakeCoords[HEAD]['x']] == minNum and direction != UP:
                direction = DOWN
            elif disDir[3] < inf and dis[snakeCoords[HEAD]['y']][snakeCoords[HEAD]['x'] - 1] == minNum and direction != RIGHT:
                direction = LEFT
            #over
            if snakeCoords[HEAD]['x'] == -1 or snakeCoords[HEAD]['x'] == self.CELLWIDTH or snakeCoords[HEAD]['y'] == -1 or snakeCoords[HEAD]['y'] == self.CELLHEIGHT:
                return
            for snakeBody in snakeCoords[1:]:
                if snakeBody['x'] == snakeCoords[HEAD]['x'] and snakeBody['y'] == snakeCoords[HEAD]['y']:
                    return
            # make move
            if direction == UP:
                newHead = {'x': snakeCoords[HEAD]['x'], 'y': snakeCoords[HEAD]['y'] - 1}
            elif direction == DOWN:
                newHead = {'x': snakeCoords[HEAD]['x'], 'y': snakeCoords[HEAD]['y'] + 1}
            elif direction == LEFT:
                newHead = {'x': snakeCoords[HEAD]['x'] - 1, 'y': snakeCoords[HEAD]['y']}
            elif direction == RIGHT:
                newHead = {'x': snakeCoords[HEAD]['x'] + 1, 'y': snakeCoords[HEAD]['y']}
            #eaten
            if snakeCoords[HEAD]['x'] != food['x'] or snakeCoords[HEAD]['y'] != food['y']:
                food_eated = True
                snakeCoords.insert(0, newHead)
            else:
                del snakeCoords[-1] # remove snake's tail segment
                snakeCoords.insert(0, newHead)
        #compare and select direction
        result = self.caldis(snakeCoords, snakeCoords[-1])
        for i in range(4):
            temp = self.dirCheck(snakeCoords[HEAD],DIRECTION[i])
            if temp['x'] == snakeCoords[-1]['x'] and temp['y'] == snakeCoords[-1]['y']:
                result = False
        return result

    #random move

    def ca_operation(self, snakeCoords,food,direction):
        #count = 0
        newDir = None
        if self.caldis(snakeCoords,food):
            if self.vRun(snakeCoords, food, direction):
                # there is a possible way => make a move
                self.caldis(snakeCoords,food)
                disdir = [inf] * 4
                if self.canmove(snakeCoords[HEAD]['x'], snakeCoords[HEAD]['y'] - 1, snakeCoords):
                    disdir[0] = dis[snakeCoords[HEAD]['y'] - 1][snakeCoords[HEAD]['x']]
                if self.canmove(snakeCoords[HEAD]['x'] + 1, snakeCoords[HEAD]['y'], snakeCoords):
                    disdir[1] = dis[snakeCoords[HEAD]['y']][snakeCoords[HEAD]['x'] + 1]
                if self.canmove(snakeCoords[HEAD]['x'], snakeCoords[HEAD]['y'] + 1, snakeCoords):
                    disdir[2] = dis[snakeCoords[HEAD]['y'] + 1][snakeCoords[HEAD]['x']]
                if self.canmove(snakeCoords[HEAD]['x'] - 1, snakeCoords[HEAD]['y'], snakeCoords):
                    disdir[3] = dis[snakeCoords[HEAD]['y']][snakeCoords[HEAD]['x'] - 1]

                maxNum = min(disdir)

                if disdir[0] < inf and dis[snakeCoords[HEAD]['y'] - 1][snakeCoords[HEAD]['x']] == maxNum and direction != DOWN:
                    newDir = UP
                elif disdir[1] < inf and dis[snakeCoords[HEAD]['y']][snakeCoords[HEAD]['x'] + 1] == maxNum and direction != LEFT:
                    newDir = RIGHT
                elif disdir[2] < inf and dis[snakeCoords[HEAD]['y'] + 1][snakeCoords[HEAD]['x']] == maxNum and direction != UP:
                    newDir = DOWN
                elif disdir[3] < inf and dis[snakeCoords[HEAD]['y']][snakeCoords[HEAD]['x'] - 1] == maxNum and direction != RIGHT:
                    newDir = LEFT

                #print("a possible road", newDir)
            else:
                self.count += 1
                disdir = [-1] * 4
                self.caldis(snakeCoords, snakeCoords[-1])
                if self.canmove(snakeCoords[HEAD]['x'], snakeCoords[HEAD]['y'] - 1, snakeCoords):
                    disdir[0] = dis[snakeCoords[HEAD]['y'] - 1][snakeCoords[HEAD]['x']]
                if self.canmove(snakeCoords[HEAD]['x'] + 1, snakeCoords[HEAD]['y'], snakeCoords):
                    disdir[1] = dis[snakeCoords[HEAD]['y']][snakeCoords[HEAD]['x'] + 1]
                if self.canmove(snakeCoords[HEAD]['x'], snakeCoords[HEAD]['y'] + 1, snakeCoords):
                    disdir[2] = dis[snakeCoords[HEAD]['y'] + 1][snakeCoords[HEAD]['x']]
                if self.canmove(snakeCoords[HEAD]['x'] - 1, snakeCoords[HEAD]['y'], snakeCoords):
                    disdir[3] = dis[snakeCoords[HEAD]['y']][snakeCoords[HEAD]['x'] - 1]
                maxNum = 0
                for i in disdir:
                    if i != inf:
                        if i > maxNum:
                            maxNum = i

                if disdir[0] > -1 and dis[snakeCoords[HEAD]['y'] - 1][snakeCoords[HEAD]['x']] == maxNum and direction != DOWN:
                    newDir = UP
                elif disdir[1] > -1 and dis[snakeCoords[HEAD]['y']][snakeCoords[HEAD]['x'] + 1] == maxNum and direction != LEFT:
                    newDir = RIGHT
                elif disdir[2] > -1 and dis[snakeCoords[HEAD]['y'] + 1][snakeCoords[HEAD]['x']] == maxNum and direction != UP:
                    newDir = DOWN
                elif disdir[3] > -1 and dis[snakeCoords[HEAD]['y']][snakeCoords[HEAD]['x'] - 1] == maxNum and direction != RIGHT:
                    newDir = LEFT
                if self.count % 5 != 0:
                    print("count: ", self.count)
                    #print("longest way",newDir)
                elif self.count % 5 == 0 and self.count % 20 != 0 and newDir == None:
                    #print("rand1")
                    newDir = self.randomMove(snakeCoords, food, direction)
                    #print("randomway", newDir)
                elif self.count % 20 == 0:
                    print("suicide!")
                    newDir = 2
                    
        else:
            disdir = [-1] * 4
            self.caldis(snakeCoords, snakeCoords[-1])
            if self.canmove(snakeCoords[HEAD]['x'], snakeCoords[HEAD]['y'] - 1, snakeCoords):
                disdir[0] = dis[snakeCoords[HEAD]['y'] - 1][snakeCoords[HEAD]['x']]
            if self.canmove(snakeCoords[HEAD]['x'] + 1, snakeCoords[HEAD]['y'], snakeCoords):
                disdir[1] = dis[snakeCoords[HEAD]['y']][snakeCoords[HEAD]['x'] + 1]
            if self.canmove(snakeCoords[HEAD]['x'], snakeCoords[HEAD]['y'] + 1, snakeCoords):
                disdir[2] = dis[snakeCoords[HEAD]['y'] + 1][snakeCoords[HEAD]['x']]
            if self.canmove(snakeCoords[HEAD]['x'] - 1, snakeCoords[HEAD]['y'], snakeCoords):
                disdir[3] = dis[snakeCoords[HEAD]['y']][snakeCoords[HEAD]['x'] - 1]

            maxNum = 0
            for i in disdir:
                if i != inf:
                    if i > maxNum:
                        maxNum = i

            if disdir[0] > -1 and dis[snakeCoords[HEAD]['y'] - 1][snakeCoords[HEAD]['x']] == maxNum and direction != DOWN:
                newDir = UP
            elif disdir[1] > -1 and dis[snakeCoords[HEAD]['y']][snakeCoords[HEAD]['x'] + 1] == maxNum and direction != LEFT:
                newDir = RIGHT
            elif disdir[2] > -1 and dis[snakeCoords[HEAD]['y'] + 1][snakeCoords[HEAD]['x']] == maxNum and direction != UP:
                newDir = DOWN
            elif disdir[3] > -1 and dis[snakeCoords[HEAD]['y']][snakeCoords[HEAD]['x'] - 1] == maxNum and direction != RIGHT:
                newDir = LEFT
        if newDir == None:
            #print("rand2")
            direction = self.randomMove(snakeCoords, food, direction)
            #print("fianl rand",direction)
            return direction

        else:
            direction = newDir
            #print(("final",direction))
            return direction

        if snakeCoords[HEAD]['x'] == -1 or snakeCoords[HEAD]['x'] ==self.CELLWIDTH or snakeCoords[HEAD]['y'] == -1 or snakeCoords[HEAD]['y'] == self.CELLHEIGHT:
            print("died for touching the border", direction)
            return -1
        for snakeBody in snakeCoords[1:]:
            print(snakeBody['x'],snakeBody['y'])
            if snakeBody['x'] == snakeCoords[HEAD]['x'] and snakeBody['y'] == snakeCoords[HEAD]['y']:
                print("died for touching the snake itself", direction)
                return -1

    def randomMove(self, snake,food,direction):
        tempdir = direction
        mindis = inf
        used = [0] * 4
        cnt = 0
        loop = 0
        while True:
            loop += 1
            print(loop)
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
            temp = self.dirCheck(snake[0], DIRECTION[i])
            if  self.canmove(temp['x'],temp['y'],snake) and (self.checkDir(DIRECTION[i], direction)):
                    tempdir = DIRECTION[i]
                    break
        return tempdir

    #check direction conflict
    def checkDir(self, temp , direction):
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

    #check if head movement is possible
    def checkHead(self, snake,direction):
        for i in range(4):
            temp = self.dirCheck(snake[HEAD], DIRECTION[i])
            if self.canmove(temp['x'],temp['y'],snake) and self.checkDir(DIRECTION[i],direction):
                if dis[temp['y']][temp['x']] < inf:
                    return True
        return False