from Layouts import Layout
from WiimoteDataParser import WiimoteData
from typing import List
from PIL import Image, ImageDraw, ImageFont
import pygame
import numpy as np
import cv2
from time import time, sleep

# TODO: save video with multiple layouts
# parse the csv and send repeated frames to the layouts in order
# i.e. if frame x appears twice, send the first one to layouts[0], second to layouts[1], etc.

# a collection of layouts, that can be drawn to screen and/or saved to video
class Encoder:
    def __init__(self, window_size, background_colour = (0,0,0), fontname = "Delfino.ttf"):
        self.frame = None
        self.size = window_size
        self.background_colour = background_colour

        try:
            ImageFont.truetype(fontname, 10)
        except:
            print(f"[WARNING] {fontname} font not found. Defaulting to arial instead.")
            fontname = "arial.ttf"
        self.fontname = fontname

        pygame.init()
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Wiimote Input Visualizer")

    def new_frame(self, *layouts: List[Layout]):
        self.frame = pygame.Surface(self.size)
        self.frame.fill(self.background_colour)
        for layout in layouts:
            self.frame = layout.draw(self.frame)

    def show(self):
        # for lack of a better place to check, since this should be called each tick
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        self.screen.blit(self.frame, (0, 0))
        pygame.display.update()

    # position is measured from the top left
    def add_text(self, text, pos=(0,0), colour=(255, 255, 255), size=16):
        arr = pygame.surfarray.array3d(self.frame)
        arr = np.flip(arr, axis=1)  # reflect horizontally
        img = Image.fromarray(arr)
        img = img.rotate(90, expand=True) #  CCW
        draw = ImageDraw.Draw(img)
        r,g,b = colour
        draw.text(
            pos,
            text,
            font = ImageFont.truetype(self.fontname, size),
            fill = (r,g,b,255)
        )
        img = img.rotate(-90, expand=True)
        arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2RGB)
        arr = np.flip(arr, axis=1)  # reflect horizontally
        self.frame = pygame.surfarray.make_surface(arr)

    # preview what it looks like
    def playback(self, input_filename: str, layout: Layout, fps = 60):
        data = [] # read file
        with open(input_filename, 'r') as f:
            data = f.readlines()
        for line in data[1:]:
            start = time()
            obj = WiimoteData(line)
            layout.set_inputs(obj)
            self.new_frame(layout)
            self.show()
            sleep(max(1/fps - (time() - start), 0))
        print("Playback complete.")
        

    # can use "XVID" codec for avi
    def save(self, input_filename: str, layout: Layout, output_filename = "output.mp4", codec = "mp4v", fps = 60):
        print("Encoding inputs as video...", end=' ')
        fourcc = cv2.VideoWriter_fourcc(*codec)
        out = cv2.VideoWriter(output_filename, fourcc, fps, self.size)

        data = [] # read file
        with open(input_filename, 'r') as f:
            data = f.readlines()
        print("Inputs loaded.")

        last_frame = WiimoteData(data[-1]).frame
        for line in data[1:]: # skip header
            obj = WiimoteData(line)
            print(f"frame: {obj.frame} / {last_frame}", end='\r', flush=True)
            
            layout.set_inputs(obj)
            self.new_frame(layout)
            self.show() # show it while encoding

            frame = pygame.surfarray.array3d(self.frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # convert
            frame = np.fliplr(frame)
            frame = np.rot90(frame)
            out.write(frame)
        out.release()
        print("\nSaved to " + output_filename)
