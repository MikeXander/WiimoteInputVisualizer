import numpy as np
import cv2
import json
import time
import pygame

BUTTON_PRESS_MODES = ["fill", "negative", "dark"]
BUTTON_PRESS_MODE = BUTTON_PRESS_MODES[1]

light_blue = [100,255,255] #P1
yellow = [255,220,0] #P2

WIDTH = 1280
HEIGHT = 720

FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wiimote Input Visualizer")


def setColour(image, RGB):
    w, h = image.get_size()
    r, g, b = RGB
    for x in range(w):
        for y in range(h):
            p = image.get_at((x, y))
            t = 25 # threshhold for setting to transparent
            if p[0] < t and p[1] < t and p[2] < t:
                image.set_at((x, y), pygame.Color(0, 0, 0, 0))
            else:
                image.set_at((x, y), pygame.Color(r, g, b, p[3]))


def loadImage(filename, RGB = [255,255,255]):
    img = pygame.image.load("./Textures/"+filename)#.convert()
    setColour(img, RGB)
    return img


def draw(frame, key, loc):
    global graphics
    if not key.upper() in graphics.keys(): return
    frame.blit(graphics[key.upper()], loc)
    return frame

    
def drawStick(frame, x, y):
    scalar = 58
    start = (LOCATION["JOYSTICK"][0] + 62, LOCATION["JOYSTICK"][0] + 78)
    end = (int(x * scalar) + start[0], int(-y * scalar) + start[1])
    white = pygame.Color(255,255,255)
    pygame.draw.aaline(frame, white, start, end)
    return frame


graphics = {
    "JOYSTICK": loadImage("joystick-gate.png"),
    "JS-OUTLINE": loadImage("joystick-outline.png"),
    "P1A": loadImage("a-outline.png", light_blue),
    "P1B": loadImage("b-outline.png", light_blue),
    "P1APRESS": loadImage("/a-pressed-"+BUTTON_PRESS_MODE+".png", light_blue),
    "P1BPRESS": loadImage("b-pressed-"+BUTTON_PRESS_MODE+".png", light_blue),
    "P2A": loadImage("a-outline.png", yellow),
    "P2B": loadImage("b-outline.png", yellow),
    "P2APRESS": loadImage("a-pressed-"+BUTTON_PRESS_MODE+".png", yellow),
    "P2BPRESS": loadImage("b-pressed-"+BUTTON_PRESS_MODE+".png", yellow),
    "DPAD": loadImage("d-pad-gate.png"),
    "UP": loadImage("d-pad-up.png"),
    "DOWN": loadImage("d-pad-down.png"),
    "LEFT": loadImage("d-pad-left.png"),
    "RIGHT": loadImage("d-pad-right.png"),
    "Z": loadImage("z-outline.png"),
    "ZPRESS": loadImage("z-pressed-"+BUTTON_PRESS_MODE+".png"),
    "C": loadImage("c-outline.png"),
    "CPRESS": loadImage("c-pressed-"+BUTTON_PRESS_MODE+".png"),
}
print("textures loaded")


DPAD_LOC = (180,125)
LOCATION = {
    "JOYSTICK": (50, 65),
    "P1A": (290, 20),
    "P1APRESS": (290, 20),
    "P1B": (390, 20),
    "P1BPRESS": (390, 20),
    "P2A": (290, 120),
    "P2APRESS": (290, 120),
    "P2B": (390, 120),
    "P2BPRESS": (390, 120),
    "DPAD": DPAD_LOC,
    "UP": DPAD_LOC,
    "DOWN": DPAD_LOC,
    "LEFT": DPAD_LOC,
    "RIGHT": DPAD_LOC,
    "Z": (180, 0),
    "ZPRESS": (180, 0),
    "C": (180, 52),
    "CPRESS": (180, 52),
}


def getButtons(data):
    togglables = ["P1A", "P1B", "P2A", "P2B", "Z", "C"]
    buttons = []
    
    for key in data["buttons"].keys():
        
        if key.upper() in togglables:
            if data["buttons"][key]:
                buttons.append(key.upper()+"PRESS")
            else:
                buttons.append(key.upper())
            
        elif data["buttons"][key]:
            buttons.append(key.upper())
            
    return buttons


def drawButtons(frame, buttons):
    global LOCATION
    for button in buttons:
        if button in LOCATION:
            frame = draw(frame, button, LOCATION[button.upper()])
    return frame


def drawConsts(frame):
    constButtons = ["JOYSTICK", "DPAD"]
    for button in constButtons:
        frame = draw(frame, button, LOCATION[button])
        frame = draw(frame, button, LOCATION[button])
    return frame


def getFrame(data):
    frame = pygame.Surface((WIDTH, HEIGHT))
    frame = drawButtons(frame, getButtons(data))
    frame = drawStick(frame, data["stick"]["X"], data["stick"]["Y"])
    frame = drawConsts(frame)
    return frame


def save(data, codec, filename, fps = FPS):
    print("saving video...")
    fourcc = cv2.VideoWriter_fourcc(*codec)
    out = cv2.VideoWriter(filename, fourcc, fps, (WIDTH, HEIGHT))
    for obj in data:
        frame = getFrame(obj)
        screen.blit(frame, (0, 0)) # show it while encoding
        pygame.display.update()
        frame = pygame.surfarray.array3d(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # convert
        frame = np.fliplr(frame)
        frame = np.rot90(frame)
        out.write(frame)
    out.release()
    print("saved " + filename)


def getData(filename, loadMsg = True):
    data = []
    with open(filename) as file:
        data = json.load(file)
    if loadMsg:
        print(filename + " loaded")
    return data


def playback(data):
    for obj in data:
        start = time.time()
        frame = getFrame(obj)
        screen.blit(frame, (0, 0))
        pygame.display.flip()
        time.sleep(max(1/FPS - (time.time() - start), 0))
    print("Playback ended")



def start_encoding(codec, filename, width, height, fps = FPS):
    print("\n\nsaving video...\n")
    fourcc = cv2.VideoWriter_fourcc(*codec)
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    return out

def save_frame(out, surf):
    frame = pygame.surfarray.array3d(surf)
    #frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # convert
    #frame = np.fliplr(frame)
    frame = np.rot90(frame)
    out.write(frame)
    return out

def stop_encoding(out):
    out.release()
    print("\n\nVideo saved\n")
