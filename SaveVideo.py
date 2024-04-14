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

# watch/preview the inputs
encoder.playback(
    input_filename = "./Sample Data/_inputs.csv",
    fps = 5
)

# save the inputs to a file
encoder.save(
    input_filename = "./Sample Data/_inputs.csv",
    output_filename = "output.mp4",
    codec = "mp4v",
    fps = 60
)
