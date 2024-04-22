import dolphin_memory_engine as dme
from sys import path
path.insert(0, '..')
from WiimoteDataParser import WiimoteTypes, WiimoteData

intb = lambda x: int.from_bytes(x, "big")

# accel values from 0 to 1023
def wiimote_accel():
    offset = 0x341572
    adjust = lambda x: x if x <= 511 else -1 * (0xFFFF - x + 1)
    read_accel = lambda addr: adjust(intb(dme.read_bytes(addr, 2))) + 512
    return (
        read_accel(offset + 0x0),
        read_accel(offset + 0x2),
        read_accel(offset + 0x4)
    )

def get_controller_data():
    return [
        WiimoteData(
            id = 5,
            extension_type = WiimoteTypes.WIIMOTE,
            acc = wiimote_accel()
        )
    ]
