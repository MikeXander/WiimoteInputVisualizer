import dolphin_memory_engine as dme
from typing import List
from sys import path
path.insert(0, '..')
from WiimoteDataParser import WiimoteTypes, WiimoteData

dme.hook() # requires Dolphin is already open
intb = lambda x: int.from_bytes(x, "big")
dme.read_int = lambda x: intb(dme.read_bytes(x, 4))

# This is the important function for the core to output
# returns the list of controller data to visualize inputs for
def get_controller_data() -> List[WiimoteData]:
    try:
        stage_time = get_stage_time()
        p1_btns, p2_btns = get_buttons()
        P1 = WiimoteData(
            frame = stage_time,
            id = 4,
            extension_type = WiimoteTypes.NUNCHUK,
            buttons = set(p1_btns),
            acc = get_wiimote_accel(),
            stick = get_stick(True)
        )
        P2 = WiimoteData(
            frame = stage_time,
            id = 5,
            extension_type = WiimoteTypes.WIIMOTE,
            buttons = p2_btns
        )
        return [P1, P2]
    except Exception as err:
        print("Failed to read from Dolphin")
        raise err

# returns a string of text with extra info to draw to the screen
def get_additional_data() -> str:
    vx, vy, vz = speed()
    vxz = (vx**2 + vz**2)**0.5
    
    stick = "x: %d\ny: %d" % get_stick(True)
    hspd = "HSpd: %.3f" % round(vxz, 3)
    _, vy, _ = base_velocity()
    yspd = "\nYSpd: %.3f" % vy if vy != 0 else "\nYSpd: 0.000"
    y = "\nY: %.3f" % previous_position()[1]
    text = stick #+ hspd + y
    return text

# ============================================================== #
#  SMG1 specific functions for reading controller data from RAM  #
# ============================================================== #

# in-level frame count (resets to 0 on death)
def get_stage_time():
    return dme.read_int(0x9ADE58)

# input coords (0-255) or processed value (float from -1.0 to 1.0)
def get_stick(get_stick_coords: bool):
    if get_stick_coords:
        return (dme.read_byte(0x661210) + 128) % 256, (dme.read_byte(0x661211) + 128) % 256
    return dme.read_float(0x61D3A0), dme.read_float(0x61D3A4)

# x,y,z accel values from 0 to 1023
def get_wiimote_accel() -> List[int]:
    offset = 0x661242
    adjust = lambda x: x if x <= 511 else -1 * (0xFFFF - x + 1)
    read_accel = lambda addr: adjust(intb(dme.read_bytes(addr, 2))) + 512
    return (
        read_accel(offset + 0x0),
        read_accel(offset + 0x2),
        read_accel(offset + 0x4)
    )

# returns the list of buttons being pressed
# includes all P1 buttons, and only A/B for P2
def get_buttons() -> List[List[str]]:
    btns = [[], []]
    data = intb(dme.read_bytes(0x61D342, 2))
    if data & 0x0001: btns[0].append("LEFT")
    if data & 0x0002: btns[0].append("RIGHT")
    if data & 0x0004: btns[0].append("DOWN")
    if data & 0x0008: btns[0].append("UP")
    if data & 0x0010: btns[0].append("+")
    if data & 0x0100: btns[0].append("2")
    if data & 0x0200: btns[0].append("1")
    if data & 0x0400: btns[0].append("B")
    if data & 0x0800: btns[0].append("A")
    if data & 0x1000: btns[0].append("-")
    if data & 0x2000: btns[0].append("Z")
    if data & 0x4000: btns[0].append("C")
    if data & 0x8000: btns[0].append("HOME")
    data = dme.read_byte(0x61EF3A)
    if data & 0x04: btns[1].append("B")
    if data & 0x08: btns[1].append("A")
    return btns

# ================================================ #
#  SMG1 specific functions for reading extra data  #
# ================================================ #

def valid_address(addr):
    if addr >= 0x80000000:
        addr -= 0x80000000
    return 0x0 <= addr <= 0x17FFFFF or 0x10000000 <= addr <= 0x13FFFFFF

# returns the address stored in location ptr_addr
def get_pointer_value(ptr_addr):
    return dme.read_word(ptr_addr) - 0x80000000

# Most addresses are offset from this pointer
def reference_pointer():
    GAMEID = dme.read_bytes(0x0, 6).decode("utf-8")
    if GAMEID == "RMGJ01":
        return get_pointer_value(0xF8F328)
    elif GAMEID in ["RMGE01", "EMGP01"]:
        return get_pointer_value(0xF8EF88)
    else:
        return -1

def read_from_ref(offset, read_function):
    if not valid_address(reference_pointer()):
        return 0
    return read_function(reference_pointer() + offset)

def read_triple(offset):
    return (
        read_from_ref(offset, dme.read_float),
        read_from_ref(offset + 0x4, dme.read_float),
        read_from_ref(offset + 0x8, dme.read_float)
    )

def position():
    return read_triple(0x3EEC)

def previous_position():
    return read_triple(0x18DC)

# based off in-game change in position
def speed():
    p1 = previous_position()
    p2 = position()
    return p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]

# in-game velocity observed on next frame
# displacement from moving platforms and launch stars are not accounted for
def base_velocity():
    return read_triple(0x3EEC + 0x78)
