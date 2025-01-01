from Layouts import Layout
from LayoutElements import Texture
from WiimoteDataParser import WiimoteData, WiimoteType3D
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont
import pygame
from pygame.locals import *
import numpy as np
import cv2
from OpenGL.GL import *
from OpenGL.GLU import *
from OBJLoader import OBJ
from time import time, sleep
from math import pi, acos, atan2

# TODO:
# - allow mismatched # of controllers and layouts?
# - Camera control for 3d
# - multiple controllers for 3d
# - move self.frame from Encoder2D to Encoder (+move add text)

class Encoder:
    def __init__(self, window_size: Tuple[int, int] = (550, 250), background_colour = (0,0,0)):
        self.size = window_size
        self.background_colour = background_colour
        self.last_display_time = time()
        self.outstream = None
        pygame.init()
        pygame.display.set_caption("Wiimote Input Visualizer")
        self.tick = 0

    # enforce displaying at specific FPS
    # return true if update successful, false if pygame was closed
    def display(self, FPS = 60, skip_event_check = False):
        current_time = time()
        sleep(max(1/FPS - (current_time - self.last_display_time), 0))
        
        if not skip_event_check:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
            
        if self.outstream is not None: # Encoding
            # convert pygame screen to opencv2 screen for output
            frame = pygame.surfarray.array3d(self.frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) 
            frame = np.fliplr(frame)
            frame = np.rot90(frame)
            self.outstream.write(frame)

        self.last_display_time = time()
        return True
    
    def start_recording(self):
        # 3D encoding will require a frame buffer
        # https://stackoverflow.com/questions/53748691/how-do-i-make-opengl-draw-do-a-non-display-surface-in-pygame
        pass

    def stop_recording(self):
        pass
    
    def __del__(self): # just in case
        pygame.display.quit()
        pygame.quit()


# a collection of layouts, that can be drawn to screen and/or saved to video
class Encoder2D(Encoder):
    def __init__(self, window_size = (550, 250), background_colour = (0,0,0), texture_path = "./Textures/"):
        super().__init__(window_size, background_colour)
        Texture.set_texture_path(texture_path)
        self.layouts = []
        self.sent_font_warn = False
        self.mismatch_layout_warn = False
        self.outstream = None
        self.output_name = "out.mp4"

        self.screen = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        self.frame = pygame.Surface(self.size) # default blank frame
        self.frame.fill(self.background_colour)

    # can't be passed to init because the layouts require pygame to already be initialized
    def set_layouts(self, layouts: List[Layout]):
        self.layouts = layouts
        self.reload_layouts() # fixes screen size but loads layouts twice initially

    # this will use the window size and background colour of the LAST VALID layout
    def reload_layouts(self):
        new_size = None
        new_colour = None
        for layout in self.layouts:
            size, col = layout.reload()
            if size is not None:
                new_size = size
            if col is not None:
                new_colour = col
        if new_size:
            self.size = new_size
            self.screen = pygame.display.set_mode(new_size)
        if new_colour:
            self.background_colour = new_colour
        
    def new_frame(self, wiimotes: List[WiimoteData]):
        self.frame = pygame.Surface(self.size)
        self.frame.fill(self.background_colour)

        if len(wiimotes) != len(self.layouts):
            if not self.mismatch_layout_warn:
                self.mismatch_layout_warn = True
                print(f"[WARNING] number of controllers ({len(wiimotes)}) mismatches number of layouts ({len(self.layouts)}). Unused layouts will be hidden.")
            while len(self.layouts) < len(wiimotes):
                self.layouts.append(Layout())
            while len(wiimotes) < len(self.layouts):
                wiimotes.append(None)

        for layout, wm in zip(self.layouts, wiimotes):
            if wm:
                layout.set_inputs(wm)
                self.frame = layout.draw(self.frame)

    # returns True if update was successful, False if pygame was closed
    def display(self, FPS = 60) -> bool:
        # for lack of a better place to check, since this should be called each tick
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # need to check here otherwise it wont close ?
                pygame.quit()
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.reload_layouts()
                elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    if self.outstream is None:
                        self.start_recording(FPS = FPS)
                    else:
                        self.stop_recording()
                        self.outstream = None

        self.screen.blit(self.frame, (0, 0))
        pygame.display.update()
        return super().display(FPS, True)

    # position is measured from the top left
    def add_text(self, text: str, pos: Tuple[int] = (0,0), colour: Tuple[int] = (255, 255, 255, 255), font: str = "Delfino.ttf", size: int = 16):
        if len(text) == 0:
            return
        
        # load font, since this could be called each tick, only give them 1 warning
        # inefficiently tries to construct the font every time
        fnt = None
        if not font.lower().endswith(".ttf"): # makes it a little more user friendly
            font += ".ttf"
        try:
            fnt = ImageFont.truetype(font, size)
        except Exception:
            if not self.sent_font_warn:
                print(f"[WARNING] {font} font not found. Defaulting to arial instead.")
                self.sent_font_warn = True
            fnt = ImageFont.truetype("arial.ttf", size)

        if len(colour) == 3: # add alpha
            colour = colour + (255,)

        arr = pygame.surfarray.array3d(self.frame)
        arr = np.flip(arr, axis=1)  # reflect horizontally
        img = Image.fromarray(arr)
        img = img.rotate(90, expand=True) #  CCW
        draw = ImageDraw.Draw(img)
        draw.text(pos, text, font = fnt, fill = colour)
        img = img.rotate(-90, expand=True)
        arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2RGB)
        arr = np.flip(arr, axis=1)  # reflect horizontally
        self.frame = pygame.surfarray.make_surface(arr)

    # preview what it looks like
    def playback(self, input_filename: str, fps = 60, text_settings = {}):
        data = [] # read file
        with open(input_filename, 'r') as f:
            data = f.readlines()
        first_frame = WiimoteData.Parse(data[1])[0][0].frame
        total_frames = WiimoteData.Parse(data[-1])[0][0].frame - first_frame
        for line in data[1:]:
            start = time()
            wiimotes, extra_info = WiimoteData.Parse(line)
            print(f"Playback frame: {wiimotes[0].frame - first_frame} / {total_frames}", end='\r', flush=True)
            self.new_frame(wiimotes)
            self.add_text(
                extra_info,
                **{
                    **{"pos":(0,0), "colour": (255, 255, 255, 255), "font": "Delfino.ttf", "size": 16},
                    **text_settings
                }
            )
            self.display()
            sleep(max(1/fps - (time() - start), 0))
        print("\nPlayback complete.")
        
    def start_recording(self, output_filename = "output.mp4", codec = "mp4v", FPS = 60):
        fourcc = cv2.VideoWriter_fourcc(*codec)
        self.outstream = cv2.VideoWriter(output_filename, fourcc, FPS, self.size)
        self.output_name = output_filename
        print(f"Saving inputs as video @ {FPS}fps to \"{output_filename}\"...", flush=True)

    def stop_recording(self):
        self.outstream.release()
        print(f"{self.output_name} saved.")
    
    # can use "XVID" codec for avi
    def save(self, input_filename: str, output_filename = "output.mp4", codec = "mp4v", fps = 60, text_settings = {}):
        data = [] # read file
        with open(input_filename, 'r') as f:
            data = f.readlines()
        print("Inputs loaded.")

        self.start_recording(output_filename, codec, fps)

        first_frame = WiimoteData.Parse(data[1])[0][0].frame
        total_frames = WiimoteData.Parse(data[-1])[0][0].frame - first_frame
        for line in data[1:]: # skip header
            wiimotes, extra_info = WiimoteData.Parse(line)
            print(f"Encoding frame: {wiimotes[0].frame - first_frame} / {total_frames}", end='\r', flush=True)
            self.new_frame(wiimotes)
            self.add_text(
                extra_info,
                **{ # unpacks and merges the default values with the text_settings parameter
                    **{"pos":(0,0), "colour": (255, 255, 255, 255), "font": "Delfino.ttf", "size": 16},
                    **text_settings
                }
            )
            self.display() # show it while encoding

        print()
        self.stop_recording()


# For smoothing out the 3D visualizer
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

    # intended use is to set an offset target (i.e. +4, or -3)
    # the value will be set modulo mod (i.e. 2Pi)
    # this is meant to handle PID for angles that wrap around
    def set_target(self, target, mod):
        pass

# TAS use cases (expected accel)
# Upright: Y = -104, Z = 0, X = lateral movement
# Ray surfing (SMG): Y = 0, Z = -104, X = twist

class Encoder3D(Encoder):
    def __init__(
            self,
            window_size = (550, 550),
            background_colour = (0,0,0),
            accel_change_threshold = 6 # ignores changes in accel smaller than this
        ):
        super().__init__(window_size, background_colour)
        self.epsilon = accel_change_threshold
        self.wiimote = None
        self.wmtype = -1
        self.accel = [ # XYZ accelerometer data
            PIDController(),
            PIDController(),
            PIDController()
        ]
        self.angle = [ # Yaw Pitch Roll
            PIDController(p = 0.12, i = 0.10),
            PIDController(p = 0.12, i = 0.10),
            PIDController()
        ]

        self.screen = pygame.display.set_mode(window_size, DOUBLEBUF | OPENGL)

        # Source: https://github.com/yarolig/OBJFileLoader
        # setup screen
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60.0, window_size[0] / window_size[1], 1, 50.0)
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

    def set_wiimote_type(self, wmtype: WiimoteType3D):
        self.wmtype = wmtype
        if wmtype == WiimoteType3D.UPRIGHT:
            self.wiimote = OBJ("./Textures/20210523_wiimote_low_pivot.obj", scale = 30)
        elif wmtype == WiimoteType3D.SIDEWAYS:
            self.wiimote = OBJ("./Textures/20210523_wiimote.obj", scale = 30)
        else:
            self.wiimote = None
            return
        self.wiimote.generate()

    # updates yaw, pitch, roll based on self.accel
    def update_angles(self):
        x, y, z = map(lambda pid: pid.value, self.accel)
        if self.wmtype == WiimoteType3D.UPRIGHT: # sphere coordinates
            # Sphere coords problem: it flips in the bottom hemisphere.
            # This is because the pitch is from [-90, 90].
            # So once you tilt past the horizontal, the magnitude of the pitch
            # angle decreases and the yaw greatly increases.
            # There may be some way around this?
            rho = max((x*x + y*y + z*z)**0.5, 0.00001)
            self.angle[0].target = -atan2(y, x) * 180/pi - 90
            self.angle[1].target = (acos(z / rho) - pi/2) * 180/pi
            self.angle[2].value = 0
            self.angle[2].target = 0

            # PID is struggling when it switches from 89 to -270
            # this makes it so the flip point is when it's upsidedown
            if self.angle[0].value > 0 and self.angle[0].target < self.angle[0].value - 180:
                self.angle[0].value -= 360
            elif self.angle[0].target > 0 and self.angle[0].value < self.angle[0].target - 180:
                self.angle[0].value += 360

            # resting straight forwards it tries to twist to the right
            if self.angle[0].target == -90 and abs(self.angle[1].target) == 90:
                self.angle[0].target = 0

        elif self.wmtype == WiimoteType3D.SIDEWAYS:
            self.angle[0].target = -atan2(y, x) * 180/pi - 90
            self.angle[1].value = 0
            self.angle[1].target = 0
            self.angle[2].target = -atan2(z, x) * 180/pi + 180

            # PID is struggling when Yaw switches from 89 to -270
            # this makes it so the flip point is when it's upsidedown
            if self.angle[0].value >= 0 and self.angle[0].target < self.angle[0].value - 180:
                self.angle[0].value -= 360
            elif self.angle[0].target >= 0 and self.angle[0].value < self.angle[0].target - 180:
                self.angle[0].value += 360

            # when holding sideways, we only care about Roll angles [-90, 90]
            # where 0 is flat. Make sure the PID doesn't spin the other way.
            if self.angle[2].value < 90 and self.angle[2].target > self.angle[2].value + 180:
                self.angle[2].value += 360
            elif self.angle[2].target < 90 and self.angle[2].value > self.angle[2].target + 180:
                self.angle[2].value -= 360

            # TODO: fix resting upright/flat up/down...
            EPSILON = 1
            if abs(self.angle[0].target - (-90)) <= EPSILON and self.angle[2].target == 90:
                self.angle[0].target = -270
            elif abs(self.angle[0].target - 0) <= EPSILON and self.angle[2].target == 270:
                self.angle[0].target = -270

        else:
            # https://www.nxp.com/files-static/sensors/doc/app_note/AN3461.pdf
            # if I take the time to do the lin alg and get yaw this will probably
            # be a better approach
            MIU = 0.001
            sign = 1 if z > 0 else -1 
            self.angle[0].value = 0
            self.angle[0].target = 0
            self.angle[1].target = -atan2(y, sign * (z*z + MIU*x*x)**0.5) * 180/pi - 90
            self.angle[2].target = atan2(x, (y*y + z*z)**0.5) * 180/pi
        
        for pid in self.angle:
            pid.step()

    def new_frame(self, wiimote: WiimoteData):
        # ignore when the game drops packets (problem with real wiimotes)
        if all(wiimote.acc[i] == 0 for i in range(3)):
            return
        
        wiimote.acc = tuple(map(lambda x: x-512, wiimote.acc)) # old code ranges from [-512, 511]
        for i in range(3):
            # Note: this ignores small changes BEFORE applying a noise filter to the new values
            # but AFTER the noise filter has already been applied to the old values...
            if abs(self.accel[i].target - wiimote.acc[i]) >= self.epsilon:
                # drop least significant base-10 digit
                self.accel[i].target = wiimote.acc[i] // 10 * 10
                self.accel[i].step()
        
        x,y,z = map(lambda pid: pid.value, self.accel)
        m = (x**2 + y**2 + z**2)**0.5
        #print(self.accel[0].target, self.accel[0].target - wiimote.acc[0])
        #print(f"X: % 3d Y % 3d Z % 3d (%.2f)" % (x,y,z,m))
        self.update_angles()
        #print(f"%4d %4d %4d" % tuple(map(lambda pid: round(pid.target), self.angle)))
        #print(f"%d" % round(self.angle[0].errTotal))

    def display(self, FPS = 60):
        if self.wiimote is None:
            raise ValueError("Use encoder.set_wiimote_type(...) before displaying")
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslate(0, -1, -8)
        yaw, pitch, roll = map(lambda pid: round(pid.value), self.angle)
        glRotate(yaw, 0, 0, 1)
        glRotate(pitch, 1, 0, 0)
        glRotate(roll, 0, 1, 0)
        self.wiimote.render()
        pygame.display.flip()
        return super().display(FPS)
