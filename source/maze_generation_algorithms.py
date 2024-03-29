import pygame
from pygame.locals import *
import random

from enum import IntEnum

from animations import *

from stack import Stack
from queue_classes import Queue, PriorityQueue

class MazeGenerationAlgorithmTypes(IntEnum):
    RANDOM_WEIGHTED_MAZE = 0,
    RANDOM_MARKED_MAZE = 1,
    RECURSIVE_DIVISION = 2

class MazeGenerationAlgorithm:
    def __init__(self, screen_manager, rect_array_obj, color_manager, animation_manager):
        """
        Initalizes the MazeGenerationAlgorithm class.

        @param screen_manager: ScreenManager
        @param rect_array_obj: RectArray
        @param color_manager: ColorManager
        @param animation_manager: AnimationManager
        """
        self.screen_manager = screen_manager
        self.animation_manager = animation_manager
        self.rect_array_obj = rect_array_obj
        self.maze = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)
        self.maze_pointer = -1
        self.color_manager = color_manager
        self.animated_coords = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)
        self.skew = None
        self.type = None

    def reset_maze(self):
        """
        This function will set the value of the self.maze attribute to be a new stack which will have a
        size that is the same as the number of nodes in the grid (we can calculate this by multiplying
        the num_of_rows attribute by the num_of_columns attribute which are both found in self.screen_manager.
        """
        self.maze = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)

    def reset_animated_coords_stack(self):
        """
        This function will set the value of the self.animated_coords attribute to be a new stack which will have a
        size that is the same as the number of nodes in the grid (we can calculate this by multiplying
        the num_of_rows attribute by the num_of_columns attribute which are both found in self.screen_manager.
        """
        self.animated_coords = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)

    def reset_maze_pointer(self):
        """
        This function will set the value of the self.maze_pointer attribute to be -1.
        """
        self.maze_pointer = -1

    def update_maze_pointer(self):
        """
        This function will increment the value of self.maze_pointer as long as it is less than the
        size of the self.maze stack (we can get the size of self.maze using self.maze.get_size()). If
        this condition is met we will increment self.maze_pointer and return 0 otherwise we will return -1.

        @return: int
        """
        if self.maze_pointer != self.maze.get_size():
            self.maze_pointer += 1
            return 0
        else:
            return -1

    def cut_maze(self, cut_off_index=None):
        """
        This function is used to change the number of coordinates in the self.maze stack.
        If the cut_off_index variable has a value of None we will then make the cut_off_index
        variable have the same value as the self.maze_pointer attribute. If the cut_off_index
        variable has been given a value other than None then we will set the self.maze_pointer
        attribute to have the same value as the cut_off_index variable. We will then resize
        the self.maze stack by removing any coordinates which come after the index of the
        cut_off_index variable.

        @param cut_off_index: int or None
        """
        if cut_off_index == None:
            cut_off_index = self.maze_pointer
        else:
            self.maze_pointer = cut_off_index

        self.maze.stack = self.maze.stack[:cut_off_index]

    def draw(self):
        """
        This function is called every frame when we need to draw a maze generation algorithm.

        When we first start drawing a maze generation algorithm the self.maze_pointer attribute
        is set to 0. Over time, we increment the value of self.maze_pointer (this process is handled
        separately and not by this function) and start drawing and animating nodes onto the screen.

        We will first check if the coordinate in self.maze at the index of self.maze_pointer is
        in the self.animated_coords stack. If it is not we will animate the coordinate using the
        add_coords_to_animation_dict method in self.animation_manager, and we will also push these
        coordinates onto the self.animated_coords stack.

        After this we will then draw all the other coordinates which came before the coordinate at
        self.maze_pointer as rectangles (since they will have been animated before).
        """
        for x in range(self.maze_pointer):
            coord = self.maze.stack[x]
            if self.animated_coords.exists(coord) == False:
                self.animation_manager.add_coords_to_animation_dict(coord, AnimationTypes.EXPANDING_SQUARE, self.color_manager.MARKED_NODE_COLOR, AnimationBackgroundTypes.THEME_BACKGROUND)
                self.rect_array_obj.array[coord[0]][coord[1]].marked = True
                self.animated_coords.push(coord)
            else:
                pygame.draw.rect(self.screen_manager.screen, self.color_manager.MARKED_NODE_COLOR, self.rect_array_obj.array[coord[0]][coord[1]])

class RandomWeightedMaze(MazeGenerationAlgorithm):
    def __init__(self, screen_manager, rect_array_obj, color_manager, animation_manager):
        """
        Initializes the RandomWeightedMaze class.

        @param screen_manager: ScreenManager
        @param rect_array_obj: RectArray
        @param color_manager: ColorManager
        @param animation_manager: AnimationManager
        """
        super().__init__(screen_manager, rect_array_obj, color_manager, animation_manager)
        self.type = MazeGenerationAlgorithmTypes.RANDOM_WEIGHTED_MAZE

    def create_random_weighted_maze(self):
        """
        This algorithm will go through each RectNode in self.rect_array_obj.array and
        randomly choose whether the RectNode should be weighted, if we decided that the
        RectNode should be weighted we will choose a random weight for it and set the
        RectNode's is_user_weight attribute to True and the weight attribute to the weight
        we have randomly generated. We will also animate this RectNode using the
        add_coords_to_animation_dict method in self.animation_manager.
        """
        self.reset_maze()

        for y in range(self.screen_manager.num_of_rows):
            for x in range(self.screen_manager.num_of_columns):
                weight = random.randint(1, 100)
                should_be_weighted_node = random.choice([0, 0, 1, 0])
                if should_be_weighted_node:
                    self.rect_array_obj.array[y][x].is_user_weight = True
                    self.rect_array_obj.array[y][x].weight = weight
                    self.maze.push([[y, x], weight])
                    self.animation_manager.add_coords_to_animation_dict((y, x), AnimationTypes.EXPANDING_SQUARE, self.color_manager.WEIGHTED_NODE_COLOR, AnimationBackgroundTypes.THEME_BACKGROUND)

class RandomMarkedMaze(MazeGenerationAlgorithm):
    def __init__(self, screen_manager, rect_array_obj, color_manager, animation_manager):
        """
        Initializes the RandomMarkedMaze class.

        @param screen_manager: ScreenManager
        @param rect_array_obj: RectArrayObj
        @param color_manager: ColorManager
        @param animation_manager: AnimationManager
        """
        super().__init__(screen_manager, rect_array_obj, color_manager, animation_manager)
        self.type = MazeGenerationAlgorithmTypes.RANDOM_MARKED_MAZE

    def create_random_marked_maze(self):
        """
        This algorithm will go through each RectNode in self.rect_array_obj.array and
        randomly choose whether the RectNode should be marked, if we decided that the
        RectNode should be marked we will set the RectNode's marked attribute to True.
        We will also animate this RectNode using the add_coords_to_animation_dict method
        in self.animation_manager.
        """
        self.reset_maze()

        for y in range(self.screen_manager.num_of_rows):
            for x in range(self.screen_manager.num_of_columns):
                should_be_marked = random.choice([0, 0, 1, 0])
                if should_be_marked:
                    self.rect_array_obj.array[y][x].marked = True
                    self.maze.push([y, x])
                    self.animation_manager.add_coords_to_animation_dict((y, x), AnimationTypes.EXPANDING_SQUARE, self.color_manager.MARKED_NODE_COLOR, AnimationBackgroundTypes.THEME_BACKGROUND)


class RecursiveDivisionSkew(IntEnum):
    VERTICAL = 0
    HORIZONTAL = 1

class RecursiveDivisionMaze(MazeGenerationAlgorithm):
    def __init__(self, screen_manager, rect_array_obj, color_manager, animation_manager):
        """
        Initializes the RecursiveDivisionMaze class.

        @param screen_manager: ScreenManager
        @param rect_array_obj: RectArrayObj
        @param color_manager: ColorManager
        @param animation_manager: AnimationManager
        """
        super().__init__(screen_manager, rect_array_obj, color_manager, animation_manager)
        self.empty_nodes_x = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)
        self.empty_nodes_y = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)
        self.type = MazeGenerationAlgorithmTypes.RECURSIVE_DIVISION

    def recursive_division(self, start_x, start_y, end_x, end_y, skew=None):
        """
        This function recursively calls itself to generate the Recursive Division Maze, and it will
        push the coordinates of the marked nodes in the maze to the self.maze stack.

        @param start_x: int
        @param start_y: int
        @param end_x: int
        @param end_y: int
        @param skew: RecursiveDivisionSkew
        @return: None
        """
        if (
                start_x not in range(self.screen_manager.num_of_columns + 1) or 
                end_x not in range(self.screen_manager.num_of_columns + 1) or
                start_y not in range(self.screen_manager.num_of_rows + 1) or
                end_y not in range(self.screen_manager.num_of_rows + 1)
        ):
            return

        start_node_coords, end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()
            
        diff_x = end_x - start_x
        diff_y = end_y - start_y

        if diff_x < 4 or diff_y < 4:
            return

        orientation = None
        if skew == None:
            if diff_x > diff_y:
                orientation = RecursiveDivisionSkew.VERTICAL
            elif diff_x < diff_y:
                orientation = RecursiveDivisionSkew.HORIZONTAL
            else:
                if random.getrandbits(1):
                    orientation = RecursiveDivisionSkew.VERTICAL
                else:
                    orientation = RecursiveDivisionSkew.HORIZONTAL
        elif skew == RecursiveDivisionSkew.VERTICAL:
            if random.randint(1, 15) < 11:
                orientation = RecursiveDivisionSkew.VERTICAL
            else:
                orientation = RecursiveDivisionSkew.HORIZONTAL
        elif skew == RecursiveDivisionSkew.HORIZONTAL:
            if random.randint(1, 15) < 11:
                orientation = RecursiveDivisionSkew.HORIZONTAL
            else:
                orientation = RecursiveDivisionSkew.VERTICAL


        if orientation == RecursiveDivisionSkew.HORIZONTAL:
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
                if (
                        x != random_empty_node_x and
                        [random_y, x] != start_node_coords and
                        [random_y, x] != end_node_coords
                ): 
                    self.maze.push([random_y, x])

            upper_end_y = random_y - 1
            lower_start_y = random_y + 1

            # Upper part
            self.recursive_division(start_x, start_y, end_x, upper_end_y, skew)

            # Lower part
            self.recursive_division(start_x, lower_start_y, end_x, end_y, skew)

        elif orientation == RecursiveDivisionSkew.VERTICAL:
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
                if (
                        y != random_empty_node_y and
                        [y, random_x] != start_node_coords and
                        [y, random_x] != end_node_coords
                ): 
                    self.maze.push([y, random_x])

            left_end_x = random_x - 1
            right_start_x = random_x + 1

            # Left part
            self.recursive_division(start_x, start_y, left_end_x, end_y, skew)

            # Right part
            self.recursive_division(right_start_x, start_y, end_x, end_y, skew)


    def run_recursive_division(self):
        """
        This function is called to run recursive division, it will reset the self.maze stack
        using the reset_maze method as well as making the self.empty_nodes_x and self.empty_nodes_y
        attributes both point to empty Stacks which are have the same size as the number of nodes in the
        grid (this can be calculated by multiplying the num_of_rows and num_of_columns attributes found
        in self.screen_manager). This function will then call the recursive_division function which will
        recursively call itself until it has finished generated the maze (it will push all the coordinates
        in the maze to the self.maze stack).
        """
        self.reset_maze()
        self.empty_nodes_x = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)
        self.empty_nodes_y = Stack(self.screen_manager.num_of_rows*self.screen_manager.num_of_columns)

        self.recursive_division(0, 0, self.screen_manager.num_of_columns, self.screen_manager.num_of_rows, self.skew)
