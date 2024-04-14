from Cores.SuperMarioGalaxy import get_controller_data, get_additional_data
from WiimoteInputEncoder import Encoder
from Layouts import *
import time

FPS = 60 # max limit

encoder = Encoder(
    window_size = (550, 280),
    background_colour = (0, 0, 0)
)

encoder.set_layouts([
    NunchukLayout("./Layouts/smg_p1.layout"),
    WiimoteLayout("./Layouts/smg_p2.layout")
])

while encoder.display():
    start = time.time()
    
    try:
        wiimotes = get_controller_data()
        encoder.new_frame(wiimotes)

        text = get_additional_data()
        encoder.add_text(
            text,
            pos = (40, 200),
            colour = (255, 255, 255),
            font = "Delfino",
            size = 25
        )
    except Exception as e:
        if str(e)[:21] == "Could not read memory":
            print("Could not read memeory. Waiting reconnect...")
            time.sleep(3)
        else:
            print(e)
            break
    
    time.sleep(max(1/FPS - (time.time() - start), 0))
