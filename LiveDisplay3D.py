from WiimoteInputEncoder import Encoder3D
from WiimoteDataParser import WiimoteType3D
import Dolphin

FPS = 60
encoder = Encoder3D()
encoder.set_wiimote_type(WiimoteType3D.UPRIGHT)

while encoder.display(FPS) and Dolphin.reconnect():
    wiimotes = Dolphin.get_controller_data()
    if len(wiimotes):
        encoder.new_frame(wiimotes[0])
