import pygame
import numpy as np
import sys

factor = 50  # grid size (pixels)
length = 15  # how many grids in this table
chess_radius = 20  # in pixels
win_status = False


def table2grid(x, y):
    return factor * (x + 1), factor * (y + 1)


class Table:
    def __init__(self, length):
        self.length = length
        self.table = np.zeros((self.length, self.length), dtype=np.int8)
        self.steps = []
        self.next_chess = 1  # only 1 or -1. 1 for black, and -1 for white
    
    def occupy(self, x, y):
        """Occupy a place in the table. `b_or_w` is used to specify whether this chess is black or white."""
        if self.table[x, y] != 0:
            return
        self.table[x, y] = self.next_chess
        self.steps.append([x, y])
        self.next_chess = -self.next_chess  # change the black/white
    
    def _in_table(self, x, y):
        """Helper function. check if this coordinate is in the table."""
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
        # explore horizontally
        x0, y0 = self._explore_one_direction(x, y, lambda x, y: (x-1, y))
        x1, y1 = self._explore_one_direction(x, y, lambda x, y: (x+1, y))
        if x1 - x0 > 5:
            return True
        # explore vertically
        x0, y0 = self._explore_one_direction(x, y, lambda x, y: (x, y-1))
        x1, y1 = self._explore_one_direction(x, y, lambda x, y: (x, y+1))
        if y1 - y0 > 5:
            return True
        # explore in y=x direction
        x0, y0 = self._explore_one_direction(x, y, lambda x, y: (x-1, y-1))
        x1, y1 = self._explore_one_direction(x, y, lambda x, y: (x+1, y+1))
        if x1 - x0 > 5:
            return True
        # explore in y=-x direction
        x0, y0 = self._explore_one_direction(x, y, lambda x, y: (x-1, y+1))
        x1, y1 = self._explore_one_direction(x, y, lambda x, y: (x+1, y-1))
        if x1 - x0 > 5:
            return True
        return False
    
    def reverse(self):
        if len(self.steps) == 0:
            return
        x, y = self.steps.pop(-1)
        self.table[x, y] = 0
        self.next_chess = -self.next_chess


class Drawer:
    def __init__(self, table: Table, screen):
        # init screen
        self.screen = screen
        # table
        self.table = table
        # the coordinates of the chess
        self.grid = np.zeros((*self.table.table.shape, 2), dtype=np.uint32)
        for x in range(length):
            for y in range(length):
                self.grid[x, y] = table2grid(x, y)
        self.flatten_grid = self.grid.reshape(-1, 2)
    
    def draw_grid(self):
        for i in range(factor, (length + 1) * factor, factor):
            pygame.draw.line(self.screen, (255, 255, 255), (factor, i), (length * factor, i))
        for i in range(factor, (length + 1) * factor, factor):
            pygame.draw.line(self.screen, (255, 255, 255), (i, factor), (i, length * factor))
    
    def draw_chess(self):
        for x in range(length):
            for y in range(length):
                color = self.table.table[x, y]
                if color == 0:
                    continue
                elif color == 1:
                    color = (0, 0, 0)
                else:
                    color = (255, 255, 255)
                center = self.grid[x, y]
                pygame.draw.circle(self.screen, color, center, chess_radius)
    
    def get_closest_point(self, mouse_pos):
        point = np.argmin(np.sum(np.abs(self.flatten_grid - mouse_pos), axis=1))
        x, y = point // length, point % length
        return x, y
    
    def draw_mouse(self, mouse_pos):
        pygame.draw.circle(self.screen, (127, 127, 127), mouse_pos, chess_radius // 3)
    
    def draw_temp_chess(self, mouse_pos):
        """draw the `temporary chess` that the mouse hovered on, for better visual experience"""
        x, y = self.get_closest_point(mouse_pos)
        pos = table2grid(x, y)
        if win_status == True:
            color = (255, 192, 192)
        elif self.table.next_chess == 1:
            color = (64, 64, 64)
        else:
            color = (192, 192, 192)
        pygame.draw.circle(self.screen, color, pos, chess_radius, 4)


class Controller:
    def __init__(self, table, drawer, screen):
        self.table = table
        self.drawer = drawer
        self.screen = screen
        self.clock = pygame.time.Clock()
        pygame.mouse.set_visible(False)
        self.mouse_pos = pygame.mouse.get_pos()
    
    def occupy(self):
        x, y = self.drawer.get_closest_point(self.mouse_pos)
        self.table.occupy(x, y)
        win_status = table.check_if_win(*self.drawer.get_closest_point(self.mouse_pos))
        if win_status:
            print("game over")
    
    def move(self, dx, dy):
        x, y = self.drawer.get_closest_point(self.mouse_pos)
        x += dx
        y += dy
        pos = table2grid(x, y)
        pygame.mouse.set_pos(pos)
        self.mouse_pos = pos

    def main_loop(self):
        """The game mainly occurs in this fucntion"""
        while True:
            need_draw = False
            for event in pygame.event.get():
                need_draw = True
                if event.type == pygame.MOUSEMOTION:
                    self.mouse_pos = pygame.mouse.get_pos()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.occupy()
                elif event.type == pygame.QUIT:
                    pygame.display.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.move(0, -1)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.move(0, 1)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.move(-1, 0)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.move(1, 0)
                    elif event.key == pygame.K_RETURN:
                        self.occupy()
                    elif event.key == pygame.K_BACKSPACE:
                        self.table.reverse()
            if need_draw:
                self.screen.fill((224, 176, 92))
                self.drawer.draw_grid()
                self.drawer.draw_chess()
                self.drawer.draw_temp_chess(self.mouse_pos)
                self.drawer.draw_mouse(self.mouse_pos)
                pygame.display.flip()
            self.clock.tick(240)


if __name__ == '__main__':
    pygame.display.init()
    screen_length = (length + 1) * factor
    screen = pygame.display.set_mode((screen_length, screen_length))
    table = Table(length)
    drawer = Drawer(table, screen)
    controller = Controller(table, drawer, screen)
    controller.main_loop()
