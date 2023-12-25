import pygame
import numpy as np
import sys

factor = 50
length = 15
chess_radius = 20
next_chess = "b"
win_status = False

class Table:
    def __init__(self, length):
        self.length = length
        self.table = np.zeros((self.length, self.length), dtype=np.int8)
    
    def occupy(self, x, y, b_or_w):
        """Occupy a place in the table. `b_or_w` is used to specify whether this chess is black or white."""
        if b_or_w == "b":
            chess = 1
        elif b_or_w == "w":
            chess = -1
        else:
            assert False
        self.table[x, y] = chess
    
    def _in_table(self, x, y):
        """Helper function. check if this chess is in the table."""
        return 0 <= x < self.length and 0 <= y < self.length
    
    def _explore_one_direction(self, x, y, change_func):
        """Helper function. Explore the chess table in one direction (horizontal, vertical, or slanted).
        Return the nearest coordinate in this direction which is not valid (has different b_or_w type or out of table).
        `chenge_func` is called to find the next coordinate."""
        b_or_w = self.table[x, y]
        while self._in_table(x, y):
            if self.table[x, y] != b_or_w:
                return x, y
            x, y = change_func(x, y)
        return x, y
    
    def check_if_win(self, x, y):
        """x and y are the coordinate of the newest chess's position. Check if there is a `five` around this chess."""
        x0, y0 = self._explore_one_direction(x, y, lambda x, y: (x-1, y))
        x1, y1 = self._explore_one_direction(x, y, lambda x, y: (x+1, y))
        if x1 - x0 > 5:
            return True
        x0, y0 = self._explore_one_direction(x, y, lambda x, y: (x, y-1))
        x1, y1 = self._explore_one_direction(x, y, lambda x, y: (x, y+1))
        if y1 - y0 > 5:
            return True
        x0, y0 = self._explore_one_direction(x, y, lambda x, y: (x-1, y-1))
        x1, y1 = self._explore_one_direction(x, y, lambda x, y: (x+1, y+1))
        if x1 - x0 > 5:
            return True
        x0, y0 = self._explore_one_direction(x, y, lambda x, y: (x-1, y+1))
        x1, y1 = self._explore_one_direction(x, y, lambda x, y: (x+1, y-1))
        if x1 - x0 > 5:
            return True
        return False


def table2grid(x, y):
    return factor * (x + 1), factor * (y + 1)


points = np.array([[x, y] for y in range(length) for x in range(length)]) * factor + factor
def get_closest_point():
    pos = pygame.mouse.get_pos()
    point = np.argmin(np.sum(np.abs(points - pos), axis=1))
    y, x = point // length, point % length
    return x, y


def draw_grid():
    for i in range(factor, (length + 1) * factor, factor):
        pygame.draw.line(screen, (255, 255, 255), (factor, i), (length * factor, i))
    for i in range(factor, (length + 1) * factor, factor):
        pygame.draw.line(screen, (255, 255, 255), (i, factor), (i, length * factor))


def draw_chess():
    for i in range(length):
        for j in range(length):
            value = table.table[i, j]
            if value == 0:
                continue
            if value == 1:
                color = (0, 0, 0)
            elif value == -1:
                color = (255, 255, 255)
            pygame.draw.circle(screen, color, table2grid(i, j), chess_radius)


def draw_temp_chess():
    x, y = get_closest_point()
    x, y = table2grid(x, y)
    if win_status == True:
        color = (255, 192, 192)
    elif next_chess == "b":
        color = (64, 64, 64)
    else:
        color = (192, 192, 192)
    pygame.draw.circle(screen, color, (x, y), chess_radius)


def occupy():
    global next_chess
    x, y = get_closest_point()
    if table.table[x, y] != 0:
        return
    table.occupy(x, y, next_chess)
    # toggle b_or_w
    if next_chess == "b":
        next_chess = "w"
    else:
        next_chess = "b"
    chess_steps.append([x, y])


def reverse():
    global next_chess
    x, y = chess_steps.pop(-1)
    table.table[x, y] = 0
    if next_chess == "b":
        next_chess = "w"
    else:
        next_chess = "b"


if __name__ == '__main__':
    pygame.display.init()
    table = Table(length)
    screen_length = (length + 1) * factor
    screen = pygame.display.set_mode((screen_length, screen_length))
    clock = pygame.time.Clock()
    chess_steps = []
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                occupy()
                win_status = table.check_if_win(*get_closest_point())
                if win_status:
                    print("game over")
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    reverse()
                    
        get_closest_point()
        screen.fill((230, 172, 67))
        draw_grid()
        draw_temp_chess()
        draw_chess()
        pygame.display.flip()
        clock.tick(60)
