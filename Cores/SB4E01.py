import dolphin_memory_engine as dme
from sys import path
path.insert(0, '..')
from WiimoteDataParser import WiimoteTypes, WiimoteData

intb = lambda x: int.from_bytes(x, "big")

# input coords (0-255) or processed value (float from -1.0 to 1.0)
def get_stick(get_stick_coords: bool):
    if get_stick_coords:
        return (dme.read_byte(0x792D10) + 128) % 256, (dme.read_byte(0x792D11) + 128) % 256
    return dme.read_float(0xB38A8C), dme.read_float(0xB38A90)

# accel values from 0 to 1023
def wiimote_accel():
    offset = 0x792C82
    adjust = lambda x: x if x <= 511 else -1 * (0xFFFF - x + 1)
    read_accel = lambda addr: adjust(intb(dme.read_bytes(addr, 2))) + 512
    return (
        read_accel(offset + 0x0),
        read_accel(offset + 0x2),
        read_accel(offset + 0x4)
    )

# returns the list of buttons being pressed
# includes all P1 buttons, and only A/B for P2
def buttons():
    data = {
        "P1": [],
        "P2": []
    }
    byte = intb(dme.read_bytes(0xB38A2E, 2))
    if byte & 0x0001: data["P1"].append("LEFT")
    if byte & 0x0002: data["P1"].append("RIGHT")
    if byte & 0x0004: data["P1"].append("DOWN")
    if byte & 0x0008: data["P1"].append("UP")
    if byte & 0x0010: data["P1"].append("+")
    if byte & 0x0100: data["P1"].append("2")
    if byte & 0x0200: data["P1"].append("1")
    if byte & 0x0400: data["P1"].append("B")
    if byte & 0x0800: data["P1"].append("A")
    if byte & 0x1000: data["P1"].append("-")
    if byte & 0x2000: data["P1"].append("Z")
    if byte & 0x4000: data["P1"].append("C")
    if byte & 0x8000: data["P1"].append("HOME")
    byte = dme.read_byte(0x793860)
    if byte & 0x04: data["P2"].append("B")
    if byte & 0x08: data["P2"].append("A")
    return data

def get_controller_data():
    btns = buttons()
    P1 = WiimoteData(
        id = 4,
        extension_type = WiimoteTypes.NUNCHUK,
        buttons = set(btns["P1"]),
        acc = wiimote_accel(),
        stick = get_stick(True)
    )
    P2 = WiimoteData(
        id = 5,
        extension_type = WiimoteTypes.WIIMOTE,
        buttons = set(btns["P2"])
    )
    return [P1, P2]
