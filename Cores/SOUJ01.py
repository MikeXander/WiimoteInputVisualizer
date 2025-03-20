import dolphin_memory_engine as dme
from typing import List
from sys import path
path.insert(0, '..')
from WiimoteDataParser import WiimoteTypes, WiimoteData

intb = lambda x: int.from_bytes(x, "big")
dme.read_int = lambda x: intb(dme.read_bytes(x, 4))

# This is the important function for the core to output
# returns the list of controller data to visualize inputs for
def get_controller_data() -> List[WiimoteData]:
    try:
        frame = get_frame()
        p1_btns = get_buttons()
        P1 = WiimoteData(
            frame=frame,
            id = 4,
            extension_type = WiimoteTypes.NUNCHUK,
            buttons = set(p1_btns),
            acc = get_wiimote_accel(),
            stick = get_stick(True)
        )
        return [P1]
    except Exception as err:
        print("Failed to read from Dolphin")
        raise err

# in-game frame count
def get_frame():
    return dme.read_int(0X80578EC0)

# input coords (0-255) or processed value (float from -1.0 to 1.0)
def get_stick(get_stick_coords: bool):

    lr, ud = dme.read_float(0x8059AD10), dme.read_float(0x8059AD14)

    if get_stick_coords:
        return int((lr + 1) * 128), int((ud + 1) * 128)
    return lr, ud 

# returns the list of buttons being pressed
def get_buttons() -> List[List[str]]:
    btns = []
    data = intb(dme.read_bytes(0x8059CF8C, 2))
    if data & 0x0100: btns.append("2")
    if data & 0x0200: btns.append("1")
    if data & 0x0400: btns.append("B")
    if data & 0x0800: btns.append("A")
    if data & 0x1000: btns.append("-")
    if data & 0x2000: btns.append("Z")
    if data & 0x4000: btns.append("C")
    if data & 0x8000: btns.append("HOME")
    if data & 0x0001: btns.append("LEFT")
    if data & 0x0002: btns.append("RIGHT")
    if data & 0x0004: btns.append("DOWN")
    if data & 0x0008: btns.append("UP")
    if data & 0x0010: btns.append("+")
    return btns

# x,y,z accel values from 0 to 1023
def get_wiimote_accel() -> List[int]:
    offset = 0x8059CF8E
    adjust = lambda x: x if x <= 511 else -1 * (0xFFFF - x + 1)
    read_accel = lambda addr: adjust(intb(dme.read_bytes(addr, 2))) + 512
    return (
        read_accel(offset + 0x0),
        read_accel(offset + 0x2),
        read_accel(offset + 0x4)
    )