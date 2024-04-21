from LayoutElements import LayoutElement, Button, DPad, Joystick, IR
from WiimoteDataParser import WiimoteData
import pygame
from typing import List

# TODO: handle report type switching

# to use the same layout repeatedly you can define a child class
# or just define your own layout (with coresponding config file)
# note: the config (.layout) files are just textfiles
# example usage:
"""
p1 = WiimoteLayout()
# or
p2 = Layout([Button("A"), DPad()], "my_controller.layout")
"""

# A collection of LayoutElements (a controller button layout)
# - This interfaces WiimoteData with each LayoutElement
# - the lines in the config file corresponds to the elements in the layout (in the order they're defined)
class Layout:
    ANY_REPORT_TYPE = -1

    def __init__(self, elements: List[LayoutElement] = [], config_filepath: str = "", report_type = None):
        self.elements = elements
        self.config = config_filepath
        self.report_type = report_type or Layout.ANY_REPORT_TYPE
        self.reload()

    def set_inputs(self, data: WiimoteData):
        # check report type and switch self if it changes? (currently assumes extensions dont change)
        second_stick = False # first joystick element is primary stick
        for element in self.elements:
            if isinstance(element, Button):
                element.is_pressed = element.name in data.buttons
            elif isinstance(element, DPad):
                element.pressed = (
                    "UP" in data.buttons,
                    "RIGHT" in data.buttons,
                    "DOWN" in data.buttons,
                    "LEFT" in data.buttons
                )
            elif isinstance(element, Joystick):
                if second_stick:
                    element.stick = data.rstick
                else:
                    element.stick = data.stick
                    second_stick = True
            elif isinstance(element, IR):
                element.cursor_pos = data.ir
    
    def draw(self, frame: pygame.Surface):
        for element in self.elements:
            frame = element.draw(frame)
        return frame

    # first line of the layout file is window size and background colour
    # returns the data from the first line: (width, height), (r, g, b)
    # returns None, None if there's an error
    def reload(self):
        if len(self.elements) == 0 or self.config == "":
            return None, None
        
        config = []
        with open(self.config, 'r') as f:
            config = list(filter(lambda line: line != '\n', f.readlines()))
        
        if len(config) != len(self.elements) + 1:
            print(f"[ERROR] Config file {self.config} has incorrect number of lines")
            return None, None
        
        for element, settings in zip(self.elements, config[1:]):
            element.reload(settings)    
        
        data = LayoutElement._read_data(config[0])
        if len(data) < 5:
            return None, None
        size = (data[0], data[1])
        if min(size) <= 0:
            size = None
        bgcol = (data[2], data[3], data[4])
        if min(size) < 0:
            bgcol = None
        return size, bgcol

class WiimoteLayout(Layout):
    def __init__(self, config_filepath: str = "./Layouts/wiimote.layout"):
        super().__init__([
            Button("A"),
            Button("B"),
            Button("1"),
            Button("2"),
            Button("+"),
            Button("-"),
            Button("HOME"),
            DPad()
        ],
        config_filepath
        )

class NunchukLayout(Layout):
    def __init__(self, config_filepath: str = "./Layouts/nunchuk.layout"):
        super().__init__([
            Button("A"),
            Button("B"),
            Button("1"),
            Button("2"),
            Button("+"),
            Button("-"),
            Button("HOME"),
            DPad(),
            Button("C"),
            Button("Z"),
            Joystick()
        ],
        config_filepath
        )

class ClassicLayout(Layout):
    def __init__(self, config_filepath: str = "./Layouts/classic.layout"):
        super().__init__([
            Button("A", "A2"),
            Button("B", "B2"),
            Button("X"),
            Button("Y"),
            Button("L"),
            Button("ZL"),
            Button("R"),
            Button("ZR"),
            Button("+"),
            Button("-"),
            Button("HOME"),
            DPad(),
            Joystick(63),
            Joystick(31)
        ],
        config_filepath
        )
