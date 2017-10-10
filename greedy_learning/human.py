import math

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3
HEAD = 0

def human_operation(direction, snakeCoords, pressed, CELLWIDTH, CELLHEIGHT):
    if pressed in range(4):
        direction = pressed
    print("the key pressed:", pressed)
    if snakeCoords[HEAD]['x'] == -1 or snakeCoords[HEAD]['x'] == CELLWIDTH or snakeCoords[HEAD]['y'] == -1 or snakeCoords[HEAD]['y'] == CELLHEIGHT:
        print("died for touching the border", direction)
        return -1
    for snakeBody in snakeCoords[1:]:
        print(snakeBody['x'],snakeBody['y'])
        if snakeBody['x'] == snakeCoords[HEAD]['x'] and snakeBody['y'] == snakeCoords[HEAD]['y']:
            print("died for touching the snake itself", direction)
            return -1
    return direction


