from Cores.SuperMarioGalaxy import *
import pygame
from pygame.locals import *
import time
from math import pi, acos, atan2
from OpenGL.GL import *
from OpenGL.GLU import *
from OBJLoader import *

FPS = 60 # max limit

pygame.init()
pygame.display.set_caption("Wiimote Input Visualizer")

size = (550, 550)
screen = pygame.display.set_mode(size, DOUBLEBUF | OPENGL)

# Source: https://github.com/yarolig/OBJFileLoader
def init():
    # setup screen
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, size[0] / size[1], 1, 50.0)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW)

    # lighting 
    # ToDo: my own lighting system to show button presses
    glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 200, 100, 0.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
init()

wiimote = OBJ("./Textures/20210523_wiimote_low_pivot.obj", scale=30)
wiimote.generate()

accel = {'X': 0, 'Y': 0, 'Z': 0}

# ToDo: control camera
'''
import keyboard

def key(s):
    return keyboard.is_pressed(s)

def rotate(speed = 1):
    global yaw, pitch
    if key('d'): yaw += speed
    elif key('a'): yaw -= speed
    if key('s'): pitch += speed
    elif key('w'): pitch -= speed
'''

class PIDController:
    #p = 0.24, i = 0.16, d = 0.09, e = 0.8
    def __init__(self, v0 = 0, p = 0.30, i = 0.12, d = 0.09, e = 0.8):
        self.value = v0
        self.target = 0
        self.err = 0
        self.errTotal = 0
        self.errLast = 0
        self._p = p
        self._i = i
        self._d = d
        self._e = e

    def step(self):
        self.err = self.target - self.value
        self.errTotal += self.err
        p = self._p * self.err
        i = self._i * self.errTotal
        d = self._d * (self.err - self.errLast)
        self.errLast = self.err
        self.errTotal *= self._e
        self.value += p + i + d
        if abs(self.value) < 1:
            self.value = 0
        return self.value


Yaw = PIDController(p = 0.12, i = 0.10)
Pitch = PIDController(p = 0.12, i = 0.10)
Roll = PIDController()

X = PIDController()
Y = PIDController()
Z = PIDController()


'''
TAS cases
Upright: Y = -104, Z = 0, X = lateral movement
Ray surfing: Y = 0, Z = -104, X = twist
'''

'''
Sphere coords problem: it flips in the bottom hemisphere.
This is because the pitch is from [-90, 90].
So once you tilt past the horizontal, the magnitude of the pitch
angle decreases and the yaw greatly increases.
There may be some way around this?
'''

def sphere_coords(X, Y, Z):
    global Yaw, Pitch
    rho = max((X*X + Y*Y + Z*Z)**0.5, 0.00001)
    Yaw.target = -atan2(Y, X) * 180/pi - 90
    Pitch.target = (acos(Z / rho) - pi/2) * 180/pi

    # PID is struggling when it switches from 89 to -270
    # this makes it so the flip point is when it's upsidedown
    if Yaw.value > 0 and Yaw.target < Yaw.value - 180:
        Yaw.value -= 360
    elif Yaw.target > 0 and Yaw.value < Yaw.target - 180:
        Yaw.value += 360

    # resting straight forwards it tries to twist to the right
    if Yaw.target == -90 and abs(Pitch.target) == 90:
        Yaw.target = 0

    Yaw.step()
    Pitch.step()
    
    return Yaw.value, Pitch.value

# https://www.nxp.com/files-static/sensors/doc/app_note/AN3461.pdf
# if I take the time to do the lin alg and get yaw this will probably
# be a better approach
def other_solution(X, Y, Z):
    global Yaw, Pitch, Roll
    MIU = 0.001
    sign = 1 if Z > 0 else -1 
    Pitch.target = -atan2(Y, sign * (Z*Z + MIU*X*X)**0.5) * 180/pi - 90
    Roll.target = atan2(X, (Y*Y + Z*Z)**0.5) * 180/pi
    
    Pitch.step()
    Roll.step()


def RotYawPitch(yaw, pitch):
    glRotate(round(yaw), 0, 0, 1)
    glRotate(round(pitch), 1, 0, 0)


def RotPitchRoll(pitch, roll):
    glRotate(round(pitch), 1, 0, 0)
    glRotate(round(roll), 0, 1, 0)


def RotAll(yaw, pitch, roll):
    glRotate(round(yaw), 0, 0, 1)
    glRotate(round(pitch), 1, 0, 0)
    glRotate(round(roll), 0, 1, 0)


while True:
    start = time.time()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
            break
    
    new_accel = {}
    try:
        new_accel = wiimote_accel()
    except Exception as e:
        print("Failed to read from Dolphin", e)
        break

    # Ignore when the game drops packets
    # This is only a problem with real wiimotes
    if new_accel['X'] == 0 and new_accel['Y'] == 0 and new_accel['Z'] == 0:
            pass
    else:
        # Ignore small changes
        TOLERANCE = 5
        for axis in "XYZ":
            if abs(accel[axis] - new_accel[axis]) > TOLERANCE:
                accel[axis] = new_accel[axis]
    #print(accel)

    # noise filter
    for k in accel.keys():
        accel[k] = accel[k]//10*10

    X.target = accel['X']
    X.step()
    Y.target = accel['Y']
    Y.step()
    Z.target = accel['Z']
    Z.step()
    
    yaw, pitch = sphere_coords(X.value, Y.value, Z.value)
    #other_solution(X.value, Y.value, Z.value)
    print(f"%4d %4d %4d" % (round(yaw), round(pitch), round(Roll.value)))

    # setup display
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslate(0, -1, -8)
    
    RotYawPitch(yaw, pitch)
    #RotPitchRoll()
    #RotAll()
    
    wiimote.render()
    
    pygame.display.flip()
    time.sleep(max(1/FPS - (time.time() - start), 0))

pygame.display.quit()
