import pygame

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
            print(f"[ERROR] Invalid button settings. Expected `x y R G B` but received `{settings}`")
            return
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
            print(f"[ERROR] Invalid dpad settings. Expected `rotation x y R G B` but received `{settings}`")
            return
        self.rotation = data[0]
        pos = (data[1], data[2])
        colour = (data[3], data[4], data[5])
        for texture in [self.gate] + self.directions:
            texture.reload(pos, colour)


class Joystick(LayoutElement):
    # Expects joystick values to range from 0 to max_stick_value
    # This will be used to normalize the stick and draw the line
    # (0,0) will be drawn on the bottom left edge of the joystick-gate
    def __init__(self, max_stick_value=255, thickness = 3):
        super().__init__()
        self.gate = Texture("joystick-gate.png")
        self.thickness = thickness
        self.stick = (128, 128)
        self.mag = max_stick_value
        self.stick_colour = (255, 255, 255)

    # return x,y as floats from -1 to 1
    def _norm_stick(self):
        half = (self.mag + 1) // 2
        return (
            (self.stick[0] - half) / self.mag,
            (self.stick[1] - half) / self.mag
        )

    def draw(self, frame: pygame.Surface):
        frame = self.gate.draw(frame)
        # draw stick
        x, y = self._norm_stick()
        w, h = self.gate.img.get_size()
        start = (self.gate.pos[0] + w / 2, self.gate.pos[1] + h / 2)
        end = (start[0] + x * w / 2, start[1] + y * h / 2) # might need to flip y-coord?
        """
        # NOTE: x,y = target_x, target_y
        SCALAR = 58
        global LOCATION
        start = (LOCATION["JOYSTICK"][0] + 62, LOCATION["JOYSTICK"][0] + 78)#98)
        end = (int(x * SCALAR) + start[0], int(-y * SCALAR) + start[1])
        WHITE = pygame.Color(255,255,255)
        #pygame.draw.aaline(frame, WHITE, start, end)

        # draw diagonals around the start and end location
        # a lot of these diagonals end up overlapping (slow)
        offsets = []
        for i in range(1, width):
            for j in range(i, -1, -1):
                offsets.extend([
                    (j, j-i),
                    (-j, i-j),
                    (j, i-j),
                    (-j, j-i)
                ])
        
        for x_offset, y_offset in offsets:
            start_offset = (start[0] + x_offset, start[1] + y_offset)
            end_offset = (end[0] + x_offset, end[1] + y_offset)
            pygame.draw.aaline(frame, WHITE, start_offset, end_offset)
        
        return frame
        """

    def reload(self, settings: str):
        data = self._read_data(settings)
        if len(data) < 5:
            print(f"[ERROR] Invalid joystick settings. Expected `x y R G B` but received `{settings}`")


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
            print(f"[ERROR] Invalid IR settings. Expected `x y bounding_box_RGB cursor_RGB` but received `{settings}`")
