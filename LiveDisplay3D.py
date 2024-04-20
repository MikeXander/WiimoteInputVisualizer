from Cores.SuperMarioGalaxy import get_controller_data
from WiimoteInputEncoder import Encoder3D
from WiimoteDataParser import WiimoteType3D

FPS = 60
encoder = Encoder3D()
encoder.set_wiimote_type(WiimoteType3D.UPRIGHT)

while encoder.display(FPS):
    wiimotes = get_controller_data()
    encoder.new_frame(wiimotes[0])
