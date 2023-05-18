import pygame
from pygame.locals import *

from enum import Enum

from stack import Stack
from queue_classes import Queue, PriorityQueue


class AnimationTypes(Enum):
    EXPANDING_SQUARE = 0
    SHRINKING_SQUARE = 1
    CIRCLE_TO_SQUARE = 2

class AnimationNode:
    def __init__(self, coords, animation_type, foreground_color, background_color, speed, column_width, row_width, row_width_int):
        self.type = animation_type
        self.background_color = background_color
        self.foreground_color = foreground_color
        self.speed = speed
        self.center = ((row_width*coords[1])+(row_width//2), (row_width*coords[0])+(row_width//2))
        self.fraction = 0
        self.increment = row_width_int//2
        self.finished = False
        self.width = 0
        self.rect = pygame.Rect(0, 0, column_width, row_width)

class AnimationManager:
    def __init__(self, screen_manager, rect_array_obj):
        self.screen_manager = screen_manager
        self.rect_array_obj = rect_array_obj
        self.start_node_coords, self.end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()
        self.animation_dict = {}

    def add_coords_to_animation_dict(self, coords, animation_type, foreground_color, background_color, speed=1):
        if tuple(coords) in self.animation_dict.keys():
            if self.animation_dict[tuple(coords)].type == animation_type:
                return

        self.animation_dict[tuple(coords)] = AnimationNode(coords, animation_type, foreground_color, background_color, speed, self.screen_manager.column_width, self.screen_manager.row_width, self.screen_manager.row_width_int)

    def update(self):
        start_node_coords, end_node_coords = self.rect_array_obj.get_start_and_end_node_coords()
        coords_to_remove = []

        for coords, node in list(self.animation_dict.items()):
            if list(coords) == start_node_coords or list(coords) == end_node_coords:
                continue

            if node.finished:
                coords_to_remove.append(coords)
                continue

            node.rect.center = node.center

            node.fraction = round(node.fraction+(self.screen_manager.resolution_divider/100), 2)
            if node.fraction > 1:
                node.fraction = 1

            if node.type == AnimationTypes.CIRCLE_TO_SQUARE:
                pygame.draw.rect(self.screen_manager.screen, node.background_color, node.rect)

                lerp_color = pygame.Color.lerp(node.foreground_color[0], node.foreground_color[1], node.fraction)

                if node.width <= self.screen_manager.row_width//2:
                    pygame.draw.circle(self.screen_manager.screen, lerp_color, node.center, node.width)
                    node.width += 1*node.speed
                else:
                    if node.increment <= 0:
                        node.finished = True
                    else:
                        node.increment -= 1*node.speed
                    
                    pygame.draw.rect(self.screen_manager.screen, lerp_color, node.rect, 0, node.increment)

            elif node.type == AnimationTypes.EXPANDING_SQUARE:
                pygame.draw.rect(self.screen_manager.screen, node.background_color, node.rect)
                if node.width <= self.screen_manager.row_width:
                    new_rect = pygame.Rect(0, 0, node.width, node.width)
                    new_rect.center = node.center
                    pygame.draw.rect(self.screen_manager.screen, node.foreground_color, new_rect)

                    node.width += 1*node.speed
                else:
                    node.finished = True
                    pygame.draw.rect(self.screen_manager.screen, node.foreground_color, node.rect)

            elif node.type == AnimationTypes.SHRINKING_SQUARE:
                pygame.draw.rect(self.screen_manager.screen, node.background_color, node.rect)
                if node.rect.width - node.width > 0:
                    new_rect = pygame.Rect(0, 0, node.rect.width-node.width, node.rect.height-node.width)
                    new_rect.center = node.center
                    pygame.draw.rect(self.screen_manager.screen, node.foreground_color, new_rect)

                    node.width += 1*node.speed
                else:
                    node.finished = True


        for removing_coord in coords_to_remove:
            self.animation_dict.pop(removing_coord)
