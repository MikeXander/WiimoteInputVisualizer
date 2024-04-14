import pygame
from math import sin, cos, atan2

# TODO
# 1. joystick draw stick
# 2. enable-bounding-box joystick option
# 3. IR(LayoutElement)
# 4. allow different colour components within a LayoutElement
# 5. pixel slight transparency. This might be able to be fixed already by changing the images?

# If all RGB values of a pixel are < Texture.TRANSPARENT_THRESHOLD, they are set to transparent
# If any RGB values are < 0, the colour in the config is ignored (the transparent clamp above still happens)

class Texture:
    TRANSPARENT_THRESHOLD = 25

    def __init__(self, image_filename: str):
        self.name = image_filename
        self.pos = (0, 0)
        self.colour = (255, 255, 255)

        self.img = pygame.image.load("./Textures/" + image_filename).convert()
        self.img.set_colorkey((0, 0, 0))
        pygame.Surface.convert_alpha(self.img)

    def draw(self, frame: pygame.Surface):
        if self.pos[0] < 0 or self.pos[1] < 0: # don't draw if a coordinate is negative
            return frame
        frame.blit(self.img, self.pos)
        return frame

    def reload(self, position, RGB):
        self.pos = position
        self.colour = RGB
        self.reload_img_colour()
    
    def reload_img_colour(self):
        w, h = self.img.get_size()
        r, g, b = self.colour
        for x in range(w):
            for y in range(h):
                pixel = self.img.get_at((x, y))
                if all(v < Texture.TRANSPARENT_THRESHOLD for v in pixel[:3]):
                    self.img.set_at((x, y), pygame.Color(0, 0, 0, 0))
                elif all(v >= 0 for v in self.colour):
                    self.img.set_at((x, y), pygame.Color(r, g, b, pixel[3]))


# these elements contain data that can change how it's drawn
class LayoutElement:
    def __init__(self):
        pass
    
    # draw this element to the frame
    def draw(self, frame: pygame.Surface):
        raise NotImplementedError()
    
    # refresh information (position, colour, etc.)
    def reload(self, settings: str):
        raise NotImplementedError()
    
    # read space separated integer data from a string
    # ignores non-numbers (and allows negatives)
    @staticmethod
    def _read_data(settings: str):
        data = map(
            int,
            filter(
                lambda x: x.lstrip('-').isdigit(),
                settings.strip().split(' ')
            )
        )
        return list(data)


class Button(LayoutElement):
    def __init__(self, name):
        super().__init__()
        self.pressed = Texture(name + "-pressed.png")
        self.released = Texture(name + "-released.png")
        self.name = name
        self.is_pressed = False
    
    def draw(self, frame: pygame.Surface):
        if self.is_pressed:
            return self.pressed.draw(frame)
        return self.released.draw(frame)
    
    def reload(self, settings: str):
        data = self._read_data(settings)
        if len(data) < 5:
            raise ValueError(f"Invalid button settings. Expected `x y R G B` but received `{settings}`")
        pos = (data[0], data[1])
        colour = (data[2], data[3], data[4])
        self.pressed.reload(pos, colour)
        self.released.reload(pos, colour)


class DPad(LayoutElement):
    def __init__(self):
        super().__init__()
        self.rotation = 0
        self.gate = Texture("d-pad-gate.png")
        self.directions = [
            Texture("d-pad-up.png"),
            Texture("d-pad-right.png"),
            Texture("d-pad-down.png"),
            Texture("d-pad-left.png")
        ]
        self.pressed = [False] * 4
    
    def draw(self, frame: pygame.Surface):
        frame = self.gate.draw(frame)
        for i in range(4):
            if self.pressed[i]:
                frame = self.directions[(i + self.rotation) % 4].draw(frame)
        return frame

    def reload(self, settings: str):
        data = self._read_data(settings)
        if len(data) < 6:
            raise ValueError(f"Invalid dpad settings. Expected `rotation x y R G B` but received `{settings}`")
        self.rotation = data[0]
        pos = (data[1], data[2])
        colour = (data[3], data[4], data[5])
        for texture in [self.gate] + self.directions:
            texture.reload(pos, colour)


class Joystick(LayoutElement):
    # Expects joystick values to range from 0 to max_stick_value
    # This will be used to normalize the stick and draw the line
    # (0,0) will be drawn on the bottom left edge of the joystick-gate
    def __init__(self, max_stick_value=255, thickness = 1.5):
        super().__init__()
        self.gate = Texture("joystick-gate.png")
        self.thickness = thickness
        self.stick = (128, 128)
        self.mag = max_stick_value
        self.stick_colour = (255, 255, 255)
        self.enablebb = False

    # return x,y as floats from -1 to 1
    def get_norm_stick(self):
        half = (self.mag + 1) // 2
        return (
            (self.stick[0] - half) / self.mag,
            (self.stick[1] - half) / self.mag
        )

    def draw(self, frame: pygame.Surface):
        frame = self.gate.draw(frame)

        # setup coordinates
        x, y = self.get_norm_stick()
        w, h = self.gate.img.get_size()
        start = (self.gate.pos[0] + w / 2, self.gate.pos[1] + h / 2)

        # need to flip y-coord
        # also not sure why it's not w/2, h/2...
        end = (start[0] + x * w, start[1] - y * h)

        if self.enablbb: # draw the boundingbox outside what the stick will draw
            posx, posy = self.gate.pos
            offset = 2
            pygame.draw.rect(
                frame,
                self.gate.colour,
                pygame.Rect((posx - offset, posy - offset), (w + 2 * offset, h + 2 * offset)),
                1
            )
        
        # draw the stick
        # draw aaline with thickness: https://stackoverflow.com/questions/30578068/pygame-draw-anti-aliased-thick-line
        center = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
        length = ((end[0] - start[0])**2 + (end[1] - start[1])**2)**0.5
        angle = atan2(start[1] - end[1], start[0] - end[0])
        UL = (
            center[0] + (length/2.) * cos(angle) - self.thickness * sin(angle),
            center[1] + self.thickness * cos(angle) + (length/2.) * sin(angle)
        )
        UR = (
            center[0] - (length/2.) * cos(angle) - self.thickness * sin(angle),
            center[1] + self.thickness * cos(angle) - (length/2.) * sin(angle)
        )
        BL = (
            center[0] + (length/2.) * cos(angle) + self.thickness * sin(angle),
            center[1] - self.thickness * cos(angle) + (length/2.) * sin(angle)
        )
        BR = (
            center[0] - (length/2.) * cos(angle) + self.thickness * sin(angle),
            center[1] - self.thickness * cos(angle) - (length/2.) * sin(angle)
        )
        pygame.draw.polygon(frame, self.stick_colour, (UL, UR, BR, BL))

        # draw circles on either end of the stick to round it off
        pygame.draw.circle(frame, self.stick_colour, start, self.thickness)
        pygame.draw.circle(frame, self.stick_colour, end, 1.25 * self.thickness)

        return frame

    def reload(self, settings: str):
        data = self._read_data(settings)
        if len(data) < 5:
            raise ValueError(f"Invalid joystick settings. Expected `enable_bounding_box x y R G B` but received `{settings}`")
        self.enablbb = bool(int(data[0]))
        pos = (data[1], data[2])
        colour = (data[3], data[4], data[5])
        self.gate.reload(pos, colour)


class IR(LayoutElement):
    # x ranges from 0 to 1023 (left to right)
    # y ranges from 0 to 767 (top to bottom) (lowest puts it at 1023 for some reason)
    def __init__(self, width=100, x=0, y=0):
        super().__init__()
        self.width = width # in px
        self.pos = (x, y) # top left
        self.cursor_pos = (0, 0)
    
    def draw(self, frame: pygame.Surface):
        # draw rect for bounding box
        # draw dot for cursor
        return frame
    
    def reload (self, settings: str):
        data = self._read_data(settings)
        if len(data) < 8:
            raise ValueError(f"Invalid IR settings. Expected `x y bounding_box_RGB cursor_RGB` but received `{settings}`")
