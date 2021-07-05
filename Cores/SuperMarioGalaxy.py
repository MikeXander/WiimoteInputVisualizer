import dolphin_memory_engine as dme

dme.hook()
GAMEID = dme.read_bytes(0x0, 6).decode("utf-8") # requires Dolphin is already open
POS_OFFSET = 0x3EEC

intb = lambda x: int.from_bytes(x, "big")
dme.read_int = lambda x: intb(dme.read_bytes(x, 4))

def valid_address(addr):
    if addr >= 0x80000000:
        addr -= 0x80000000
    return 0x0 <= addr <= 0x17FFFFF or 0x10000000 <= addr <= 0x13FFFFFF

# returns the address stored in location ptr_addr
def get_pointer_value(ptr_addr):
    return dme.read_word(ptr_addr) - 0x80000000

# Most addresses are offset from this pointer
def reference_pointer():
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
    return {
        "X": read_from_ref(offset, dme.read_float),
        "Y": read_from_ref(offset + 0x4, dme.read_float),
        "Z": read_from_ref(offset + 0x8, dme.read_float),
    }

def position():
    return read_triple(POS_OFFSET)

def previous_position():
    return read_triple(0x18DC)

# based off in-game change in position
def speed():
    p1 = previous_position()
    p2 = position()
    speed = {
        "X": p2["X"] - p1["X"],
        "Y": p2["Y"] - p1["Y"],
        "Z": p2["Z"] - p1["Z"]
    }
    speed["XZ"] = (speed["X"]**2 + speed["Z"]**2) ** 0.5
    speed["XYZ"] = (speed["X"]**2 + speed["Y"]**2 + speed["Z"]**2) ** 0.5
    return speed

def text_info():
    addr = get_pointer_value(0x9A9240)
    if addr == 0:
        return {
            "text_progress": 0,
            "alpha_req": 0,
            "fade-rate": 0
        }
    return {
        "text_progress": dme.read_word(addr + 0x2D39C),
        "alpha_req": dme.read_word(addr + 0x2D3B0),
        "fade-rate": dme.read_word(addr + 0x2D3B4)
    }

def set_position(x, y, z):
    if valid_address(reference_pointer()):
        addr = reference_pointer() + 0x18DC
        dme.write_float(addr, x)
        dme.write_float(addr + 0x4, y)
        dme.write_float(addr + 0x8, z)

# change the player's position relative to their current position
def change_position(dx, dy, dz):
    pos = position()
    set_position(pos["X"] + dx, pos["Y"] + dy, pos["Z"] + dz)

# input coords aand processed value as a float from -1.0 to 1.0 inclusive
def stick():
    return {
        "X": (dme.read_byte(0x661210) + 128) % 256,
        "Y": (dme.read_byte(0x661211) + 128) % 256,
        "X_processed": dme.read_float(0x61D3A0),
        "Y_processed": dme.read_float(0x61D3A4)
    }

# accel values from -512 to 511
def wiimote_accel():
    offset = 0x661242
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
    byte = intb(dme.read_bytes(0x61D342, 2))
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
    byte = dme.read_byte(0x61EF3A)
    if byte & 0x04: data["P2"].append("B")
    if byte & 0x08: data["P2"].append("A")
    return data

# in-game velocity
# displacement from moving platforms and launch stars are not accounted for
# this is the velocity that's observed on the NEXT frame
def base_velocity():
    return read_triple(POS_OFFSET + 0x78)

def predicted_next_position():
    vel = base_velocity()
    pos = position()
    return {
        "X": pos["X"] + vel["X"],
        "Y": pos["Y"] + vel["Y"],
        "Z": pos["Z"] + vel["Z"]
    }

# direction of gravity
def down_gravity():
    return read_triple(0x1B10)

# this is just a positive version of gravity
def up_gravity():
    return read_triple(0x6A3C)

# This can be different from upwards gravity
def tilt():
    return read_triple(POS_OFFSET + 0xC0)

def state():
    if not valid_address(reference_pointer()):
        return "0".zfill(32)
    addr = reference_pointer() + POS_OFFSET - 0x128
    data = dme.read_bytes(addr, 32)
    return bin(intb(data))[2:].zfill(32)

def on_ground():
    return state()[2] == "1"

# This appears to be an in-game timer
# It counts up by 1 per frame starting from the level-beginning cutscenes.
# It also pauses for a few frames when you get the star.
# It resets to 0 if you die.
def stage_time():
    return dme.read_int(0x9ADE58)

# Shake related info
def wiimote_shake():
    return read_from_ref(0x27F0, dme.read_byte)

def nunchuck_shake():
    return read_from_ref(0x27F1, dme.read_byte)

def spin_cooldown_timer():
    return read_from_ref(0x2217, dme.read_byte)

def spin_attack_timer():
    return read_from_ref(0x2214, dme.read_byte)

# Value is 180 when inactive
def midair_spin_timer():
    return read_from_ref(0x41BF, dme.read_byte)

def midair_spin_type():
    return read_from_ref(0x41E7, dme.read_byte)

# Types include:
# Jump, double jump or rainbow star jump, triple jump,
# bonk or forward facing slope jump, sideflip, long jump, backflip, wall jump,
# midair spin, ?, ledge hop, spring topman bounce, enemy bounce,
# jump off swing / pull star release / after planet landing / spin out of water
def last_jump_type():
    return read_from_ref(0x41EF, dme.read_byte)

def ground_turn_timer():
    return read_from_ref(0x41CB, dme.read_byte)

def file_starbits():
    return dme.read_int(0xF63CF4)

def rotation(): # 0x18E8 ?
    temp = read_triple(0x18DC + 0xC)
    return {
        "AngleA": temp["X"],
        "AngleB": temp["Y"],
        "AngleC": temp["Z"]
    }

'''
def angle():
    return dme.read_float(reference_pointer() + 0x3FC4)
'''

def nunchuk_encryption_key(): # Found by BillyWAR
    addr = 0x661AC4
    key = ""
    for i in range(16):
        key += "%02X " % dme.read_byte(addr + i)
    return key[:-1]
