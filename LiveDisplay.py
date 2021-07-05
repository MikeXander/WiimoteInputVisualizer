import WiimoteInputEncoder as encoder
from Cores.SuperMarioGalaxy import *
import pygame
import time

FPS = 60 # max limit

pygame.init()
screen = pygame.display.set_mode((550, 280))
pygame.display.set_caption("Wiimote Input Visualizer")

while True:
    start = time.time()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
            break
    data = {}
    try:
        b = buttons()
        s = stick()
        data = {
            "frame":0,
            "buttons":{
                "p1b":"B" in b["P1"],
                "p2b":"B" in b["P2"],
                "p1a":"A" in b["P1"],
                "two":"2" in b["P1"],
                "right":"RIGHT" in b["P1"],
                "one":"1" in b["P1"],
                "z":"Z" in b["P1"],
                "p2a":"A" in b["P2"],
                "left":"LEFT" in b["P1"],
                "plus":"+" in b["P1"],
                "down":"DOWN" in b["P1"],
                "minus":"-" in b["P1"],
                "up":"UP" in b["P1"],
                "c":"C" in b["P1"],
                "home":"HOME" in b["P1"]
            },
            "vel":{
                "position": position(),
                "up_grav": up_gravity(),
                "velocity": base_velocity(),
                "gravity": down_gravity(),
                "tilt": tilt()
            },
            "stick":{
                "Y": s["Y_processed"],
                "X": s["X_processed"]
            }
        }
    except Exception as e:
        print(e)
        break
    screen.blit(encoder.getFrame(data), (0, 0))
    pygame.display.update()
    time.sleep(max(1/FPS - (time.time() - start), 0))

pygame.display.quit()
