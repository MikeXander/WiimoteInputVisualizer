import dolphin_memory_engine as dme

dme.hook()
GAMEID = dme.read_bytes(0x0, 6).decode("utf-8") # requires Dolphin is already open

intb = lambda x: int.from_bytes(x, "big")
dme.read_int = lambda x: intb(dme.read_bytes(x, 4))

def valid_address(addr):
    if addr >= 0x80000000:
        addr -= 0x80000000
    return 0x0 <= addr <= 0x17FFFFF or 0x10000000 <= addr <= 0x13FFFFFF

# returns the address stored in location ptr_addr
def get_pointer_value(ptr_addr):
    return dme.read_word(ptr_addr) - 0x80000000

# accel values from -512 to 511
def wiimote_accel():
    offset = 0x341572
    adjust = lambda x: x if x <= 511 else -1 * (0xFFFF - x + 1)
    read_accel = lambda addr: adjust(intb(dme.read_bytes(addr, 2)))
    return {
        "X": read_accel(offset + 0x0),
        "Y": read_accel(offset + 0x2),
        "Z": read_accel(offset + 0x4)
    }
