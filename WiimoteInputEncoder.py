import numpy as np
import cv2
import json
import time

BUTTON_PRESS_MODES = ["fill", "negative", "dark"]
BUTTON_PRESS_MODE = BUTTON_PRESS_MODES[1]

light_blue = [100,255,255] #P1
yellow = [255,220,0] #P2

BLACKFRAME = np.zeros((720, 1280, 3), np.uint8)

WINDOW_NAME = "Input Display"
WIDTH = 1280
HEIGHT = 720

FPS = 60


def setColour(image, RGB):
    BGR = [RGB[2], RGB[1], RGB[0]]
    for i in range(3):
        for y in range(image.shape[0]):
            for x in range(image.shape[1]):
                image[y, x, i] = max(0, image[y, x, i]-255+BGR[i])
        #image[0:image.shape[0], 0:image.shape[1], i] -= 255-RGB[i] # underflows
    #image = np.clip(image, 0, 255) # not working?


def loadImage(filename, RGB = [255,255,255]):
    img = cv2.imread("./Textures/"+filename, 1)
    setColour(img, RGB)
    return np.copy(img)


def draw(frame, key, loc):
    global graphics
    if not key.upper() in graphics.keys(): return
    x, y = loc
    image = graphics[key.upper()]
    frame[y:y+image.shape[0], x:x+image.shape[1], 0:3] += image

    
def drawStick(frame, x, y):
    scalar = 58
    start = (LOCATION["JOYSTICK"][0] + 62, LOCATION["JOYSTICK"][0] + 78)
    end = (int(x * scalar) + start[0], int(-y * scalar) + start[1])
    white = (255,255,255)
    thickness = 4
    cv2.line(frame, start, end, white, thickness)
    #draw("js-outline", end[0]-64, end[1]-64)


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
            draw(frame, button, LOCATION[button.upper()])


def drawConsts(frame):
    constButtons = ["JOYSTICK", "DPAD"]
    for button in constButtons:
        draw(frame, button, LOCATION[button])
        draw(frame, button, LOCATION[button])


def getFrame(data):
    frame = np.copy(BLACKFRAME)
    drawButtons(frame, getButtons(data))
    drawStick(frame, data["stick"]["X"], data["stick"]["Y"])
    drawConsts(frame)
    return frame


def save(data, codec, filename, fps = FPS):
    print("saving video...")
    fourcc = cv2.VideoWriter_fourcc(*codec)
    out = cv2.VideoWriter(filename, fourcc, fps, (WIDTH, HEIGHT))
    for obj in data:
        frame = getFrame(obj)
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


def initDisplay():
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, WIDTH, HEIGHT)


def showLastFrame(filename):
    data = getData(filename, False)
    frame = getFrame(data[-1])
    cv2.imshow(WINDOW_NAME, frame)


def exitCondition():
    return cv2.waitKey(1) & 0xFF == ord('q')


def closeWindow():
    cv2.destroyAllWindows()


def playback(data):
    initDisplay()
    for obj in data:
        start = time.time()
        frame = getFrame(obj)
        cv2.imshow(WINDOW_NAME, frame)
        time.sleep(max(1/FPS - (time.time() - start), 0))
        if exitCondition():
            break
    print("Playback ended")
    closeWindow()


