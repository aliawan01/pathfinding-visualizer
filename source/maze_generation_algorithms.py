import pygame
from pygame.locals import *
import random

from stack import Stack
from queue_classes import Queue, PriorityQueue

class MazeGenerationAlgorithm:
    def __init__(self, screen, rect_array_obj, num_of_rows, num_of_columns):
        self.screen = screen
        self.num_of_columns = num_of_columns
        self.num_of_rows = num_of_rows
        self.rect_array_obj = rect_array_obj
        self.rect_array = self.rect_array_obj.array
        self.maze = Stack(self.num_of_rows*self.num_of_columns)
        self.maze_pointer = -1

    def reset_maze_pointer(self):
        self.maze_pointer = -1

    def update_maze_pointer(self):
        if self.maze_pointer != self.maze.get_size():
            self.maze_pointer += 1
            return 0
        else:
            return -1

    def draw(self, marked_node_color):
        for x in range(self.maze_pointer):
            coord = self.maze.stack[x]
            pygame.draw.rect(self.screen, marked_node_color, self.rect_array[coord[0]][coord[1]]) 


class RandomWeightedMaze(MazeGenerationAlgorithm):
    def __init__(self, screen, rect_array_obj, num_of_rows, num_of_columns):
        super().__init__(screen, rect_array_obj, num_of_rows, num_of_columns)

    def create_random_weighted_maze(self):
        for y in range(self.num_of_rows):
            for x in range(self.num_of_columns):
                weight = random.randint(1, 100)
                should_be_weighted_node = random.choice([0, 0, 1, 0])
                if should_be_weighted_node:
                    self.rect_array[y][x].is_user_weight = True
                    self.rect_array[y][x].weight = weight

class RandomMarkedMaze(MazeGenerationAlgorithm):
    def __init__(self, screen, rect_array_obj, num_of_rows, num_of_columns):
        super().__init__(screen, rect_array_obj, num_of_rows, num_of_columns)

    def create_random_marked_maze(self):
        self.maze = Stack(self.num_of_rows*self.num_of_columns)

        for y in range(self.num_of_rows):
            for x in range(self.num_of_columns):
                should_be_marked = random.choice([0, 0, 1, 0])
                if should_be_marked:
                    self.rect_array[y][x].marked = True
                    self.maze.push([y, x])


class RecursiveDivisionMaze(MazeGenerationAlgorithm):
    def __init__(self, screen, rect_array_obj, num_of_rows, num_of_columns):
        super().__init__(screen, rect_array_obj, num_of_rows, num_of_columns)
        self.empty_nodes_x = Stack(self.num_of_rows*self.num_of_columns)
        self.empty_nodes_y = Stack(self.num_of_rows*self.num_of_columns)

    def recursive_division(self, start_x, start_y, end_x, end_y, skew=None):
        if (
                start_x not in range(self.num_of_columns + 1) or 
                end_x not in range(self.num_of_columns + 1) or
                start_y not in range(self.num_of_rows + 1) or
                end_y not in range(self.num_of_rows + 1)
        ):
            return
            
        diff_x = end_x - start_x
        diff_y = end_y - start_y

        if diff_x < 4 or diff_y < 4:
            return

        if skew == None:
            if diff_x > diff_y:
                orientation = 'vertical'
            elif diff_x < diff_y:
                orientation = 'horizontal'
            else:
                if random.getrandbits(1):
                    orientation = 'vertical'
                else:
                    orientation = 'horizontal'
        elif skew == 'vertical':
            if random.randint(1, 15) < 11:
                orientation = 'vertical'
            else:
                orientation = 'horizontal'
        elif skew == 'horizontal':
            if random.randint(1, 15) < 11:
                orientation = 'horizontal'
            else:
                orientation = 'vertical'


        if orientation == 'horizontal':
            valid_y = []
            for y in range(start_y+1, end_y):
                if self.empty_nodes_y.exists(y) == False:
                    valid_y.append(y)

            if len(valid_y) == 0:
                return

            random_y = random.choice(valid_y)

            random_empty_node_x = random.randrange(start_x, end_x)
            self.empty_nodes_x.push(random_empty_node_x)

            for x in range(start_x, end_x):
                if x != random_empty_node_x: 
                    self.rect_array[random_y][x].marked = True

            upper_end_y = random_y - 1
            lower_start_y = random_y + 1

            # Upper part
            self.recursive_division(start_x, start_y, end_x, upper_end_y, skew)

            # Lower part
            self.recursive_division(start_x, lower_start_y, end_x, end_y, skew)

        elif orientation == 'vertical':
            valid_x = []
            for x in range(start_x+1, end_x):
                if self.empty_nodes_x.exists(x) == False:
                    valid_x.append(x)

            if len(valid_x) == 0:
                return

            random_x = random.choice(valid_x)

            random_empty_node_y = random.randrange(start_y, end_y)
            self.empty_nodes_y.push(random_empty_node_y)

            for y in range(start_y, end_y):
                if y != random_empty_node_y: 
                    self.rect_array[y][random_x].marked = True

            left_end_x = random_x - 1
            right_start_x = random_x + 1

            # Left part
            self.recursive_division(start_x, start_y, left_end_x, end_y, skew)

            # Right part
            self.recursive_division(right_start_x, start_y, end_x, end_y, skew)


    def run_recursive_division(self, skew):
        self.maze = Stack(self.num_of_rows*self.num_of_columns)
        self.empty_nodes_x = Stack(self.num_of_rows*self.num_of_columns)
        self.empty_nodes_y = Stack(self.num_of_rows*self.num_of_columns)

        self.recursive_division(0, 0, self.num_of_columns, self.num_of_rows, skew)
