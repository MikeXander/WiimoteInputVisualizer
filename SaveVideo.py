from WiimoteInputEncoder import Encoder
from Layouts import *

encoder = Encoder(
    window_size = (550, 250),
    background_colour = (0, 0, 0)
)

encoder.set_layouts([
    NunchukLayout("./Layouts/nunchuk.layout"),
    WiimoteLayout("./Layouts/wiimote.layout"),
    ClassicLayout("./Layouts/classic.layout")
])

encoder.save(
    input_filename = "./Sample Data/_inputs.csv",
    output_filename = "output.mp4",
    codec = "mp4v",
    fps = 60
)
