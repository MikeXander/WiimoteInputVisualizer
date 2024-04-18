from Cores.SuperMarioGalaxy import get_controller_data, get_additional_data
from WiimoteInputEncoder import Encoder2D
from Layouts import *

FPS = 60

encoder = Encoder2D(
    window_size = (550, 280),
    background_colour = (0, 0, 0)
)

encoder.set_layouts([
    NunchukLayout("./Layouts/smg_p1.layout"),
    WiimoteLayout("./Layouts/smg_p2.layout")
])

while encoder.display(FPS):
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
