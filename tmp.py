import sys, random
import pygame
from pygame.locals import *
import pymunk.pygame_util
import pymunk
import math
# def add_ball(space):
#     mass = 1
#     radius = 14
#     moment = pymunk.moment_for_circle(mass, 0, radius) # 1
#     body = pymunk.Body(mass, moment) # 2
#     x = random.randint(120, 380)
#     body.position = x, 550 # 3
#     shape = pymunk.Circle(body, radius) # 4
#     space.add(body, shape) # 5
#     return shape
# def add_static_L(space):
#     body = pymunk.Body(body_type = pymunk.Body.STATIC) # 1
#     body.position = (300, 300)
#     l1 = pymunk.Segment(body, (-150, 0), (255, 0), 5) # 2
#     l2 = pymunk.Segment(body, (-150, 0), (-150, 50), 5)
#
#     space.add(l1, l2) # 3
#     return l1,l2
# def to_pygame(p):
#     """Small hack to convert pymunk to pygame coordinates"""
#     return int(p.x), int(-p.y+600)
#def to_pygame(p):
#def add_ball(space):
#def add_static_l(space):
def main(insert_space=None, insert_screen=None):
    # pygame.init()
    pygame.display.set_mode((600, 600))
    # pygame.display.set_caption("Joints. Just wait and the L will tip over")
    # if insert_space is not None:
    #     space = insert_space
    # draw_options = pymunk.pygame_util.DrawOptions(screen)

def main_orig(insert_space=None, insert_screen=None):
    pygame.init()
    if insert_screen is not None:
        screen = insert_screen
    else:
        screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Joints. Just wait and the L will tip over")
    # clock = pygame.time.Clock()
    #
    # space = pymunk.Space()
    # space.gravity = (0.0, -900.0)
    if insert_space is not None:
        space = insert_space
    # lines = add_static_L(space)
    # balls = []
    draw_options = pymunk.pygame_util.DrawOptions(screen)

    # ticks_to_next_ball = 10
    # do_draw(screen, space, draw_options)
    # while True:
    #     # for event in pygame.event.get():
    #     #     if event.type == QUIT:
    #     #         sys.exit(0)
    #     #     elif event.type == KEYDOWN and event.key == K_ESCAPE:
    #     #         sys.exit(0)
    #     #
    #     # ticks_to_next_ball -= 1
    #     # if ticks_to_next_ball <= 0:
    #     #     ticks_to_next_ball = 25
    #     #     ball_shape = add_ball(space)
    #     #     balls.append(ball_shape)
    #
    #     # space.step(1/50.0)
    #
    #     break
    #     # import time
        # time.sleep(1)
        # clock.tick(50)
def do_draw(screen, space, draw_options):
    # for event in pygame.event.get():
    #     pass
    screen.fill((255, 255, 255))
    space.debug_draw(draw_options)

    pygame.display.flip()

if __name__ == '__main__':
    (main())