"""In-Built Player System for making game in a 1 - 10 lines"""

## pysick/ep.py

import pysick
import pysick.keys as keys
import pysick.clock
import random
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

#===================Constants======================

epAdvanced = 'X_EP_ADVANCED<>3D'
epEnableDt = 'X_DELTA_TIME$ACTIVE'
epCameraFix = False
CAMERA_POS = [0, 30, 100]  # Camera z should be far from terrain
CAMERA_ROT = [30, 0]       # Look angle (up/down, left/right)



'''CLASSES'''

#===================class-1========================
class epBasePlayerController:
    """Creates a basic player controller"""
    def __init__(self, ):

        self.position = [0, 0]
        self.player_weight = [50, 50]
        self.player_color = (255, 0, 0)
        self.player_speed = 5
        self.jumping = False  # Track whether player is jumping

        self.player = pysick.graphics.Rect(self.position[0],
                                           self.position[1],
                                           self.player_weight[0],
                                           self.player_weight[1],
                                           self.player_color
                                           )

    def change_sprite(self, x, y, width, height):
        self.position = [x, y]
        self.player_weight = [width, height]

    def change_color(self, color):
        self.player_color = color

    def change_speed(self, speed):
        self.player_speed = speed

    def update_sprite(self):

        self.player = pysick.graphics.Rect(self.position[0],
                                           self.position[1],
                                           self.player_weight[0],
                                           self.player_weight[1],
                                           self.player_color
                                           )

    def update_binds(self):

        keys.init()

        if keys.is_pressed(keys.KEY_S):
            self.position[1] += self.player_speed
        if keys.is_pressed(keys.KEY_W):
            self.position[1] -= self.player_speed
        if keys.is_pressed(keys.KEY_D):
            self.position[0] += self.player_speed
        if keys.is_pressed(keys.KEY_A):
            self.position[0] -= self.player_speed

    def upload_sprite(self):
        pysick.graphics.draw(self.player)

    def loop(self, ms):


        self.update_binds()
        self.update_sprite()
        self.upload_sprite()

        pysick.clock.tick(ms)

        self.loop(ms)

class epAdvancedPlayerController:
    def __init__(self):
        self.position = [100, 100]
        self.size = [50, 50]
        self.color = (255, 0, 0)
        self.jumping = False

        self.velocity = [0, 0]
        self.acceleration = [0, 0]

        self.gravity = 1
        self.jump_power = -15
        self.on_ground = False

        self.max_speed = 10

        self.controls = {
            "left": keys.KEY_A,
            "right": keys.KEY_D,
            "up": keys.KEY_W,
            "down": keys.KEY_S,
            "jump": keys.KEY_SPACE,
        }

        self.player = pysick.graphics.Rect(
            self.position[0], self.position[1],
            self.size[0], self.size[1],
            self.color
        )

    def set_position(self, x, y):
        self.position = [x, y]

    def set_size(self, width, height):
        self.size = [width, height]

    def set_color(self, color):
        self.color = color

    def set_controls(self, control_dict):
        self.controls.update(control_dict)

    def update_input(self):
        if keys.is_pressed(self.controls["left"]):
            self.velocity[0] = -self.max_speed
        elif keys.is_pressed(self.controls["right"]):
            self.velocity[0] = self.max_speed
        else:
            self.velocity[0] = 0

        # Jump (one-time per press, only if on ground)
        if keys.was_pressed(self.controls["jump"]) and self.on_ground:
            self.velocity[1] = self.jump_power
            self.on_ground = False
            self.jumping = True

    def update_physics(self):
        # Gravity (apply only if in air)
        if not self.on_ground:
            self.velocity[1] += self.gravity
            self.velocity[1] = min(self.velocity[1], self.max_speed)

        # Apply velocity
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]

        # Clamp within window bounds
        win_w, win_h = pysick.ingine.width, pysick.ingine.height

        self.position[0] = max(0, min(self.position[0], win_w - self.size[0]))
        self.position[1] = max(0, min(self.position[1], win_h - self.size[1]))

        # Ground collision
        if self.position[1] >= win_h - self.size[1]:
            self.position[1] = win_h - self.size[1]
            self.velocity[1] = 0
            self.on_ground = True
            self.jumping = False

    def update_sprite(self):
        self.player.x = self.position[0]
        self.player.y = self.position[1]
        self.player.width = self.size[0]
        self.player.height = self.size[1]
        self.player.fill = self.color

    def upload_sprite(self):
        pysick.graphics.draw(self.player)

    def loop(self, ms):
        keys.init()
        while not pysick.QUIT:
            pysick.graphics.fill_screen((20, 20, 20))  # clear background

            self.update_input()
            self.update_physics()
            self.update_sprite()
            self.upload_sprite()

            pysick.ingine.slap()
            pysick.clock.tick(ms)



class epBaseTwoPlayerController:
    def __init__(self):
        # Player 1 properties
        self.p1_pos = [100, 100]
        self.p1_size = [50, 50]
        self.p1_color = (255, 0, 0)
        self.p1_speed = 5
        self.p1_keys = {
            "up": keys.KEY_W,
            "down": keys.KEY_S,
            "left": keys.KEY_A,
            "right": keys.KEY_D
        }

        # Player 2 properties
        self.p2_pos = [600, 100]
        self.p2_size = [50, 50]
        self.p2_color = (0, 0, 255)
        self.p2_speed = 5
        self.p2_keys = {
            "up": keys.KEY_UP,
            "down": keys.KEY_DOWN,
            "left": keys.KEY_LEFT,
            "right": keys.KEY_RIGHT
        }

        # Sprites
        self.p1 = pysick.graphics.Rect(*self.p1_pos, *self.p1_size, self.p1_color)
        self.p2 = pysick.graphics.Rect(*self.p2_pos, *self.p2_size, self.p2_color)

        keys.init()

    def move_player(self, pos, keymap, speed):
        if keys.is_pressed(keymap["up"]):
            pos[1] -= speed
        if keys.is_pressed(keymap["down"]):
            pos[1] += speed
        if keys.is_pressed(keymap["left"]):
            pos[0] -= speed
        if keys.is_pressed(keymap["right"]):
            pos[0] += speed

    def update_sprites(self):
        self.p1.x, self.p1.y = self.p1_pos
        self.p2.x, self.p2.y = self.p2_pos

    def draw_players(self):
        pysick.graphics.draw(self.p1)
        pysick.graphics.draw(self.p2)

    def loop(self, ms=30):
        while not pysick.QUIT:
            pysick.graphics.fill_screen((20, 20, 20))

            # Move both players
            self.move_player(self.p1_pos, self.p1_keys, self.p1_speed)
            self.move_player(self.p2_pos, self.p2_keys, self.p2_speed)

            # Update and draw
            self.update_sprites()
            self.draw_players()

            pysick.ingine.slap()
            pysick.clock.tick(ms)



class epBaseTwoPlayerShooter:
    def __init__(self):
        # Player 1 setup
        self.p1_pos = [100, 250]
        self.p1_size = [50, 50]
        self.p1_color = (255, 0, 0)
        self.p1_keys = {
            "up": keys.KEY_W,
            "down": keys.KEY_S,
            "left": keys.KEY_A,
            "right": keys.KEY_D,
            "shoot": keys.KEY_SPACE,
        }

        # Player 2 setup
        self.p2_pos = [600, 250]
        self.p2_size = [50, 50]
        self.p2_color = (0, 0, 255)
        self.p2_keys = {
            "up": keys.KEY_UP,
            "down": keys.KEY_DOWN,
            "left": keys.KEY_LEFT,
            "right": keys.KEY_RIGHT,
            "shoot": keys.KEY_RETURN,
        }

        # Sprites
        self.p1 = pysick.graphics.Rect(*self.p1_pos, *self.p1_size, self.p1_color)
        self.p2 = pysick.graphics.Rect(*self.p2_pos, *self.p2_size, self.p2_color)

        # Bullets
        self.p1_bullets = []
        self.p2_bullets = []

        # Scores
        self.p1_score = 0
        self.p2_score = 0

        # Labels
        self.score1_label = pysick.ingine.add_label("P1: 0", 20, 20)
        self.score2_label = pysick.ingine.add_label("P2: 0", 700, 20)

        keys.init()

    def move(self, pos, controls):
        if keys.is_pressed(controls["up"]):    pos[1] -= 5
        if keys.is_pressed(controls["down"]):  pos[1] += 5
        if keys.is_pressed(controls["left"]):  pos[0] -= 5
        if keys.is_pressed(controls["right"]): pos[0] += 5

    def shoot(self):
        if keys.was_pressed(self.p1_keys["shoot"]):
            bullet = pysick.graphics.Rect(
                self.p1.x + self.p1_size[0],
                self.p1.y + self.p1_size[1] // 2 - 5,
                10, 10, (255, 0, 0)
            )
            self.p1_bullets.append(bullet)

        if keys.was_pressed(self.p2_keys["shoot"]):
            bullet = pysick.graphics.Rect(
                self.p2.x - 10,
                self.p2.y + self.p2_size[1] // 2 - 5,
                10, 10, (0, 0, 255)
            )
            self.p2_bullets.append(bullet)

    def update_bullets(self):
        for bullet in self.p1_bullets[:]:
            bullet.x += 10
            if bullet.x > 800:
                self.p1_bullets.remove(bullet)
            elif pysick.colliCheck.rectxrect(bullet, self.p2):
                self.p1_score += 1
                self.p1_bullets.remove(bullet)

        for bullet in self.p2_bullets[:]:
            bullet.x -= 10
            if bullet.x < 0:
                self.p2_bullets.remove(bullet)
            elif pysick.colliCheck.rectxrect(bullet, self.p1):
                self.p2_score += 1
                self.p2_bullets.remove(bullet)

    def draw_all(self):
        pysick.graphics.draw(self.p1)
        pysick.graphics.draw(self.p2)

        for b in self.p1_bullets:
            pysick.graphics.draw(b)

        for b in self.p2_bullets:
            pysick.graphics.draw(b)

        self.score1_label["text"] = f"P1: {self.p1_score}"
        self.score2_label["text"] = f"P2: {self.p2_score}"

    def loop(self, ms=30):
        while not pysick.QUIT:
            pysick.graphics.fill_screen((20, 20, 20))

            self.move(self.p1_pos, self.p1_keys)
            self.move(self.p2_pos, self.p2_keys)

            self.p1.x, self.p1.y = self.p1_pos
            self.p2.x, self.p2.y = self.p2_pos

            self.shoot()
            self.update_bullets()
            self.draw_all()

            pysick.ingine.slap()
            pysick.clock.tick(ms)



class epBaseSpaceShooter:
    def __init__(self):
        self.player_pos = [375, 500]
        self.player_size = [50, 50]
        self.player_color = (0, 255, 255)

        self.player = pysick.graphics.Rect(
            self.player_pos[0], self.player_pos[1],
            self.player_size[0], self.player_size[1],
            self.player_color
        )

        self.bullets = []
        self.enemies = []
        self.score = 0
        self.game_over = False

        self.score_label = pysick.gui.add_label("Score: 0", 20, 20)

        keys.init()

    def handle_input(self):
        if keys.is_pressed(keys.KEY_LEFT):
            self.player_pos[0] -= 7
        if keys.is_pressed(keys.KEY_RIGHT):
            self.player_pos[0] += 7
        if keys.was_pressed(keys.KEY_SPACE):
            self.shoot()

        # Clamp within screen
        self.player_pos[0] = max(0, min(self.player_pos[0], 800 - self.player_size[0]))

    def shoot(self):
        bullet = pysick.graphics.Rect(
            self.player.x + self.player_size[0] // 2 - 5,
            self.player.y,
            10, 20,
            (255, 255, 0)
        )
        self.bullets.append(bullet)

    def spawn_enemy(self):
        if random.random() < 0.05:
            x = random.randint(0, 750)
            enemy = pysick.graphics.Rect(x, -50, 50, 50, (255, 0, 0))
            self.enemies.append(enemy)

    def update_bullets(self):
        for b in self.bullets[:]:
            b.y -= 15
            if b.y < 0:
                self.bullets.remove(b)

    def update_enemies(self):
        for e in self.enemies[:]:
            e.y += 5
            if e.y > 600:
                self.enemies.remove(e)

            if pysick.colliCheck.rectxrect(e, self.player):
                self.game_over = True

        # Bullet collision with enemies
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if pysick.colliCheck.rectxrect(bullet, enemy):
                    self.enemies.remove(enemy)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    self.score += 1
                    break

    def draw_all(self):
        pysick.graphics.draw(self.player)
        for b in self.bullets:
            pysick.graphics.draw(b)
        for e in self.enemies:
            pysick.graphics.draw(e)
        self.score_label["text"] = f"Score: {self.score}"

    def loop(self, ms=30):
        while not pysick.QUIT and not self.game_over:
            pysick.graphics.fill_screen((0, 0, 20))

            self.handle_input()
            self.spawn_enemy()
            self.update_bullets()
            self.update_enemies()

            self.player.x = self.player_pos[0]
            self.player.y = self.player_pos[1]

            self.draw_all()

            pysick.ingine.slap()
            pysick.clock.tick(ms)

        if self.game_over:
            pysick.message_box.show_info("Game Over", f"Final Score: {self.score}")


class epBaseArc:
    def __init__(self, x=100, y=100, width=50, height=50, start=0, extent=90, color=(0, 0, 255)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.start = start
        self.extent = extent
        self.color = color

        self._arc = {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "start": self.start,
            "extent": self.extent,
            "fill": self.color,
        }

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self._arc["x"] = x
        self._arc["y"] = y

    def set_size(self, width, height):
        self.width = width
        self.height = height
        self._arc["width"] = width
        self._arc["height"] = height

    def set_color(self, color):
        self.color = color
        self._arc["fill"] = color

    def set_angles(self, start, extent):
        self.start = start
        self.extent = extent
        self._arc["start"] = start
        self._arc["extent"] = extent

    def draw(self):
        epBaseDraw.arc(self)

class epBaseLine:
    def __init__(self, x1, y1, x2, y2, color=(0, 0, 0)):
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.color = color

    def draw(self):
        epBaseDraw.line(self)

class epBasePolygon:
    def __init__(self, points, color=(0, 0, 0)):
        self.points = points  # list of (x, y)
        self.color = color

    def draw(self):
        epBaseDraw.polygon(self)

class epBaseText:
    def __init__(self, x, y, text, font=("Arial", 14), color=(0, 0, 0), anchor="nw"):
        self.x, self.y = x, y
        self.text = text
        self.font = font
        self.color = color
        self.anchor = anchor

    def draw(self):
        epBaseDraw.text(self)

class epBaseCircle:
    def __init__(self, x, y, radius, color=(0, 0, 0)):
        self.x, self.y = x, y
        self.radius = radius
        self.color = color

    def draw(self):
        epBaseDraw.circle(self)

class epBaseOval:
    def __init__(self, x, y, width, height, color=(0, 0, 0)):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.color = color

    def draw(self):
        epBaseDraw.oval(self)

class epBaseDraw:
    @staticmethod
    def arc(arc):
        canvas = pysick.ingine._get_canvas()
        fill = pysick._color_to_hex(arc.color)
        canvas.create_arc(arc.x, arc.y, arc.x + arc.width, arc.y + arc.height,
                          start=arc.start, extent=arc.extent, fill=fill)

    @staticmethod
    def line(line):
        canvas = pysick.ingine._get_canvas()
        fill = pysick._color_to_hex(line.color)
        canvas.create_line(line.x1, line.y1, line.x2, line.y2, fill=fill)

    @staticmethod
    def polygon(poly):
        canvas = pysick.ingine._get_canvas()
        fill = pysick._color_to_hex(poly.color)
        points = [coord for point in poly.points for coord in point]
        canvas.create_polygon(points, fill=fill)

    @staticmethod
    def text(txt):
        canvas = pysick.ingine._get_canvas()
        fill = pysick._color_to_hex(txt.color)
        canvas.create_text(txt.x, txt.y, text=txt.text, font=txt.font,
                           fill=fill, anchor=txt.anchor)

    @staticmethod
    def circle(circle):
        canvas = pysick.ingine._get_canvas()
        fill = pysick._color_to_hex(circle.color)
        x, y, r = circle.x, circle.y, circle.radius
        canvas.create_oval(x - r, y - r, x + r, y + r, fill=fill)

    @staticmethod
    def oval(oval):
        canvas = pysick.ingine._get_canvas()
        fill = pysick._color_to_hex(oval.color)
        canvas.create_oval(oval.x, oval.y, oval.x + oval.width,
                           oval.y + oval.height, fill=fill)




class epAdvancedCube:
    def __init__(self, x, y, z, size, color=(1, 1, 1), rotation=(0, 0, 0)):
        self.position = [x, y, z]
        self.size = size
        self.color = color  # RGB 0.0 - 1.0
        self.rotation = rotation  # (rx, ry, rz) in degrees

    def draw(self):
        if not _ENABLE_ADVANCED: return
        x, y, z = self.position
        s = self.size / 2
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        glColor3f(*self.color)
        glutSolidCube(self.size)
        glPopMatrix()



class epAdvancedCuboid:
    def __init__(self, x, y, z, width, height, depth, color=(1, 1, 1), rotation=(0, 0, 0)):
        self.position = [x, y, z]
        self.size = [width, height, depth]
        self.color = color
        self.rotation = rotation

    def draw(self):
        if not _ENABLE_ADVANCED: return
        x, y, z = self.position
        w, h, d = self.size
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        glScalef(w, h, d)
        glColor3f(*self.color)
        glutSolidCube(1)  # Scale makes this a cuboid
        glPopMatrix()



class epBaseTerrain:
    def __init__(self, gravity=1, jump_power=-15, player_color=(0, 200, 255)):
        self.gravity = gravity
        self.jump_power = jump_power

        # Player state
        self.player_pos = [100, 100]
        self.player_size = [50, 50]
        self.velocity = [0, 0]
        self.on_ground = False

        self.player = pysick.graphics.Rect(*self.player_pos, *self.player_size, player_color)

        # Terrain blocks
        self.blocks = [
            pysick.graphics.Rect(0, 550, 800, 50, (100, 100, 100)),  # ground
            pysick.graphics.Rect(200, 450, 100, 20, (100, 100, 100)),
            pysick.graphics.Rect(400, 350, 100, 20, (100, 100, 100)),
            pysick.graphics.Rect(600, 250, 100, 20, (100, 100, 100)),
        ]

        keys.init()

    def update_input(self):
        speed = 5
        if keys.is_pressed(keys.KEY_A):
            self.player_pos[0] -= speed
        if keys.is_pressed(keys.KEY_D):
            self.player_pos[0] += speed
        if keys.was_pressed(keys.KEY_SPACE) and self.on_ground:
            self.velocity[1] = self.jump_power
            self.on_ground = False

    def apply_physics(self):
        self.velocity[1] += self.gravity
        self.player_pos[1] += self.velocity[1]

        # Simple floor collision
        self.on_ground = False
        for block in self.blocks:
            if pysick.colliCheck.rectxrect(self.player, block):
                if self.velocity[1] > 0:  # falling
                    self.player_pos[1] = block.y - self.player_size[1]
                    self.velocity[1] = 0
                    self.on_ground = True

    def draw_all(self):
        pysick.graphics.draw(self.player)
        for block in self.blocks:
            pysick.graphics.draw(block)

    def loop(self, ms=30):
        while not pysick.QUIT:
            pysick.graphics.fill_screen((20, 20, 30))

            self.update_input()
            self.apply_physics()

            self.player.x, self.player.y = self.player_pos
            self.draw_all()

            pysick.ingine.slap()
            pysick.clock.tick(ms)


class epAdvancedTerrain:
    def __init__(self, width=10, depth=10, block_size=5):
        self.width = width
        self.depth = depth
        self.block_size = block_size
        self.terrain = []  # List of (x, y, z, height)

        self.generate_heightmap()

        self.player_pos = [0, 10, 0]
        self.player_velocity = [0, 0, 0]
        self.gravity = -0.3
        self.grounded = False

    def generate_heightmap(self):
        for x in range(self.width):
            for z in range(self.depth):
                height = random.randint(1, 4)
                self.terrain.append((x, height, z, height))

    def update_physics(self):
        # Apply gravity
        if not self.grounded:
            self.player_velocity[1] += self.gravity
        else:
            self.player_velocity[1] = 0

        # Apply velocity
        self.player_pos[1] += self.player_velocity[1]

        # Check collision with terrain blocks (simplified ground check)
        if self.player_pos[1] <= self.block_size * 2:
            self.player_pos[1] = self.block_size * 2
            self.grounded = True
        else:
            self.grounded = False

    def draw_block(self, x, y, z, h):
        if not _ENABLE_ADVANCED:
            return
        s = self.block_size
        glPushMatrix()
        glTranslatef(x * s, h * s / 2, z * s)
        glScalef(s, h * s, s)
        glColor3f(0.3 + 0.05 * h, 0.7 - 0.05 * h, 0.2)
        glutSolidCube(1)
        glPopMatrix()

    def draw_player(self):
        if not _ENABLE_ADVANCED:
            return
        glPushMatrix()
        glTranslatef(*self.player_pos)
        glColor3f(1, 0, 0)
        glutSolidCube(self.block_size)
        glPopMatrix()

    def render(self):
        if not _ENABLE_ADVANCED:
            return

        # Set camera
        glLoadIdentity()
        gluLookAt(
            CAMERA_POS[0], CAMERA_POS[1], CAMERA_POS[2],
            0, 0, 0,
            0, 1, 0
        )

        # Draw terrain
        for x, y, z, h in self.terrain:
            self.draw_block(x, y, z, h)

        # Draw player
        self.draw_player()

    def loop(self):
        self.update_physics()
        self.render()

# pysick/ep_camera.py or inside ep.py


# Globals for window size and camera
_glut_window = None
_window_size = (800, 600)


def epAdvancedWindowInit(width=800, height=600, title="pysick graphics(Open GL)"):
    global _glut_window, _window_size
    _window_size = (width, height)

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(100, 100)
    _glut_window = glutCreateWindow(title.encode())

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1.0)

    print(f"[pysick] OpenGL 3D Window initialized ({width}x{height})")

    # Setup projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, width / height, 0.1, 1000.0)
    glMatrixMode(GL_MODELVIEW)


def epAdvancedRun(main_loop_func):
    glutDisplayFunc(main_loop_func)
    glutIdleFunc(main_loop_func)
    glutMainLoop()

def epEnable(code):
    global _ENABLE_ADVANCED
    if code == 'X_EP_ADVANCED<>3D':
        _ENABLE_ADVANCED = True
        glEnable(GL_DEPTH_TEST)

def epDisable(code):
    global _ENABLE_ADVANCED
    if code == 'X_EP_ADVANCED<>3D':
        _ENABLE_ADVANCED = False
        glDisable(GL_DEPTH_TEST)



#------------------------Internals Do not modify or use---------------------------


_ENABLE_ADVANCED = False
_epCameraFix = False
_camera_position = [0, 0]


_camera_position = [0, 0]

def _set_camera(x, y):
    _camera_position[0] = x
    _camera_position[1] = y

def _move_camera(dx, dy):
    _camera_position[0] += dx
    _camera_position[1] += dy

def _get_camera():
    return tuple(_camera_position)

def _draw(obj):
    cam_x, cam_y = _get_camera()
    draw_x = obj.x - cam_x
    draw_y = obj.y - cam_y

def follow_player(player):
    cam_x = player.x - pysick.ingine.width // 2
    cam_y = player.y - pysick.ingine.height // 2
    _set_camera(cam_x, cam_y)

    # Then draw with canvas using draw_x, draw_y instead of obj.x, obj.y
