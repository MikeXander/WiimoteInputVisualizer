import dolphin_memory_engine as dme

dme.hook()
GAMEID = dme.read_bytes(0x0, 6).decode("utf-8") # requires Dolphin is already open

intb = lambda x: int.from_bytes(x, "big")
dme.read_int = lambda x: intb(dme.read_bytes(x, 4))

# input coords aand processed value as a float from -1.0 to 1.0 inclusive
def stick():
    return {
        "X_processed": dme.read_float(0xB38A8C),
        "Y_processed": dme.read_float(0xB38A90)
    }

# accel values from -512 to 511
def wiimote_accel():
    offset = 0x792C82
    adjust = lambda x: x if x <= 511 else -1 * (0xFFFF - x + 1)
    read_accel = lambda addr: adjust(intb(dme.read_bytes(addr, 2)))
    return {
        "X": read_accel(offset + 0x0),
        "Y": read_accel(offset + 0x2),
        "Z": read_accel(offset + 0x4)
    }

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

