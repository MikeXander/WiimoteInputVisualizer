from Layouts import Layout
from WiimoteDataParser import WiimoteData
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont
import pygame
import numpy as np
import cv2
from time import time, sleep

# TODO: allow mismatched # of controllers and layouts?

# a collection of layouts, that can be drawn to screen and/or saved to video
class Encoder:
    def __init__(self, window_size = (550, 250), background_colour = (0,0,0)):
        self.layouts = []
        self.size = window_size
        self.background_colour = background_colour
        self.sent_font_warn = False
    
        pygame.init() # pygame setup
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Wiimote Input Visualizer")

        self.frame = pygame.Surface(self.size) # default blank frame
        self.frame.fill(self.background_colour)

    # can't be passed to init because the layouts require pygame to already be initialized
    def set_layouts(self, layouts: List[Layout]):
        self.layouts = layouts

    def reload_layouts(self):
        for layout in self.layouts:
            layout.reload()

    def new_frame(self, wiimotes: List[WiimoteData]):
        self.frame = pygame.Surface(self.size)
        self.frame.fill(self.background_colour)
        if len(wiimotes) != len(self.layouts):
            print(f"[ERROR] number of controllers ({len(wiimotes)}) mismatches number of layouts ({len(self.layouts)}). Drawing skipped.")
            return
        for layout, wm in zip(self.layouts, wiimotes):
            layout.set_inputs(wm)
            self.frame = layout.draw(self.frame)

    # returns True if update was successful, False if pygame was closed
    def display(self) -> bool:
        # for lack of a better place to check, since this should be called each tick
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.reload_layouts()

        self.screen.blit(self.frame, (0, 0))
        pygame.display.update()
        return True
    
    def __del__(self): # just in case
        pygame.display.quit()
        pygame.quit()

    # position is measured from the top left
    def add_text(self, text: str, pos: Tuple[int] = (0,0), colour: Tuple[int] = (255, 255, 255, 255), font: str = "Delfino.ttf", size: int = 16):
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
    def playback(self, input_filename: str, fps = 60):
        data = [] # read file
        with open(input_filename, 'r') as f:
            data = f.readlines()
        first_frame = WiimoteData.Parse(data[1])[0].frame
        total_frames = WiimoteData.Parse(data[-1])[0].frame - first_frame
        for line in data[1:]:
            start = time()
            wiimotes = WiimoteData.Parse(line)
            print(f"Playback frame: {wiimotes[0].frame - first_frame} / {total_frames}", end='\r', flush=True)
            self.new_frame(wiimotes)
            self.display()
            sleep(max(1/fps - (time() - start), 0))
        print("\nPlayback complete.")
        
    # can use "XVID" codec for avi
    def save(self, input_filename: str, output_filename = "output.mp4", codec = "mp4v", fps = 60):
        print(f"Saving inputs as video @ {fps}fps to \"{output_filename}\"...", end=' ')
        fourcc = cv2.VideoWriter_fourcc(*codec)
        out = cv2.VideoWriter(output_filename, fourcc, fps, self.size)

        data = [] # read file
        with open(input_filename, 'r') as f:
            data = f.readlines()
        print("Inputs loaded.")

        first_frame = WiimoteData.Parse(data[1])[0].frame
        total_frames = WiimoteData.Parse(data[-1])[0].frame - first_frame
        for line in data[1:]: # skip header
            wiimotes = WiimoteData.Parse(line)
            print(f"Encoding frame: {wiimotes[0].frame - first_frame} / {total_frames}", end='\r', flush=True)
            self.new_frame(wiimotes)
            self.display() # show it while encoding

            # convert pygame screen to opencv2 screen for output
            frame = pygame.surfarray.array3d(self.frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) 
            frame = np.fliplr(frame)
            frame = np.rot90(frame)
            out.write(frame)
        out.release()
        print("\nEncoding complete.")
