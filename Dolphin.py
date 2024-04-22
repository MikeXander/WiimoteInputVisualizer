from WiimoteDataParser import WiimoteData
import Cores
import dolphin_memory_engine as dme
from time import time, sleep
from typing import List
from os import listdir
from os.path import join, isfile
import pygame

# This handles the connection to Dolphin Emulator (and auto detects game)

# import every supported game from ./Cores/
SUPPORTED_GAMES = set()
for f in listdir("./Cores"):
    if isfile(join("./Cores", f)):
        gameid = f[:-3]
        SUPPORTED_GAMES.add(gameid)
        __import__("Cores." + gameid)

dme.get_gameid = lambda: dme.read_bytes(0x0, 6).decode("utf-8")

# sleep but let pygame events occur
# returns true if time passed, false otherwise
def wait(sec):
    start = time()
    while time() - start < sec:
        sleep(1/60) # check at 60fps
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
    return True

def reconnect(max_retries = 10):
    if dme.is_hooked():
        return True
    for retry in range(max_retries):
        dme.hook()
        if dme.is_hooked():
            print("Connected to " + dme.get_gameid())
            return True
        elif retry == 0:
            print("Reconnecting to Dolphin.", end='', flush=True)
        if not wait(3):
            print(" Exiting visualizer.")
            return False
        print(".", end='', flush=True)
    print(f"\nMaximum reconnection attempts ({max_retries}) exceeded. Exiting visualizer.")
    return False

# runs method for the appropriate game based on gameid
# returns None if something goes wrong (likely game closed)
last_gameid = ""
def call_game_module_method(method):
    # prevent trying to find the game id when we know that it wont work
    if not dme.is_hooked():
        return None
    
    try:
        gameid = dme.get_gameid()

        if gameid not in SUPPORTED_GAMES:
            global last_gameid
            if gameid != last_gameid: # game changed
                print(f"[WARNING] Detected unsupported game: {gameid}")
            last_gameid = gameid
            return None
        
        Game = getattr(Cores, gameid)
        if not hasattr(Game, method): # method not implemented
            return None
        return getattr(Game, method)()
    
    except Exception as e:
        if str(e)[:21] == "Could not read memory":
            dme.un_hook() # next loop will try to reconnect
            return None
        raise e # propagate any other errors
    
def get_controller_data() -> List[WiimoteData]:
    return call_game_module_method("get_controller_data") or []
    
def get_additional_data() -> str:
    return call_game_module_method("get_additional_data") or ""
