from WiimoteInputEncoder import Encoder2D
from Layouts import *
import Dolphin

FPS = 60

encoder = Encoder2D(
    texture_path = "./Textures/"
)

encoder.set_layouts([
    NunchukLayout("./Layouts/smg_p1.layout"),
    WiimoteLayout("./Layouts/smg_p2.layout")
])

while encoder.display(FPS) and Dolphin.reconnect():
    wiimotes = Dolphin.get_controller_data()
    encoder.new_frame(wiimotes)
    text = Dolphin.get_additional_data()
    encoder.add_text(
        text,
        pos = (40, 200),
        colour = (255, 255, 255),
        font = "Delfino",
        size = 25
    )
