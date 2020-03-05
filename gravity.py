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

SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Pymunk test"


class PhysicsSprite(arcade.Sprite):
    def __init__(self, pymunk_shape, filename):
        super().__init__(filename, center_x=pymunk_shape.body.position.x, center_y=pymunk_shape.body.position.y)
        self.pymunk_shape = pymunk_shape
    def grav_pull(self, space):
        x = self.pymunk_shape.body.position.x
        y = self.pymunk_shape.body.position.y
        shape_list = space.point_query((x, y), 1550, pymunk.ShapeFilter())
        my_mass = self.pymunk_shape.body.mass

        for pqi in shape_list:
            shape = pqi.shape
            dx = shape.body.position.x - x
            dy = shape.body.position.y - y
            other_mass = shape.body.mass
            mag = math.sqrt(dx ** 2 + dy ** 2)
            if mag == 0: continue
            mag /= 30

            force = my_mass * other_mass * 10 / (mag ** 2) * 5
            dx /= mag
            dy /= mag
            dx *= force
            dy *= force

            shape.body.apply_force_at_world_point((-dx, -dy), (x, y))  # , point=pymunk.Vec2d(x,y))


class CircleSprite(PhysicsSprite):
    def __init__(self, pymunk_shape, filename):
        super().__init__(pymunk_shape, filename)
        self.width = pymunk_shape.radius * 4
        self.height = pymunk_shape.radius * 4


class BoxSprite(PhysicsSprite):
    def __init__(self, pymunk_shape, filename, width, height):
        super().__init__(pymunk_shape, filename)
        self.width = width
        self.height = height


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        # -- Pymunk
        self.space = pymunk.Space()
        self.space.iterations = 35
        self.space.gravity = (0.0, 0)#-900.0)

        # Lists of sprites or lines
        self.sprite_list: arcade.SpriteList[PhysicsSprite] = arcade.SpriteList()
        self.static_lines = []

        # Used for dragging shapes around with the mouse
        self.shape_being_dragged = None
        self.last_mouse_position = 0, 0

        self.draw_time = 0
        self.processing_time = 0

        # Create the floor
        floor_height = 80
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        shape = pymunk.Segment(body, [0, floor_height], [SCREEN_WIDTH, floor_height], 0.0)
        shape.friction = 10
        self.space.add(shape)
        self.static_lines.append(shape)


        size = 32
        mass = 1
        x = 500 + 160
        y = (floor_height + size / 2) + 32*5

        for xm, ym, mass in ((0,0, 1), (0, 400, 6), (400, 0, 1)):

            moment = pymunk.moment_for_circle(mass, 0, 32, (0, 0))
            body = pymunk.Body(mass, moment)
            body.position = pymunk.Vec2d(x+xm, y+ym)
            shape = pymunk.Circle(body, 32, pymunk.Vec2d(0, 0))
            shape.elasticity = .99#0.2
            shape.friction = 0*0.9
            self.space.add(body, shape)
            sprite = CircleSprite(shape, ":resources:images/items/coinGold.png")
            self.sprite_list.append(sprite)


    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        # Draw all the sprites
        self.sprite_list.draw()

        # Draw the lines that aren't sprites
        for line in self.static_lines:
            body = line.body

            pv1 = body.position + line.a.rotated(body.angle)
            pv2 = body.position + line.b.rotated(body.angle)
            arcade.draw_line(pv1.x, pv1.y, pv2.x, pv2.y, arcade.color.WHITE, 2)

        # Display timings
        output = f"Processing time: {self.processing_time:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 20, arcade.color.WHITE, 12)

        output = f"Drawing time: {self.draw_time:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 40, arcade.color.WHITE, 12)

        self.draw_time = timeit.default_timer() - draw_start_time

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            # Create the stacks of boxes
            for row in range(5):
                for column in range(5):
                    size = 32
                    mass = 1.0
                    X = x + (column - 2.5) * 32
                    Y = y + (row - 2.5) * 32

                    moment = pymunk.moment_for_circle(mass, 0, 32, (0, 0))
                    body = pymunk.Body(mass, moment)
                    body.position = pymunk.Vec2d(X, Y)
                    shape = pymunk.Circle(body, 32, pymunk.Vec2d(0, 0))
                    shape.elasticity = 0.2
                    shape.friction = 0.9
                    self.space.add(body, shape)
                    # body.sleep()

                    sprite = CircleSprite(shape, ":resources:images/items/coinGold.png")
                    self.sprite_list.append(sprite)
            # self.last_mouse_position = x, y
            # # See if we clicked on anything
            # shape_list = self.space.point_query((x, y), 1, pymunk.ShapeFilter())
            #
            # # If we did, remember what we clicked on
            # if len(shape_list) > 0:
            #     self.shape_being_dragged = shape_list[0]

        elif button == arcade.MOUSE_BUTTON_RIGHT:

            shape_list = self.space.point_query((x,y), 100, pymunk.ShapeFilter())

            for pqi in shape_list:
                shape = pqi.shape
                dx = shape.body.position.x - x
                dy = shape.body.position.y - y
                mag = math.sqrt(dx**2 + dy ** 2)/2000
                dx /= mag
                dy /= mag
                shape.body.apply_impulse_at_world_point((dx,dy), (x,y))#, point=pymunk.Vec2d(x,y))

            # # With right mouse button, shoot a heavy coin fast.
            # mass = 1200
            # radius = 40
            # inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
            # body = pymunk.Body(mass, inertia)
            # body.position = x, y
            # body.velocity = 2000, 0
            # shape = pymunk.Circle(body, radius, pymunk.Vec2d(0, 0))
            # shape.friction = 0.3
            # self.space.add(body, shape)
            #
            # sprite = CircleSprite(shape, ":resources:images/items/coinGold.png")
            # self.sprite_list.append(sprite)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            # Release the item we are holding (if any)
            self.shape_being_dragged = None

    def on_mouse_motion(self, x, y, dx, dy):
        if self.shape_being_dragged is not None:
            # If we are holding an object, move it with the mouse
            self.last_mouse_position = x, y
            self.shape_being_dragged.shape.body.position = self.last_mouse_position
            self.shape_being_dragged.shape.body.velocity = dx * 20, dy * 20

    def on_update(self, delta_time):
        start_time = timeit.default_timer()

        # Check for balls that fall off the screen
        for sprite in self.sprite_list:
            if max(abs(sprite.pymunk_shape.body.position.y), abs(sprite.pymunk_shape.body.position.x)) > 2000:
                # Remove balls from physics space
                self.space.remove(sprite.pymunk_shape, sprite.pymunk_shape.body)
                # Remove balls from physics list
                sprite.remove_from_sprite_lists()
            sprite.grav_pull(self.space)
        # Update physics
        # Use a constant time step, don't use delta_time
        # See "Game loop / moving time forward"
        # http://www.pymunk.org/en/latest/overview.html#game-loop-moving-time-forward
        self.space.step(1 / 120.0)

        # If we are dragging an object, make sure it stays with the mouse. Otherwise
        # gravity will drag it down.
        if self.shape_being_dragged is not None:
            self.shape_being_dragged.shape.body.position = self.last_mouse_position
            self.shape_being_dragged.shape.body.velocity = 0, 0

        # Move sprites to where physics objects are
        import random
        for sprite in self.sprite_list:
            sprite.center_x = sprite.pymunk_shape.body.position.x
            sprite.center_y = sprite.pymunk_shape.body.position.y
            sprite.angle = math.degrees(sprite.pymunk_shape.body.angle)

        # Save the time it took to do this.
        self.processing_time = timeit.default_timer() - start_time


def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

    arcade.run()


if __name__ == "__main__":
    main()