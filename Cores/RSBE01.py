import dolphin_memory_engine as dme
from typing import List, Tuple
from sys import path
path.insert(0, '..')
from WiimoteDataParser import WiimoteTypes, WiimoteData
from math import floor

# NOTE: these memory values are probably dynamic
# i.e. this module does NOT work and will return garbage data right now...

signed = lambda x: x if x < 0x80 else x - 0xFF
dme.read_signed_byte = lambda addr: signed(dme.read_byte(addr))

def get_controller_data() -> List[WiimoteData]:
    return [
        WiimoteData(
            extension_type = WiimoteTypes.CLASSIC,
            buttons = get_buttons(),
            stick = get_left_stick(),
            rstick = get_right_stick()
        )
    ]

def get_buttons() -> List[str]:
    btns = []
    data = int.from_bytes(dme.read_bytes(0x5BAE01, 3))
    if data & 0x000001: btns.append("LEFT")
    if data & 0x000002: btns.append("RIGHT")
    if data & 0x000004: btns.append("DOWN")
    if data & 0x000008: btns.append("UP")
    if data & 0x000100: btns.append("A")
    if data & 0x000200: btns.append("B")
    if data & 0x000400: btns.append("X")
    if data & 0x000800: btns.append("Y")
    if data & 0x101000: btns.append("+")
    if data & 0x080000: btns.append("-")
    if data & 0x000040: btns.append("L")
    if data & 0x000020: btns.append("R")
    if data & 0x004000 and data & 0x10: btns.append("ZL")
    if data & 0x008000 and data & 0x10: btns.append("ZR")
    return btns


# these RAM values range from -100 to 100
# they're adjusted to be the right range for a classic controller test [0, 63] and [0, 31]
coord = lambda x, scale: scale/2 + min(floor(scale * x / 200), scale/2 - 1)

def get_left_stick() -> Tuple[int, int]:
    return (
        coord(dme.read_signed_byte(0x5BAE30), 64),
        coord(dme.read_signed_byte(0x5BAE31), 64)
    )

def get_right_stick() -> Tuple[int, int]:
    return (
        coord(dme.read_signed_byte(0x5BAE32), 32),
        coord(dme.read_signed_byte(0x5BAE33), 32),
    )
