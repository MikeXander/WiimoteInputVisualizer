from __future__ import annotations
from typing import Set, List, Tuple

# TODO: better errors (invalid length, invalid specific entries), parse more

# This saves a CSV-like file with variable length rows (can change as extensions/controllers change)
# Each row always starts with: Frame, Number of Controllers, ...
# and then depending on what wiimotes are enabled and what extensions they have
# these are the respective headers based on extension type
HEADERS = {
	0: "ControllerID, ExtensionID, Buttons, IR, Accel", # None
	1: "ControllerID, ExtensionID, Buttons, IR, Accel, Stick, NunchukAccel", # Nunchuk
	2: "ControllerID, ExtensionID, Buttons, LStick, RStick" # Classic
}
# example row:
# 42,3,0, A B,0 0,512 512 616,1, C Z,0 0,512 512 616,128 128,512 512 716,2, L R ZL ZR,32 32,16 16

class WiimoteTypes:
    WIIMOTE = 0 # ir, acc
    NUNCHUK = 1 # ir, acc, stick, nacc
    CLASSIC = 2 # stick, rstick

class WiimoteType3D:
    UPRIGHT = 0
    SIDEWAYS = 1

def read_ints(space_separated_ints: str):
    return tuple(map(int, space_separated_ints.split()))

# standardized data type
class WiimoteData:
    def __init__(
            self,
            frame: int = -1, # this isnt wiimote data but it's important for encoding videos
            id: int = 4, # Wiimotes 1-4 have IDs 4-7
            extension_type: WiimoteTypes = WiimoteTypes.WIIMOTE,
            buttons: Set[str] = None, # set of uppercase button names that are pressed. Ex: {"A", "B"}
            ir: Tuple[int] = (0, 0), # range: [0, 1023]
            acc: Tuple[int] = (512, 512, 616), # range: [0, 1023]
            stick: Tuple[int] = (128, 128), # range: [0, 255] for nunchuk, [0, 63] for classic controller
            nacc: Tuple[int] = (512, 512, 716), # range: [0, 1023]
            rstick: Tuple[int] = (128, 128) # range: [0, 31] for classic controller
        ):
        self.frame = frame
        self.id = id
        self.type = extension_type
        self.buttons = buttons or set() 
        self.buttons = set(self.buttons) # enforce type
        self.ir = ir
        self.acc = acc
        self.stick = stick
        self.nacc = nacc
        self.rstick = rstick

    # this is for converting 1 line in the csv output
    @ staticmethod
    def Parse(csv_line: str) -> Tuple[List[WiimoteData], str]:
        try:
            data = csv_line.strip().split(',')
            frame = int(data[0])
            num_wiimotes = int(data[1])
            wmdata = []
            i = 2

            for _ in range(num_wiimotes):
                controller_id = int(data[i])
                extension_type = int(data[i+1])
                btns = set(map(lambda b: b.upper(), data[i+2].strip().split(' ')))
                wm = None

                if extension_type == WiimoteTypes.WIIMOTE:
                    wm = WiimoteData(
                        frame, controller_id, extension_type, btns,
                        ir = read_ints(data[i+3]),
                        acc = read_ints(data[i+4])
                    )
                    i += 5

                elif extension_type == WiimoteTypes.NUNCHUK:
                    wm = WiimoteData(
                        frame, controller_id, extension_type, btns,
                        ir = read_ints(data[i+3]),
                        acc = read_ints(data[i+4]),
                        stick = read_ints(data[i+5]),
                        nacc = read_ints(data[i+6])
                    )
                    i += 7

                elif extension_type == WiimoteTypes.CLASSIC:
                    wm = WiimoteData(
                        frame, controller_id, extension_type, btns,
                        stick = read_ints(data[i+3]),
                        rstick = read_ints(data[i+4])
                    )
                    i += 5
                wmdata.append(wm)
            
            wmdata = sorted(wmdata, key = lambda wm: wm.id) # sort by ID (Wiimote 1 appears first)
            extradata = "" if i >= len(data) else ','.join(data[i:]).replace("\\n", "\n")
            return (wmdata, extradata)
        except Exception:
            raise ValueError(f"Invalid format parsing wiimote data from `{csv_line}`")
