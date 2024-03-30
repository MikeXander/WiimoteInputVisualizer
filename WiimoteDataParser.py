# TODO: better errors (invalid length, invalid specific entries), parse more

# this is for converting 1 line in the csv output from
# the lua script into a standardized data type
class WiimoteData:
    def __init__(self, info: str):
        try:
            data = info.strip().split(',')
            self.frame = int(data[0]) # this isnt necessarily wiimote data but it's important here
            self.report_type = 0x0
            self.buttons = data[1].strip().split(' ') # list of uppercase button names that are pressed
            self.ir = (0, 0)
            self.acc = (512, 512, 616) # default: pointing at screen
            self.stick = (128, 128)
            self.nacc = (512, 512, 716)
        except Exception:
            raise ValueError(f"Invalid format parsing wiimote data from `{info}`")
