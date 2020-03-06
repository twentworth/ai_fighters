"""
Use Pymunk physics engine.

For more info on Pymunk see:
http://www.pymunk.org/en/latest/

To install pymunk:
pip install pymunk

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.pymunk_box_stacks

Click and drag with the mouse to move the boxes.
"""
import random
import arcade
import pymunk
import timeit
import math
import os
import math
import time
import neat
import matplotlib.pyplot as plt
import pymunk.matplotlib_util
import pygame
from pygame.locals import *
import gzip
import pymunk.pygame_util

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
SCREEN_TITLE = "Pymunk test"
FRAMERATE = 10

DIRECTIONS = {}
for k in range(8):
    v = pymunk.Vec2d((1, 0))
    v.rotate_degrees(45 * k)
    DIRECTIONS[k] = v
KEYS_TO_DIRECTIONS = {
    frozenset((arcade.key.RIGHT,)): 0,
    frozenset((arcade.key.RIGHT, arcade.key.UP)): 1,
    frozenset((arcade.key.UP,)): 2,
    frozenset((arcade.key.LEFT, arcade.key.UP)): 3,
    frozenset((arcade.key.LEFT,)): 4,
    frozenset((arcade.key.LEFT, arcade.key.DOWN)): 5,
    frozenset((arcade.key.DOWN,)): 6,
    frozenset((arcade.key.DOWN, arcade.key.RIGHT)): 7,
}
KEYS_TO_DIRECTIONS_2 = {
    frozenset((arcade.key.D,)): 0,
    frozenset((arcade.key.D, arcade.key.W)): 1,
    frozenset((arcade.key.W,)): 2,
    frozenset((arcade.key.A, arcade.key.W)): 3,
    frozenset((arcade.key.A,)): 4,
    frozenset((arcade.key.A, arcade.key.S)): 5,
    frozenset((arcade.key.S,)): 6,
    frozenset((arcade.key.S, arcade.key.D)): 7,
}

def keys_to_dir(keys, keymap):
    mx_val = None
    mx_num = 0
    for k, v in keymap.items():
        x = len(k.intersection(keys))

        if x > mx_num and x == len(k):
            mx_num = x
            mx_val = v
    return mx_val

class PhysicsSprite(arcade.Sprite):
    def __init__(self, pymunk_shape, filename):
        super().__init__(filename, center_x=pymunk_shape.body.position.x, center_y=pymunk_shape.body.position.y)
        self.pymunk_shape = pymunk_shape


class CircleSprite(PhysicsSprite):
    def __init__(self, pymunk_shape, filename):
        super().__init__(pymunk_shape, filename)
        self.width = pymunk_shape.radius * 4
        self.height = pymunk_shape.radius * 4
def tf(x):
    if x >= .5:
        return 1
    else:
        return 0
def post_solve_bullet_hit(arbiter, space, data):
    bullet_shape, fighter_shape = arbiter.shapes

    bullet = data['arcade'].shape_to_obj_map.get(bullet_shape)
    fighter = data['arcade'].shape_to_obj_map.get(fighter_shape)

    if bullet is None:
        if bullet_shape not in data['arcade'].shapes_deleted_this_step:
            print('Lost object:', bullet_shape)
        return

    if fighter is not None and fighter != bullet.who_fired_me: #we hit an enemy
        fighter.health -= bullet.damage
        fighter.last_damage_time = data['arcade'].sim_time
        bullet.who_fired_me.damage_dealt += bullet.damage
        fighter.last_damage_enemy = bullet.who_fired_me

    data['arcade'].delete_object(bullet)

def warped_path(pos1, pos2, width, height):
    """
    returns the vector to the nearest direction to pos2 from pos1
    :param pos1:
    :param pos2:
    :param width:
    :param height:
    :return:
    """
    smallest_vec = None
    smallest_distance = float('inf')
    for xadd in (-width, 0, width):
        for yadd in (-height, 0, height):
            pos2_2 = pos2 + pymunk.Vec2d(xadd, yadd)
            diff = pos2_2 - pos1
            if diff.length < smallest_distance:
                smallest_vec = diff
                smallest_distance = diff.length
    return smallest_vec



class Bullet(object):
    size = 10
    mass = .1
    thrust_force = 200
    max_velocity = 400
    image = ":resources:images/items/coinGold.png"
    category = 0b100
    filter_mask = pymunk.ShapeFilter.ALL_MASKS ^ 0b100
    damage = 3
    collision_type = 1

    def __init__(self, x, y, space, simulator):
        self.space = space
        self.simulator = simulator
        self.moment = pymunk.moment_for_circle(self.mass, 0, self.size, (0, 0))
        self.body = pymunk.Body(self.mass, self.moment)
        self.body.position = pymunk.Vec2d(x, y)
        self.shape = pymunk.Circle(self.body, self.size, pymunk.Vec2d(0, 0))
        self.shape.filter = pymunk.ShapeFilter(categories=self.category, mask=self.filter_mask)
        self.shape.collision_type = self.collision_type
        self.shape.elasticity = 0
        self.shape.friction = .9
        self.body.collision_type = 0

        self.space.add(self.body, self.shape)
        self.sprite = CircleSprite(self.shape, self.image)
        self.who_fired_me = None
        self.distance_traveled = 0
        self.prev_location = self.body.position
        self.max_travel_distance_allowed = math.sqrt(self.simulator.width ** 2 + self.simulator.height ** 2)
    @property
    def x(self):
        return self.body.position.x

    @property
    def y(self):
        return self.body.position.y

    @property
    def position(self):
        return self.body.position

    def delete(self):
        self.space.remove(self.shape, self.body)

    def set_velocity(self, vec):
        self.body.velocity = vec

    def set_vel_direction_at_max(self, vec):
        vec = vec/vec.length
        self.body.velocity = vec * self.max_velocity

    def on_draw_fn(self):
        self.sprite.center_x = self.x
        self.sprite.center_y = self.y
        self.sprite.angle = math.degrees(self.shape.body.angle)
    def update(self):
        self.distance_traveled += (self.position - self.prev_location).length
        if self.distance_traveled > self.max_travel_distance_allowed:
            self.simulator.delete_object(self)
        self.prev_location = self.position





class Fighter_base(Bullet):
    size = 16
    mass = 1
    thrust_force = 1200
    max_velocity = 120
    shoot_time = .15
    shoot_damage = .3
    shoot_energy_restore = .3
    shoot_energy_restore = .3
    max_shoot_energy = 2
    image = ":resources:images/items/coinGold.png"
    category = 0b10
    filter_mask = pymunk.ShapeFilter.ALL_MASKS
    collision_type = 2
    max_health = 100
    def __init__(self, x, y, space, simulator):
        super().__init__(x, y, space, simulator)
        self.shape.elasticity = .5
        self.shape.friction = 0
        self.body.collision_type = 1


        self.most_recent_bullet_time = 100

        self.health = self.max_health
        self.shoot_energy = self.max_shoot_energy
        self.last_shot_time = 0

        self.body_direction = 0
        self.gun_direction = 0
        self.is_shooting = 0
        self.is_thrusting = 0
        self.creation_time = self.simulator.sim_time
        self.death_time = 0
        self.damage_dealt = 0
        self.last_update_time = 0
        self.last_damage_time = 0
        self.last_damage_enemy = None
        self.is_invincible = False
        self.max_travel_distance_allowed = float('inf')
    def shoot(self):
        if self.simulator.sim_time - self.last_shot_time > self.shoot_time and self.shoot_energy > 0:
            self.last_shot_time = self.simulator.sim_time
            cur_pos = self.position
            offset = self.size + Bullet.size
            new_position = cur_pos + DIRECTIONS[self.gun_direction] * offset
            new_bullet = Bullet(new_position.x, new_position.y, self.space, self.simulator)
            new_bullet.set_vel_direction_at_max(DIRECTIONS[self.gun_direction])
            new_bullet.who_fired_me = self
            self.simulator.register_object(new_bullet)
            self.shoot_energy -= self.shoot_damage
    def update(self):
        super().update()

        # if self.x < 0:
        #     self.body.position.x += self.simulator.width
        # elif self.x > self.simulator.width:
        #     self.body.position.x -= self.simulator.width
        # if self.y < 0:
        #     self.body.position.y += self.simulator.height
        # elif self.y > self.simulator.height:
        #     self.body.position.y -= self.simulator.height

        if self.body.velocity.length < .05 * self.max_velocity:
            self.body.velocity *= 0
        if self.is_thrusting:
            force = self.thrust_force * DIRECTIONS[self.body_direction]
        else:
            vel_dir = self.body.velocity
            vel_p = min(1, vel_dir.length / self.max_velocity)
            if vel_dir.length > 0: vel_dir /= -vel_dir.length
            force = self.thrust_force/5 * vel_dir * vel_p
        self.body.apply_force_at_world_point(force, (self.x, self.y))  # , point=pymunk.Vec2d(x,y))

        if self.is_shooting: self.shoot()

        if self.body.velocity.length > self.max_velocity:
            percent = (self.body.velocity.length - ((self.body.velocity.length - self.max_velocity) / FRAMERATE * 4))/self.body.velocity.length
            self.body.velocity = self.body.velocity * percent

        # restore health
        cur_time = self.simulator.sim_time
        self.shoot_energy = min(self.shoot_energy + self.shoot_energy_restore * (cur_time - self.last_update_time), self.max_shoot_energy)
        self.last_update_time = cur_time

        self.body.position.x = max(self.body.position.x, self.size)
        self.body.position.x = min(self.body.position.x, self.simulator.width - self.size)
        self.body.position.y = max(self.body.position.y, self.size)
        self.body.position.y = min(self.body.position.y, self.simulator.height - self.size)

        if self.health <= 0 and not self.is_invincible:
            self.death_time = self.simulator.sim_time
            self.delete()
            self.simulator.delete_object(self)




class Player_Fighter(Fighter_base):

    def update(self):
        self.key_input(self.simulator.keys)
        super().update()

    def key_input(self, keys):
        dir = keys_to_dir(keys, KEYS_TO_DIRECTIONS)
        gun_dir = keys_to_dir(keys, KEYS_TO_DIRECTIONS_2)

        if dir is not None:
            self.body_direction = dir
            self.is_thrusting = 1
        else:
            self.is_thrusting = 0

        if gun_dir is not None:
            self.is_shooting = 1
            self.gun_direction = gun_dir
        else:
            self.is_shooting = 0

class AI_Fighter(Fighter_base):

    def __init__(self, x, y, space, simulator, ai_genome, config):
        super().__init__(x, y, space, simulator)
        self.ai_genome = ai_genome
        self.ai_net = neat.nn.FeedForwardNetwork.create(ai_genome, config)
        self.model_output = None

    def update_ai_fitness(self, x):
        if self.ai_genome.fitness is None:
            self.ai_genome.fitness = 0
        self.ai_genome.fitness += x
    #
    # def dist_health_to_targeted_enemy(self):
    #     x0 = self.position
    #     x0 += DIRECTIONS[self.gun_direction] * self.size + Bullet.size
    #     max_distance = self.simulator.max_distance
    #     x1 = x0 + DIRECTIONS[self.gun_direction] * max_distance
    #     query_info = self.space.segment_query_first(x0, x1, Bullet.size, pymunk.ShapeFilter(mask=self.category))
    #     if query_info is None:
    #         return self.simulator.max_distance, Fighter_base.max_health
    #     shape = query_info.shape
    #     # x_2 = shape.body.position.x
    #     # y_2 = shape.body.position.y
    #     enemy_obj = self.simulator.shape_to_obj_map[shape]
    #
    #     return (self.position - shape.body.position).length / self.simulator.max_distance, enemy_obj.health / enemy_obj.max_health

    def nearest_enemy_dir(self):
        dist = float('inf')
        cur_fighter = None
        for fighter in self.simulator.fighters:
            if fighter == self:
                continue

            fighter_dist = warped_path(self.body.position, fighter.body.position, self.simulator.width, self.simulator.height)
            cur_dist = fighter_dist.length
            if cur_dist < dist:
                dist = cur_dist
                cur_fighter_vec = fighter_dist
        if cur_fighter is None:
            return pymunk.Vec2d(1,1)
        return cur_fighter_vec

    def get_model_input(self):


        nearest_enemy_vec = self.nearest_enemy_dir()
        total_len = math.sqrt(self.simulator.width ** 2 + self.simulator.height ** 2)

        # who_shot_me = self.last_damage_enemy
        # if who_shot_me is not None:
        #     who_shot_me_vec = warped_path(self.body.position, who_shot_me.body.position, self.simulator.width, self.simulator.height)
        # else:
        #     who_shot_me_vec = pymunk.Vec2d(total_len * 2, 0)



        return [
            self.body.velocity.length /total_len,
            self.body.velocity.angle,#velocity angle
            #x,y, health direction of nearest enemy
            nearest_enemy_vec.length / total_len,
            nearest_enemy_vec.angle,
            #dist to enemy in gun direction , ...
            # who_shot_me_vec.length / total_len,
            # who_shot_me_vec.angle,
            # enemy health in direction
            self.simulator.sim_time - self.last_damage_time,
        ]
    def set_model_output(self, output):
        """
        output format:
        [
        is_shooting
        is_thrusting
        dir_bit_1
        dir_bit_2
        dir_bit_3
        gun_bit_1
        gun_bit_2
        gun_bit_3
        ]
        """
        self.model_output = output
        self.is_shooting = tf(output[0])
        self.is_thrusting = tf(output[1])
        self.body_direction = tf(output[2]) + 2 * tf(output[3]) + 4 * tf(output[4])
        self.gun_direction = tf(output[5]) + 2 * tf(output[6]) + 4 * tf(output[7])

    def update(self):
        self.set_model_output(self.ai_net.activate(self.get_model_input()))
        super().update()


class BoxSprite(PhysicsSprite):
    def __init__(self, pymunk_shape, filename, width, height):
        super().__init__(pymunk_shape, filename)
        self.width = width
        self.height = height

class simulator(object):
    width = SCREEN_WIDTH
    height = SCREEN_HEIGHT
    def __init__(self):
        self.space = pymunk.Space()
        self.space.iterations = 35
        self.space.gravity = (0.0, 0)  # -900.0)

        # Lists of sprites or lines

        self.static_lines = []
        self.shape_to_obj_map = {}
        self.shapes_deleted_this_step = set()
        self.sim_time = 0

        self.draw_time = 0
        self.processing_time = 0

        self.keys = set()

        # Create the box
        # floor_height = 0
        # body = pymunk.Body(body_type=pymunk.Body.STATIC)
        #
        # for x,y in (([0, floor_height], [SCREEN_WIDTH, floor_height]),
        #             ([0, SCREEN_HEIGHT - floor_height], [SCREEN_WIDTH, SCREEN_HEIGHT - floor_height]),
        #             ([floor_height, floor_height], [floor_height, SCREEN_HEIGHT - floor_height]),
        #             ([SCREEN_WIDTH - floor_height, floor_height], [SCREEN_WIDTH - floor_height, SCREEN_HEIGHT - floor_height])):
        #     shape = pymunk.Segment(body, x,y, 0.0)
        #     shape.friction = 10
        #     shape.collision_type = 3
        #     shape.filter = pymunk.ShapeFilter(categories=0b1)
        #     self.space.add(shape)
        #     self.static_lines.append(shape)



        # shape = pymunk.Segment(body, [0, floor_height], [SCREEN_WIDTH, floor_height], 0.0)
        # shape.friction = 10
        # shape.collision_type = 3
        # self.space.add(shape)
        # self.static_lines.append(shape)
        #
        # shape = pymunk.Segment(body, [0, SCREEN_HEIGHT - floor_height], [SCREEN_WIDTH, SCREEN_HEIGHT - floor_height],
        #                        0.0)
        # shape.friction = 10
        # shape.collision_type = 3
        # shape.filter = pymunk.ShapeFilter(categories=0b1)
        # self.space.add(shape)
        # self.static_lines.append(shape)
        #
        # shape = pymunk.Segment(body, [floor_height, floor_height], [floor_height, SCREEN_HEIGHT - floor_height], 0.0)
        # shape.friction = 10
        # shape.collision_type = 3
        # self.space.add(shape)
        # self.static_lines.append(shape)
        #
        # shape = pymunk.Segment(body, [SCREEN_WIDTH - floor_height, floor_height],
        #                        [SCREEN_WIDTH - floor_height, SCREEN_HEIGHT - floor_height], 0.0)
        # shape.friction = 10
        # shape.collision_type = 3
        # self.space.add(shape)
        # self.static_lines.append(shape)

        self.fighters = set()#{Player_Fighter(500, 500, self.space, self), Fighter_base(540, 500, self.space, self)}
        self.bullets = set()#{Bullet(600, 600, self.space, self), Bullet(640, 600, self.space, self)}
        self.dead_fighters = set()

        for obj in self.all_objects:
            self.shape_to_obj_map[obj.shape] = obj
        # flying_arrows = []
        self.bullet_hit_handler = self.space.add_collision_handler(Bullet.collision_type, Fighter_base.collision_type)
        self.bullet_hit_handler.data['arcade'] = self
        self.bullet_hit_handler.post_solve = post_solve_bullet_hit

        self.bullet_hit_handler = self.space.add_collision_handler(Bullet.collision_type, 3)
        self.bullet_hit_handler.data['arcade'] = self
        self.bullet_hit_handler.post_solve = post_solve_bullet_hit
    @property
    def all_objects(self):
        return self.fighters.union(self.bullets)

    @property
    def all_fighters_dead_and_alive(self):
        return self.fighters.union(self.dead_fighters)

    @property
    def max_distance(self):
        return math.sqrt(self.width ** 2 + self.height ** 2)

    def create_ai_fighters_from_gennomes(self, genomes, config, create_human=False):
        prev_coords = []

        def get_random_start():
            k = True
            while k:
                new_coord = pymunk.Vec2d(Fighter_base.size + random.random() * (self.width - 2 * Fighter_base.size),
                                         Fighter_base.size + random.random() * (self.height - 2 * Fighter_base.size))
                if not any((x - new_coord).length < Fighter_base.size for x in prev_coords):
                    k = False
            prev_coords.append(new_coord)
            new_vel = pymunk.Vec2d(Fighter_base.max_velocity,0) * random.random()
            new_vel.rotate(2 * math.pi * random.random())
            return new_coord, new_vel
            pass
        x0 = pymunk.Vec2d(self.width/2, self.height/2)
        angle_add = 2 * math.pi * random.random()
        for i, genome in enumerate(genomes):
            # stvec = pymunk.Vec2d(1,0)
            # stvec.rotate(i * 2 * math.pi / (len(genomes) + create_human) + angle_add)
            # x1 = x0 + 150 * stvec
            x1, v1 = get_random_start()
            new_fighter = AI_Fighter(x1.x, x1.y, self.space, self, genome, config)
            new_fighter.shape.velocity = v1
            self.register_object(new_fighter)
        if create_human:
            # x1 = x0 + 150 * pymunk.Vec2d(1, 0).rotate(len(genomes) * 2 * math.pi / (len(genomes) + create_human) + angle_add)
            x1, v1 = get_random_start()
            new_fighter = Player_Fighter(x1.x, x1.y, self.space, self)
            new_fighter.shape.velocity = v1
            self.register_object(new_fighter)

    def register_object(self, obj):
        self.shape_to_obj_map[obj.shape] = obj
        if isinstance(obj, Fighter_base):
            self.fighters.add(obj)
        elif isinstance(obj, Bullet):
            self.bullets.add(obj)

    def delete_object(self, obj):

        try:
            self.shapes_deleted_this_step.add(obj.shape)
            if isinstance(obj, Fighter_base):
                self.dead_fighters.add(obj)
                if obj.death_time <= 0: obj.death_time = self.sim_time
                self.fighters.remove(obj)
            elif isinstance(obj, Bullet):
                self.bullets.remove(obj)
            if obj is not None:
                obj.delete()
        except KeyError:
            pass
        try:
            del self.shape_to_obj_map[obj.shape]
        except KeyError:
            pass

    def run_full_simulation(self, t, display_sim=False):

        # print('start')
        if display_sim:
            pygame.init()
            screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("Joints. Just wait and the L will tip over")
            draw_options = pymunk.pygame_util.DrawOptions(screen)


        tlast = time.time()
        for _ in range(int(t * FRAMERATE)):
            self.on_update()
            if display_sim:
                time.sleep(max(1 / FRAMERATE - (time.time() - tlast), 0))
                tlast = time.time()
                screen.fill((255, 255, 255))
                self.space.debug_draw(draw_options)

                pygame.display.flip()
                pygame.display.set_mode((self.width, self.height))
                if _%FRAMERATE == 0:
                    print(_ * FRAMERATE)
        total_time = 0
        total_damage = 0
        total_health_removed = 0
        for obj in self.all_fighters_dead_and_alive:
            if obj.death_time <= 0:
                obj.death_time = self.sim_time
            total_time += obj.death_time - obj.creation_time
            total_damage += obj.damage_dealt
            total_health_removed += obj.max_health - obj.health #computing seperately since damage dealt can maybe miss damage on race conditions?
            if total_damage == 0: total_damage = 1
            if total_health_removed == 0: total_health_removed = 1
        # print('TT: ',total_time, 'total dmg: ', total_damage)
        #update fitnesses
        for obj in self.all_fighters_dead_and_alive:
            if isinstance(obj, AI_Fighter):
                # obj.update_ai_fitness(2 * (obj.death_time - obj.creation_time) - total_time + obj.damage_dealt/100)
                # obj.update_ai_fitness(obj.damage_dealt + obj.health + (obj.death_time - obj.creation_time)/total_time*10)
                damage_taken = obj.max_health - obj.health
                obj.update_ai_fitness(
                    obj.damage_dealt / total_damage - damage_taken / total_health_removed) #-1 is worst, 1 is best
                # X = 2 * (obj.death_time - obj.creation_time) - total_time + obj.damage_dealt/100
                # if X is None:
                #
                #     print(2 * (obj.death_time - obj.creation_time) - total_time + obj.damage_dealt/100,
                #           obj.death_time, obj.creation_time, obj.damage_dealt)
        # print('done')


    def on_update(self, delta_time=None):
        start_time = timeit.default_timer()

        for obj in self.all_objects:
            obj.update()
        for obj in self.all_objects:
            obj_pos_x = obj.body.position.x
            obj_pos_y = obj.body.position.y

            if obj_pos_x < 0: obj_pos_x += self.width
            if obj_pos_x > self.width: obj_pos_x -= self.width
            if obj_pos_y < 0: obj_pos_y += self.height
            if obj_pos_y > self.height: obj_pos_y -= self.height

            obj.body.position = pymunk.Vec2d(obj_pos_x, obj_pos_y)


            # if not ((-20<= obj.x <= self.width+20) and (-20 <= obj.y <= self.height+20)):
            #     if obj in self.fighters:
            #         x_orig = obj.x
            #         y_orig = obj.y
            #         x = max(min(self.width - obj.size, obj.x), obj.size)
            #         y = max(min(self.height - obj.size, obj.y), obj.size)
            #         obj.body.position = pymunk.Vec2d(x,y)
            #         vel_x = obj.body.velocity.x
            #         vel_y = obj.body.velocity.y
            #         if x != x_orig: vel_x = 0
            #         if y != y_orig: vel_y = 0
            #
            #
            #         obj.body.velocity = pymunk.Vec2d(vel_x, vel_y)
            #     else:
            #         self.delete_object(obj)
        self.space.step(1 / FRAMERATE)
        self.sim_time += 1 / FRAMERATE



        # Save the time it took to do this.
        self.shapes_deleted_this_step = set() #remove deleted objects
        self.processing_time = timeit.default_timer() - start_time



class gameWindow(arcade.Window):

    def __init__(self):
        self.simulator = simulator()
        self.draw_time = 0

        width = self.simulator.width
        height = self.simulator.height
        title = 'TEST'
        super().__init__(width, height, title)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self.simulator.register_object(Player_Fighter(300, 300, self.simulator.space, self.simulator))

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        for obj in self.simulator.all_objects:
            obj.on_draw_fn()

        # Draw all the sprites
        for obj in self.simulator.all_objects:
            obj.sprite.draw()
            if isinstance(obj, Fighter_base):
                # arcade.draw_text(str(obj.health), obj.sprite.position[0]-16, obj.sprite.position[1]-12, arcade.color.BLACK, 15)

                arcade.draw_text(str(round(obj.health,1)), obj.x - 16, obj.y - 12, arcade.color.BLACK, 15)
                arcade.draw_text(str(round(obj.shoot_energy, 1)), obj.x - 16, obj.y - 22, arcade.color.BLACK, 15)


        # Draw the lines that aren't sprites
        for line in self.simulator.static_lines:
            body = line.body

            pv1 = body.position + line.a.rotated(body.angle)
            pv2 = body.position + line.b.rotated(body.angle)
            arcade.draw_line(pv1.x, pv1.y, pv2.x, pv2.y, arcade.color.WHITE, 2)

        # Display timings
        output = f"Processing time: {self.simulator.processing_time:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 20, arcade.color.WHITE, 12)

        output = f"Drawing time: {self.draw_time:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 40, arcade.color.WHITE, 12)

        output = f"keys: {self.simulator.keys}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 60, arcade.color.WHITE, 12)

        output = f"num objects: {len(self.simulator.all_objects)}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 80, arcade.color.WHITE, 12)

        self.draw_time = timeit.default_timer() - draw_start_time
    def on_update(self, delta_time: float):
        self.simulator.on_update(delta_time)

    def on_key_press(self, symbol: int, modifiers: int):
        self.simulator.keys.add(symbol)

    def on_key_release(self, symbol: int, modifiers: int):
        self.simulator.keys.remove(symbol)



def main():
    gameWindow()

    arcade.run()


if __name__ == "__main__":
    main()