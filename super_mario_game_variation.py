#!/usr/bin/env python3

##################
# Game Constants #
##################

# other than TILE_SIZE, feel free to step, modify, or delete these constants as
# you see fit.

TILE_SIZE = 128

# 0 movement
GRAVITY = -9
MAX_DOWNWARD_SPEED = 48
PLAYER_JUMP_SPEED = 62
PLAYER_JUMP_DURATION = 3
PLAYER_BORED_THRESHOLD = 60

# horizontal movement
PLAYER_DRAG = 6
PLAYER_MAX_HORIZONTAL_SPEED = 48
PLAYER_HORIZONTAL_ACCELERATION = 16

STORM_LIGHTNING_ROUNDS = 5
STORM_RAIN_ROUNDS = 10

BEE_SPEED = 40
CATERPILLAR_SPEED = 16
PEANUT_SPEED = 60

CHIPMUNK_POWER = 5


# the following maps single-letter strings to the name of the object they
# represent, for use with deserialization in Game.__init__.
SPRITE_MAP = {
    "p": "player",
    "c": "cloud",
    "=": "floor",
    "B": "building",
    "C": "castle",
    "u": "cactus",
    "t": "tree",
    'e': 'bee',
    'f': 'fire',
    '~': 'caterpillar',
    'h': 'helicopter',
    's': 'storm',
    'i': 'chipmunk',
    'w': 'water_wave',
}

STATIC_SPRITE_MAP = {
    "c": "cloud",
    "=": "floor",
    "B": "building",
    "C": "castle",
    "u": "cactus",
    "t": "tree",
}

DYNAMIC_SPRITE_MAP = {
    'e': 'Bee',
    'f': 'Fire',
    '~': 'Caterpillar',
    'h': 'Helicopter',
    'i': 'Chipmunk',
    'w': 'Water_wave',
}


TEXTURE_MAP = {
    'p': 'slight_smile',
    '=': 'black_large_square',
    'c': 'cloud',
    't': 'tree',
    'C': 'castle',
    'u': 'cactus',
    'B': 'classical_building',
    'f': 'fire',
    '~': 'caterpillar',
    'e': 'bee',
    'nut': 'peanut',
    'i': 'chipmunk',
    's': 'thunderstorm',
}

def direction(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

def same_sign(a, b):
    return (a >= 0) == (b >= 0)
##########################
# Classes and Game Logic #
##########################
class Sprite():
    def __init__(self, x, y, sprite, xv = 0, yv = 0):
        self.sprite = sprite
        self.texture = TEXTURE_MAP[sprite]
        self.x = x
        self.y = y
        self.xv = xv
        self.yv = yv
        self.vel = (xv, yv)
        self.dead = False
        self.pos = (self.x, self.y)
    def get_position(self):
        return (self.x, self.y)
    def bounds_check(self):
        return self.pos.y < - TILE_SIZE
    @property
    def rectangle(self):
        return Rectangle(self.x, self.y, TILE_SIZE, TILE_SIZE)
    def __repr__(self):
        return 'Sprite({}, {})'.format(self.texture, self.pos)
    
class Dynamic(Sprite):
    def __init__(self, x, y, xv = 0, yv = 0):
        super().__init__(x, y, xv, yv)
    def update_y(self, acceleration):
        self.yv = max(self.yv + acceleration, -MAX_DOWNWARD_SPEED)
        self.y += self.yv
    def update_x(self, acceleration):
        if self.texture in ['~', 'nut']:
            self.x = self.xv
        self.xv +=  acceleration
        if self.xv > 0:
            drag = -PLAYER_DRAG 
        else: 
            drag = PLAYER_DRAG
        if abs(self.xv) < abs(drag):
            self.xv = 0
        else:
            self.xv +=  drag
        if abs(self.xv) > PLAYER_MAX_HORIZONTAL_SPEED:
            self.xv = direction(self.xv) * PLAYER_MAX_HORIZONTAL_SPEED
        self.x += self.xv
    def update_x_no_drag(self, acceleration = 0):
        self.xv += acceleration
        if abs(self.xv) > PLAYER_MAX_HORIZONTAL_SPEED:
            self.xv = direction(self.xv) * PLAYER_MAX_HORIZONTAL_SPEED
        self.x += self.xv
    # def update_position(self, x, y):
    #     self.pos = (self.x + x, self.y + y)
    def update_velocity(self, jump = False):
        self.vel = (self.xv, self.yv)
        if jump:
            self.vel = (self.xv, PLAYER_JUMP_SPEED + GRAVITY)
    def get_velocity(self):
        return self.vel
    def __repr__(self):
        return 'Dynamic({}, {})'.format(self.texture, self.pos)

class Static(Sprite):
    def __init__(self, x, y, texture):
        super().__init__(x, y, texture)
    def __repr__(self):
        return 'Static({}, {})'.format(self.texture, (self.x, self.y))

class Player(Dynamic):
    def __init__(self, x, y, xv = 0, yv = 0):
        super().__init__(x, y, xv, yv)
        self.player = True
        self.bored_count = 0
    def is_bored(self):
        return self.bored_count > PLAYER_BORED_THRESHOLD
    def __repr__(self):
        return 'Player({}, {})'.format(self.texture, self.pos)

class Bee(Dynamic):
    def __init__(self, x, y, xv = 0, yv = BEE_SPEED):
        super().__init__(x, y, xv, yv)
    def __repr__(self):
        return 'Bee({}, {})'.format(self.texture, self.pos)

class Caterpillar(Dynamic):
    def __init__(self, x, y, xv = CATERPILLAR_SPEED, yv = 0):
        super().__init__(x, y, xv, yv)
    def __repr__(self):
        return 'Caterpillar({}, {})'.format(self.texture, self.pos)

class Chipmunk(Dynamic):
    def __init__(self, x, y, xv = 0, yv = 0):
        super().__init__(x, y, xv, yv)
    def __repr__(self):
        return 'Chipmunk({}, {})'.format(self.texture, self.pos)

class Fire(Dynamic):
    def __init__(self, x, y, xv = 0, yv = 0):
        super().__init__(x, y, xv, yv)
    def __repr__(self):
        return 'Fire({}, {})'.format(self.texture, self.pos)
class Storm(Static):
    def __init__(self, x, y, texture, xv = 0, yv = 0):
        super().__init__(x, y, texture)
    def __repr__(self):
        return 'Storm({}, {})'.format(self.texture, self.pos)



class Rectangle:
    """
    A rectangle object to help with collision detection and resolution.
    """

    def __init__(self, x, y, w, h):
        """
        Initialize a new rectangle.

        `x` and `y` are the coordinates of the bottom-left corner. `w` and `h`
        are the dimensions of the rectangle.
        """
        self.x, self.y, self.w, self.h = x, y, w, h

    def intersects(self, other):
        """
        Check whether `self` and `other` (another Rectangle) overlap.

        Rectangles are open on the top and right sides, and closed on the
        bottom and left sides; concretely, this means that the rectangle
        [0, 0, 1, 1] does not intersect either of [0, 1, 1, 1] or [1, 0, 1, 1].
        """
        return (
            self.x < other.x + other.w and
            self.x + self.w > other.x and
            self.y < other.y + other.h and
            self.y + self.h > other.y
        )
    

    @staticmethod
    def translation_vector(r1, r2):
        """
        Compute how much `r2` needs to step to stop intersecting `r1`.

        If `r2` does not intersect `r1`, return `None`.  Otherwise, return a
        minimal pair `(x, y)` such that translating `r2` by `(x, y)` would
        suppress the overlap. `(x, y)` is minimal in the sense of the "L1"
        distance; in other words, the sum of `abs(x)` and `abs(y)` should be
        as small as possible.

        When two pairs `(x1, y1)` and `(x2, y2)` are tied in terms of this
        metric, return the one whose first element has the smallest
        magnitude.
        """
        if not r1.intersects(r2):
            return None
        else:
            x = min(r1.x + r1.w - r2.x, r1.x - r2.x - r2.w, key=abs)
            y = min(r1.y + r1.h - r2.y, r1.y - r2.y - r2.h, key=abs)
            return (x, 0) if abs(x) < abs(y) else (0, y)

class Game:
    def __init__(self, level_map):
        """
        Initialize a new game, populated with objects from `level_map`.

        `level_map` is a 2D array of 1-character strings; all possible strings
        (and some others) are listed in the SPRITE_MAP dictionary.  Each
        character in `level_map` corresponds to a sprite of size `TILE_SIZE *
        TILE_SIZE`.

        This function is free to store `level_map`'s data however it wants.
        For example, it may choose to just keep a copy of `level_map`; or it
        could choose to read through `level_map` and extract the position of
        each sprite listed in `level_map`.

        Any choice is acceptable, as long as it works with the implementation
        of `timestep` and `render` below.
        """
        self.game, self.dynamic, self.static, self.player = self.make_game(level_map)
        self.status = 'ongoing'
        self.face = 'slight_smile'
        self.idle_count = 0  
        self.jump_count, self.can_jump, self.jumping = 0, True, False
        self.nut_count, self.nuts = 0, []
        self.storm_duration, self.storm, self.thunder, = 0, True, True
        self.dead = False
        
    def timestep(self, keys):
        """
        Simulate the evolution of the game state over one time step.  `keys` is
        a list of currently pressed keys.

        process user input (i.e., adjust the game state based on the keys that are pressed)
        compute any changes in velocities and positions
        resolve any collisions
        """
        # print(keys)
        horizontal_mapping = {'left': -PLAYER_HORIZONTAL_ACCELERATION,
                            'right': PLAYER_HORIZONTAL_ACCELERATION}
        # vertical_mapping = {'up': PLAYER_JUMP_SPEED, down': }
        if self.status != 'ongoing':
            return None
        else:
            if not keys:             
                self.idle_count += 1
                if self.idle_count > PLAYER_BORED_THRESHOLD:
                    self.face = 'sleeping'
            else:
                self.idle_count = 0
                self.face = 'slight_smile'

            temp = 0
            for key in keys:
                # print(key)                
                if key == 'up' and self.can_jump:
                    self.jumping = True
                    self.can_jump = False
                if key in horizontal_mapping:
                    temp += horizontal_mapping[key]
                # if (key == 'x' or key == 'z') and self.nut_count > 0:
                #     self.nut_count -= 1
                #     nut = Dynamic(self.player.x, self.player.y, 'n')
                #     nut.xv = PEANUT_SPEED if key == 'x' else -PEANUT_SPEED
                #     self.game.append(Dynamic(nut))
                #     self.nuts.append(Dynamic(nut))
                #     self.dynamic.append(Dynamic(nut))

            self.jump_helper()
            self.update_helper(temp)
            self.storm_helper()
            self.collision_check()
            


    def jump_helper(self):
        if self.jumping and self.jump_count < PLAYER_JUMP_DURATION:
            self.jump_count += 1
            self.player.yv = PLAYER_JUMP_SPEED
        elif not self.jumping or not self.jump_count < PLAYER_JUMP_DURATION:
            self.jump_count = 0
            self.jumping = False

    def update_helper(self, temp):
        """
        Updates player, nuts, bees, caterpillars, fire, chipmunks
        """
        #player
        self.player.update_x(temp)
        self.player.update_y(GRAVITY)
        #nuts
        # for nut in self.nuts:
        #     nut.update_x(0)
        for sprite in self.dynamic:
            # print(sprite)
            if isinstance(sprite, Bee):
                sprite.update_y(0)
                continue
            elif isinstance(sprite, Caterpillar):
                sprite.update_x_no_drag()
                sprite.update_y(GRAVITY)
                # sprite.update_y(GRAVITY)
                continue
            # sprite.update_x(0)
            sprite.update_y(GRAVITY)
            # print(sprite.y)
       
    def storm_helper(self):
        self.storm_duration += 1
        # print(self.storm_duration)
        if self.storm_duration == STORM_LIGHTNING_ROUNDS and self.thunder:
            self.thunder = False
            # print(self.thunder)
            self.storm_duration = 0

        elif self.storm_duration == STORM_RAIN_ROUNDS and not self.thunder:
            self.thunder = True
            self.storm_duration = 0

    def collision_check(self):
        """
        checks for collisions, first with y, then with x
        """
        #y col
        for sprite in self.static:
            if not sprite.dead:
                # for nut in self.nuts:
                #     if not nut.dead:
                #         if sprite.rectangle.intersects(nut.rectangle):
                #             nut.dead = True
                for dyn in self.dynamic:
                    # print(dyn)
                    if sprite is dyn or dyn.dead:
                        continue
                    if sprite.rectangle.intersects(dyn.rectangle):
                        step = Rectangle.translation_vector(sprite.rectangle, dyn.rectangle)
                        if isinstance(dyn, Bee):
                            dyn.yv = -dyn.yv
                            dyn.y += step[1]
                        if isinstance(dyn, Fire):
                            # self.check_game_state(sprite.texture)
                            # dyn.yv = 0
                            # print(sprite, dyn)
                            dyn.y += step[1]
                            if isinstance(sprite, (Player, Caterpillar)):
                                sprite.dead = True
                        if isinstance(dyn, Chipmunk):
                            # self.check_game_state(sprite.texture)
                            dyn.yv = 0
                            dyn.y += step[1]
                            if isinstance(sprite, Player):
                                dyn.dead = True
                        if isinstance(dyn, Caterpillar):
                            # self.check_game_state(sprite.texture)
                            # print(dyn.xv)
                            if step[0] == 0:
                                dyn.yv = 0
                            if step[1] == 0:
                                dyn.xv = -dyn.xv
                            dyn.y += step[1]
                            dyn.x += step[0]
                if sprite.rectangle.intersects(self.player.rectangle) and not isinstance(sprite, Player):
                    self.check_game_state(sprite.texture)
                    step = Rectangle.translation_vector(sprite.rectangle, self.player.rectangle)
                    ystep = step[1]
                    if ystep != 0 and not same_sign(ystep, self.player.yv):
                        self.player.yv = 0
                        self.can_jump = True
                        self.player.y += ystep

        #xcol
        for sprite in self.static:
            if not sprite.dead:
                for dyn in self.dynamic:
                    if sprite is dyn or dyn.dead:
                        continue
                    if sprite.rectangle.intersects(dyn.rectangle):
                        step = Rectangle.translation_vector(sprite.rectangle, dyn.rectangle)
                        if isinstance(dyn, Caterpillar):
                            # self.check_game_state(sprite.texture)
                            if step[0] == 0:
                                dyn.yv = 0
                            if step[1] == 0:
                                dyn.xv = -dyn.xv
                        dyn.y += step[1]
                        dyn.x += step[0]

                if sprite.rectangle.intersects(self.player.rectangle) and not isinstance(sprite, Player):
                    self.check_game_state(sprite.texture)
                    step = Rectangle.translation_vector(sprite.rectangle, self.player.rectangle)
                    xstep = step[0]
                    if xstep != 0 and not same_sign(xstep, self.player.xv):
                        self.player.xv = 0
                        self.player.x += xstep

        #dynamic cols
        for sprite in self.dynamic:
            if not sprite.dead:
                if isinstance(sprite, (Bee, Fire)):
                    if sprite.rectangle.intersects(self.player.rectangle):
                        self.check_game_state(sprite.texture)
                if isinstance(sprite, Caterpillar):
                    step = Rectangle.translation_vector(sprite.rectangle, self.player.rectangle)
                    if step:
                        if step[1] > 0:
                            sprite.dead = True
                        else:
                            self.player.dead = True
                            self.status = 'defeat'
                            self.face = 'injured'
                    for fire in self.dynamic:
                        if isinstance(fire, Fire):
                            if sprite.rectangle.intersects(fire.rectangle):
                                sprite.dead = True
                                
                            

        
    def check_game_state(self, intersect = None):
        """
        Changes game state and player texture based on the intersecting sprite
        """
        if intersect == 'cactus' or self.player.y < -TILE_SIZE or (intersect == 'thunderstorm' and self.thunder) or intersect == 'fire' or intersect == 'bee':
            self.status = 'defeat'
            self.face = 'injured'
        if intersect == 'castle':
            self.status = 'victory'
            self.face = 'partying_face'

    def make_game(self, level_map):
        """
        Given a level map, returns a dictionary with all the sprite, location values
        in the form:

        {
            'player': (x, y),
            'floor': [(x, y), (x, y), ...],
        }
        """
        game_object_list = []
        dynamic_list = []
        static_list = []
        y = -TILE_SIZE
        for line in range(len(level_map)-1, -1, -1):
            y += TILE_SIZE
            x = -TILE_SIZE
            for sprite in level_map[line]:
                x += TILE_SIZE
                if sprite == 'p':
                    player = (Player(x, y, sprite))
                    game_object_list.append(player)
                elif sprite == 's':
                    storm = Storm(x, y, sprite)
                    game_object_list.append(storm)
                    static_list.append(storm)
                    self.storm = True
                elif sprite in STATIC_SPRITE_MAP:
                    static = Static(x, y, sprite)
                    game_object_list.append(static)
                    static_list.append(static)
                elif sprite in DYNAMIC_SPRITE_MAP:
                    #append the sprite as a class object of itself
                    # Class = DYNAMIC_SPRITE_MAP[sprite]
                    # Class()
                    # game_object_list.append(Class(x, y, sprite))
                    #this didn't work because it was creating a new instance of the class
                    #and not appending the instance to the list
                    if sprite == 'e':
                        bee = Bee(x, y, sprite)
                        bee.yv = BEE_SPEED
                        game_object_list.append(bee)
                        dynamic_list.append(bee)
                    if sprite == '~':
                        cat = Caterpillar(x, y, sprite)
                        cat.xv = CATERPILLAR_SPEED
                        game_object_list.append(cat)
                        dynamic_list.append(cat)
                    if sprite == 'f':
                        fire = Fire(x, y, sprite)
                        game_object_list.append(fire)
                        dynamic_list.append(fire)
                    if sprite == 'i':
                        chip = Chipmunk(x, y, sprite)
                        game_object_list.append(chip)
                        dynamic_list.append(chip)

        return game_object_list, dynamic_list, static_list, player
            
    def render(self, w, h):
        """
        Report status and list of sprite dictionaries for sprites with a
        horizontal distance of w//2 from player.  See writeup for details.
        
        Game.render(w, h) to return a tuple of two values:

        A string indicating the state of the game ("ongoing", "victory", or "defeat"). To start with, the status is always "ongoing" (though that will change later in the lab).

        A list of sprites, stored as dictionaries of the following form:

        {
            'texture': 'slight_smile', # a string representing the texture to be used
            'pos': (512, 128),  # the (x, y) position of the sprite's lower-left corner
            'player': True, # boolean indicating if this sprite represents the player
        }

        """
        
        sprite_list = []
        # print(1)
        boundary = Rectangle(self.player.x-w//2, 0, w, h)
        # print(w, h)
        self.check_game_state()
        if -TILE_SIZE < self.player.y < h:
            sprite_list.append({'texture': self.face, 'pos': (self.player.x, self.player.y), 'player': True})
        for sprite in self.game:
            # print(sprite)
            if not sprite.dead:
                if sprite.rectangle.intersects(boundary) and not isinstance(sprite, Player):
                    # print(sprite)
                    if isinstance(sprite, Storm):
                        if self.thunder:
                            # print('h')
                            sprite_list.append({'texture': 'thunderstorm', 'pos': (sprite.x, sprite.y), 'player': False})
                        else:
                            # print('f')
                            sprite_list.append({'texture': 'rainy', 'pos': (sprite.x, sprite.y), 'player': False})
                    else:
                        sprite_list.append({'texture': sprite.texture, 'pos': (sprite.x, sprite.y), 'player': False})
        # print(sprite_list)
        return (self.status, sprite_list)
        



        


if __name__ == "__main__":
    pass