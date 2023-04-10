import pygame
from pygame.locals import *

from stack import Stack
from queue_classes import Queue, PriorityQueue

class PathfindingAlgorithm:
    def __init__(self, screen, rect_array_obj, num_of_rows, num_of_columns):
        self.screen = screen
        self.num_of_columns = num_of_columns
        self.num_of_rows = num_of_rows
        self.rect_array_obj = rect_array_obj
        self.rect_array = self.rect_array_obj.array
        self.checked_nodes = Stack(self.num_of_rows*self.num_of_columns)
        self.path = Stack(self.num_of_rows*self.num_of_columns)
        self.drawn_checked_nodes = False
        self.checked_nodes_pointer = -1
        self.path_pointer = -1

    def get_checked_nodes(self):
        if self.checked_nodes == Stack(0):
            return None
        else:
            return self.checked_nodes

    def get_path(self):
        if self.path == Stack(0):
            return None
        else:
            return self.path

    def reset_checked_nodes_pointer(self):
        self.checked_nodes_pointer = -1

    def update_checked_nodes_pointer(self):
        if self.checked_nodes_pointer != self.checked_nodes.get_size():
            self.checked_nodes_pointer += 1
            return 0
        else:
            return -1

    def reset_path_pointer(self):
        self.path_pointer = -1

    def update_path_pointer(self):
        if self.path_pointer != self.path.get_size():
            self.path_pointer += 1
            return 0
        else:
            return -1

    def get_euclidean_distance(self, coords, end_node_coords):
        diff_row = end_node_coords[0]+1 - coords[0]
        diff_column = end_node_coords[1]+1 - coords[1]
        return (diff_row**2) + (diff_column**2)

    def get_manhattan_distance(self, coords, end_node_coords):
        diff_row = abs(end_node_coords[0] - coords[0])
        diff_column = abs(end_node_coords[1] - coords[1])
        manhattan_distance = diff_row + diff_column
        # NOTE(ali): This makes sure that the heuristic and distance values
        #            don't mess each other up.
        return manhattan_distance*10

    def draw(self, checked_node_color, path_node_color):
        for x in range(self.checked_nodes_pointer):
            coord = self.checked_nodes.stack[x]
            pygame.draw.rect(self.screen, checked_node_color, self.rect_array[coord[0]][coord[1]]) 

        if self.checked_nodes_pointer == self.checked_nodes.get_size():
            self.drawn_checked_nodes = True

        if self.drawn_checked_nodes:
            for x in range(self.path_pointer):
                coord = self.path.stack[x]
                pygame.draw.rect(self.screen, path_node_color, self.rect_array[coord[0]][coord[1]]) 


class DFS(PathfindingAlgorithm):
    def __init__(self, screen, rect_array_obj, num_of_rows, num_of_columns):
        super().__init__(screen, rect_array_obj, num_of_rows, num_of_columns)

    def run_dfs(self):
        self.checked_nodes = Stack(self.num_of_rows*self.num_of_columns)
        self.path = Stack(self.num_of_rows*self.num_of_columns)

        self.checked_nodes_pointer = -1
        self.path_pointer = -1

        # Getting the coordinates of the start and end nodes.
        start_node_coords, end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()
        
        self.checked_nodes.push(start_node_coords)
        self.path.push(start_node_coords)

        running = True
        while running:
            if self.path.peek(False) == -1:
                running = False
                break

            for coords in self.rect_array_obj.get_valid_adjacent_nodes(self.path.peek()):
                if coords == end_node_coords:
                    running = False
                    break
                if coords not in self.checked_nodes.stack:
                    self.checked_nodes.push(coords)
                    self.path.push(coords)
                    break
            else:
                if self.path.get_size() == 0:
                    return Stack(0)
                else:
                    self.path.pop()

        self.checked_nodes.remove_empty_values()
        self.path.remove_empty_values()


class BFS(PathfindingAlgorithm):
    def __init__(self, screen, rect_array_obj, num_of_rows, num_of_columns):
        super().__init__(screen, rect_array_obj, num_of_rows, num_of_columns)

    def run_bfs(self):
        self.checked_nodes = Stack(self.num_of_rows*self.num_of_columns)
        self.path = Stack(self.num_of_rows*self.num_of_columns)

        self.checked_nodes_pointer = -1
        self.path_pointer = -1

        frontier = Queue()

        parent_child_dict = {}

        # Getting the coordinates of the start and end nodes.
        start_node_coords, end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()

        for y in range(self.num_of_rows):
            for x in range(self.num_of_columns):
                parent_child_dict[(y, x)] = None

        self.checked_nodes.push(start_node_coords)
        frontier.enqueue(start_node_coords) 

        running = True
        while frontier.is_empty() == False and running:
            current_coord = frontier.dequeue()

            if current_coord == end_node_coords:
                running = False
                break

            for coord in self.rect_array_obj.get_valid_adjacent_nodes(current_coord):
                if self.checked_nodes.exists(coord) == False:
                    frontier.enqueue(coord)
                    self.checked_nodes.push(coord)
                    parent_child_dict[tuple(coord)] = current_coord

        
        self.checked_nodes.remove_empty_values()

        if running == False:
            self.path.push(end_node_coords)
            coord = end_node_coords
            while True:
                parent_coord = parent_child_dict[tuple(coord)]
                if parent_coord == start_node_coords:
                    break

                self.path.push(parent_coord)
                coord = parent_coord


        self.path.remove_empty_values()
        self.path.reverse()

class Dijkastra(PathfindingAlgorithm):
    def __init__(self, screen, rect_array_obj, num_of_rows, num_of_columns):
        super().__init__(screen, rect_array_obj, num_of_rows,  num_of_columns)

    def run_dijkastra(self):
        self.checked_nodes = Stack(self.num_of_rows*self.num_of_columns)
        self.path = Stack(self.num_of_rows*self.num_of_columns)

        self.checked_nodes_pointer = -1
        self.path_pointer = -1

        parent_child_dict = {}
        expanded_nodes = []
        frontier = PriorityQueue()

        # Getting the coordinates of the start and end nodes.
        start_node_coords, end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()

        for y in range(self.num_of_rows):
            for x in range(self.num_of_columns):
                parent_child_dict[(y, x)] = None

        self.checked_nodes.push(start_node_coords)
        frontier.enqueue(start_node_coords, self.rect_array_obj.get_weight_at_node(start_node_coords))

        running = True
        while frontier.is_empty() == False and running:
            current_coord = frontier.dequeue()
            expanded_nodes.append(current_coord)

            if current_coord == end_node_coords:
                running = False
                break

            for coord in self.rect_array_obj.get_valid_adjacent_nodes(current_coord):
                if coord not in expanded_nodes:
                    current_distance = self.rect_array_obj.get_weight_at_node(current_coord)
                    coord_distance = self.rect_array_obj.get_weight_at_node(coord)

                    if frontier.exists(coord) == False:
                        self.rect_array_obj.set_weight_at_node(coord, current_distance + coord_distance)
                        parent_child_dict[tuple(coord)] = current_coord
                        frontier.enqueue(coord, current_distance + coord_distance)

                        self.checked_nodes.push(coord)
                    elif current_distance + 1 < coord_distance:
                        self.rect_array_obj.set_weight_at_node(coord, current_distance + 1)
                        parent_child_dict[tuple(coord)] = current_coord

                        frontier.replace(coord, current_distance + 1)


        self.checked_nodes.remove_empty_values()

        if running == False:
            self.path.push(end_node_coords)
            coord = end_node_coords
            while True:
                parent_coord = parent_child_dict[tuple(coord)]
                if parent_coord == None:
                    break

                self.path.push(parent_coord)
                coord = parent_coord

        self.path.remove_empty_values()
        self.path.reverse()


class AStar(PathfindingAlgorithm):
    def __init__(self, screen, rect_array_obj, num_of_rows, num_of_columns):
        super().__init__(screen, rect_array_obj, num_of_rows,  num_of_columns)
        self.heuristic_dict = {}
        frontier = PriorityQueue()
        expanded_nodes = []

    def calculate_f_value(self, coords):
        g = self.rect_array_obj.get_weight_at_node(coords)
        h = self.heuristic_dict[tuple(coords)]
        return g + h

    def run_astar(self):
        self.checked_nodes = Stack(self.num_of_rows*self.num_of_columns)
        self.path = Stack(self.num_of_rows*self.num_of_columns)

        self.checked_nodes_pointer = -1
        self.path_pointer = -1

        self.heuristic_dict = {}
        parent_child_dict = {}

        frontier = PriorityQueue()
        expanded_nodes = []

        # Getting the coordinates of the start and end nodes.
        start_node_coords, end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()

        for y in range(self.num_of_rows):
            for x in range(self.num_of_columns):
                distance = self.get_manhattan_distance([y, x], end_node_coords)
                self.heuristic_dict[(y, x)] = distance
                parent_child_dict[(y, x)] = None

        frontier.enqueue(start_node_coords, self.calculate_f_value(start_node_coords))

        running = True
        while not frontier.is_empty() and running:
            current_coord = frontier.dequeue()
            expanded_nodes.append(current_coord)

            if current_coord == end_node_coords:
                running = False
                break

            for coord in self.rect_array_obj.get_valid_adjacent_nodes(current_coord):
                if coord not in expanded_nodes:
                    current_distance = self.rect_array_obj.get_weight_at_node(current_coord)
                    coord_distance = self.rect_array_obj.get_weight_at_node(coord)

                    if frontier.exists(coord) == False:
                        self.rect_array_obj.set_weight_at_node(coord, current_distance + 1)
                        parent_child_dict[tuple(coord)] = current_coord
                        frontier.enqueue(coord, self.calculate_f_value(coord))

                        self.checked_nodes.push(coord)
                    elif current_distance + 1 < coord_distance:
                        self.rect_array_obj.set_weight_at_node(coord, current_distance + 1)
                        parent_child_dict[tuple(coord)] = current_coord

                        frontier.replace(coord, self.calculate_f_value(coord))


        self.checked_nodes.remove_empty_values()

        if running == False:
            self.path.push(end_node_coords)
            coord = end_node_coords
            while True:
                parent_coord = parent_child_dict[tuple(coord)]
                if parent_coord == None:
                    break

                self.path.push(parent_coord)
                coord = parent_coord

        self.path.remove_empty_values()
        self.path.reverse()



class GreedyBFS(PathfindingAlgorithm):
    def __init__(self, screen, rect_array_obj, num_of_rows, num_of_columns):
        super().__init__(screen, rect_array_obj, num_of_rows,  num_of_columns)
        self.h_parent_dict = {}

    def run_greedy_bfs(self):
        self.checked_nodes = Stack(self.num_of_rows*self.num_of_columns)
        self.path = Stack(self.num_of_rows*self.num_of_columns)

        self.checked_nodes_pointer = -1
        self.path_pointer = -1

        heuristic_dict = {}
        parent_child_dict = {}

        frontier = PriorityQueue()
        expanded_nodes = []

        # Getting the coordinates of the start and end nodes.
        start_node_coords, end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()

        for y in range(self.num_of_rows):
            for x in range(self.num_of_columns):
                distance = self.get_manhattan_distance([y, x], end_node_coords)
                heuristic_dict[(y, x)] = distance
                parent_child_dict[(y, x)] = None

        frontier.enqueue(start_node_coords, heuristic_dict[tuple(start_node_coords)])

        running = True
        while frontier.is_empty() == False and running:
            current_coord = frontier.dequeue()
            expanded_nodes.append(current_coord)

            if current_coord == end_node_coords:
                running = False
                break

            for coord in self.rect_array_obj.get_valid_adjacent_nodes(current_coord):
                if coord not in expanded_nodes:
                    if frontier.exists(coord) == False:
                        parent_child_dict[tuple(coord)] = current_coord
                        frontier.enqueue(coord, heuristic_dict[tuple(coord)])

                        self.checked_nodes.push(coord)


        self.checked_nodes.remove_empty_values()

        if running == False:
            self.path.push(end_node_coords)
            coord = end_node_coords
            while True:
                parent_coord = parent_child_dict[tuple(coord)]
                if parent_coord == None:
                    break

                self.path.push(parent_coord)
                coord = parent_coord

        self.path.remove_empty_values()
        self.path.reverse()


class BidirectionalBFS(PathfindingAlgorithm):
    def __init__(self, screen, rect_array_obj, num_of_rows, num_of_columns):
        super().__init__(screen, rect_array_obj, num_of_rows,  num_of_columns)
        self.search_a_checked_nodes = Queue()
        self.search_b_checked_nodes = Queue()

    def find_common_coord(self):
        for item in self.search_a_checked_nodes:
            if self.search_b_checked_nodes.exists(item):
                return item

    def run_bidirectional_bfs(self):
        self.search_a_checked_nodes = Queue()
        self.search_b_checked_nodes = Queue()
        self.checked_nodes = Stack(self.num_of_rows*self.num_of_columns)

        self.path = Stack(self.num_of_rows*self.num_of_columns)

        self.checked_nodes_pointer = -1
        self.path_pointer = -1

        search_a_frontier = Queue()
        search_b_frontier = Queue()

        search_a_parent_child_dict = {}
        search_b_parent_child_dict = {}

        # Getting the coordinates of the start and end nodes.
        start_node_coords, end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()

        for y in range(self.num_of_rows):
            for x in range(self.num_of_columns):
                search_a_parent_child_dict[(y, x)] = None
                search_b_parent_child_dict[(y, x)] = None

        self.search_a_checked_nodes.enqueue(start_node_coords)

        search_a_frontier.enqueue(start_node_coords) 
        search_b_frontier.enqueue(end_node_coords) 

        running = True
        while (search_a_frontier.is_empty() == False and search_b_frontier.is_empty() == False) and running:
            search_a_current_coord = search_a_frontier.dequeue()
            search_b_current_coord = search_b_frontier.dequeue()

            common_coord = self.find_common_coord()
            if common_coord != None:
                running = False
                break

            for coord in self.rect_array_obj.get_valid_adjacent_nodes(search_a_current_coord):
                if self.search_a_checked_nodes.exists(coord) == False:
                    search_a_frontier.enqueue(coord)
                    self.search_a_checked_nodes.enqueue(coord)
                    search_a_parent_child_dict[tuple(coord)] = search_a_current_coord

            for coord in self.rect_array_obj.get_valid_adjacent_nodes(search_b_current_coord):
                if self.search_b_checked_nodes.exists(coord) == False:
                    search_b_frontier.enqueue(coord)
                    self.search_b_checked_nodes.enqueue(coord)
                    search_b_parent_child_dict[tuple(coord)] = search_b_current_coord

        
        if running == False:
            common_coord = self.find_common_coord()

            path_a = Stack(self.num_of_rows*self.num_of_columns)
            path_b = Stack(self.num_of_rows*self.num_of_columns)

            search_a_coord = common_coord
            search_b_coord = common_coord

            path_a.push(common_coord)
            coord = common_coord
            while True:
                parent_coord = search_a_parent_child_dict[tuple(coord)]
                if parent_coord == start_node_coords:
                    break

                path_a.push(parent_coord)
                coord = parent_coord

            path_a.reverse()

            coord = common_coord
            while True:
                parent_coord = search_b_parent_child_dict[tuple(coord)]
                if parent_coord == end_node_coords:
                    break

                path_b.push(parent_coord)
                coord = parent_coord

            self.path.merge(path_a, path_b)

        # NOTE(ali): Getting the checked nodes.
        while True:
            coord_a = self.search_a_checked_nodes.dequeue()
            coord_b = self.search_b_checked_nodes.dequeue()

            if coord_a != None:
                self.checked_nodes.push(coord_a)
            if coord_b != None:
                self.checked_nodes.push(coord_b)

            if coord_a == None and coord_b == None:
                self.checked_nodes.remove_empty_values()
                break