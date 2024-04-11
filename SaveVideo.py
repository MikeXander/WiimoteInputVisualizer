from WiimoteInputEncoder import Encoder
from Layouts import WiimoteLayout

encoder = Encoder(
    window_size = (550, 250),
    background_colour = (0, 0, 0)
)

encoder.save(
    input_filename = "_inputs.csv",
    layouts = [
        WiimoteLayout("./Layouts/wiimote.layout")
    ],
    output_filename = "output.mp4",
    codec = "mp4v",
    fps = 60
)
