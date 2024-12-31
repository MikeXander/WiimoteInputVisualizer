# WiimoteInputVisualizer
This is a set of scripts for reading wiimote controller data from RAM in Dolphin Emulator and either displaying the inputs in real-time or encoding a video of a TAS with an input overlay.

For a generalized wiimote input visualizer that works on console, see my [WiimoteEmulator](https://github.com/MikeXander/WiimoteEmulator).

This was inspired by [this gamecube input display](https://github.com/bkacjios/m-overlay) and uses their textures as the base for the textures here.

Here is an example produced by these scripts:

https://github.com/user-attachments/assets/e50bfb22-724b-4a43-b7f8-9fe80746e8f4

An example of the live display, also displaying additional data (like in-game speed values), can be seen in my [Super Mario Galaxy Introductory Movement Tutorial](https://youtu.be/95qLMrX08SY?si=O-1JVK16MLTnSvNZ).

## Setup
1. Download and install [python 3](https://www.python.org/downloads/)
   - Make sure to add python to your PATH when given the option
2. Install the required python libraries
    - First, open a command prompt inside the folder containing these files
      - This can be done by opening a command prompt and then navigating to this folder with the command `cd /path/to/WiimoteInputVisualizer`
      - Or, if you're using Windows, navigate to the folder in the File Explorer, and in the top left click `File > Open Windows PowerShell`
    - Then, run `python -m pip install -r requirements.txt`

Additionally, to encode a video with the input overlay at perfect 60fps (this will only work with TASes made on Dolphin 5.0):
1. Download and open [Dolphin 5.0 Lua Core (Wiimote Version)](https://github.com/MikeXander/Dolphin-Lua-Core/releases)
    - Note: make sure youre on the latest version or the lua scripts wont work. If you have a previous version of Dolphin-Lua, all you need to do is replace Dolphin.exe
2. Move both of the lua scripts from `./Dolphin Scripts/` to `/Dolphin/Sys/Scripts/`
3. Download [FFmpeg](https://www.ffmpeg.org/download.html) and add it to your PATH

## Viewing Inputs in Real-Time
Open up your game in any version of Dolphin Emulator, then run `LiveDisplay.py` or `LiveDisplay3D.py`. It's that easy!

If you are unfamiliar with running python scripts, just search it up on the internet. There are many resources on how to do it which are explained better than what I could come up with.

Note: during live display (2D), if the input display window is in focus, pressing Ctrl+R will reload the layout, and Ctrl+S will start recording a video of the inputs (press again to stop recording, and save `output.mp4`).

## Customizing the Layouts
Basic changes to the provided layouts are done by editing various text files. A little bit of python knowledge is useful but not required.

#### Setting the controller extensions
There are 3 supported modes: no extension, nunchuk, and classic controller.

To set the type of controller to display and the layout you want to use, edit the following lines in `LiveDisplay.py`:

```
encoder.set_layouts([
    NunchukLayout("./Layouts/smg_p1.layout"),
    WiimoteLayout("./Layouts/smg_p2.layout")
])
```
As is, this will display the nunchuk buttons for P1 using the `smg_p1` layout and the standard buttons for P2 using the `smg_p2` layout. Some changes you could make are:
- changing `NunchukLayout` to `ClassicLayout` to show classic controller buttons
- changing `"./Layouts/smg_p2.layout"` to `"./Layouts/wiimote.layout"` to use the `wiimote` layout
- Adding a comma after the second layout, and putting in another `WiimoteLayout(...)` to show inputs for a 3rd controller

You can make your own layout files and use those too, just make sure that they follow the same format as `wiimote.layout`, `nunchuk.layout`, and `classic.layout`.

Also, the window size of the visualizer and the background colour will match that of the last layout (i.e. window size in P4's layout takes priority over P3).

#### Changing colours/positions of buttons
The layout files contained in the `./Layouts/` folder can be directly edited as text files to change the positions and colours of buttons. Here is a brief description of some of the options:
- xy: the (x,y) position measured from the top left. If any coordinate is negative, the button will be hidden from the layout.
- RGB: the RGB values from 0-255 to colour the button.
- Joystick enable bounding box: this is the square around the octagonal joystick gate. A value of 0 means hide it, 1 means show it. 
- DPad rotation: this is a value from 0-3 that changes which button is displayed as "up". If the wiimote is held in the upright position, a value of 0 corresponds to DPad Up pointing up, a value of 3 corresponds to DPad Right pointing up. This correspondence may change if the controller is set to horizontal wiimote inside the Dolphin controller settings.

#### Changing the images used for buttons
To change the base textures, you can replace any of the images in the `./Textures/` folder with your own. Keep in mind:
- Any pixel value darker than #191919 is set to transparent
- Currently, buttons will always be set to a solid colour, although they will match the transparency of the png provided (the alpha value is preserved)
- You will need to close and re-run the visualizer to see changes made to the base textures.

#### Adding on-screen text (displaying speed, joystick coordinates, etc.)
Additional information is added on a per-game basis. Scroll down to the **Extending Use To Other Games** section to see how to set this up.

To change the position, colour, font, and fontsize of the text, edit the options directly at the bottom of `LiveDisplay.py`. The font defaults to arial, but I personally recommend [Delfino](https://fontmeme.com/fonts/delfino-font/).

#### 3D Display Modes
There are too many degrees of freedom to perfectly visualize an arbitrary wiimote without assumptions (without having gyro information). By default it is set to the `WiimoteType3D.UPRIGHT` position, but you can edit `LiveDisplay3D.py` to use `WiimoteType3D.SIDEWAYS` instead.

The 3D display script is more of a proof of concept that gives a rough idea of how the wiimote is held.


## Encoding a Video with Inputs
My process for adding an input overlay and encoding a TAS at the same time is this:
1. Edit `Export_Wiimote_Inputs.lua` and `Encode.lua` to specify start and end frames (and optionally the filename of the input data).
2. Playback your TAS, and run both lua scripts.
3. Edit `SaveVideo.py` to contain your desired controller layouts, and point to the input data (which is named `_inputs.csv` by default and is created in the same directory as your Dolphin.exe).
4. Run `SaveVideo.py` to create a video of the input overlay.
5. Combine the input overlay and the TAS encode into one video.

For the final step, I recommend removing the background, and adding a small drop shadow to the overlay so that the inputs stand out. This can be done with any video editing software or with the following FFmpeg command:
```
ffmpeg -i input_overlay.mp4 -i background_footage.mp4 -filter_complex "[0:v]colorkey=color=#000000:similarity=0.1:blend=0.1[removed_bg];[removed_bg]split[inputs][shadow];[shadow]format=rgba,colorchannelmixer=aa=0.9:rr=0:gg=0:bb=0,scale=iw:ih,boxblur=3:1[drop_shadow];[1:v][drop_shadow]overlay=x=0:y=3[bg_with_shadow];[bg_with_shadow][inputs]overlay=x=3:y=0" -c:v libx264 output.mp4
```
Alternatively, if you don't want to add a drop shadow, and only want to remove the background, the videos can be joined with:
```
ffmpeg -i background_footage.mp4 -i input_overlay.mp4 -filter_complex "[1:v]colorkey=color=#000000:similarity=0.1:blend=0.1[inputs];[0:v][inputs]overlay" -c:v libx264 output.mp4
```
If you are unfamiliar with FFmpeg, the key things to note about those commands are:
- the input video files are named `input_overlay.mp4` and `background_footage.mp4`
- `color=#000000` specifies the background RGB colour (in hexadecimal) to make transparent
- they output to `output.mp4`

#### :warning: Keep in mind that this tool is designed for short segments
- The inputs are likely to desync from the gameplay when encoding across loading zones because lag frames are ignored in the lua scripts
- The input display encodes at 60fps which will desync overtime from gameplay that runs at 59.94fps 


## Additional Uses
The `Export_Wiimote_Inputs.lua` script generates a list of all your input data (once per frame) in a more readable format than DTMs. Using this, you could check various statistics about your inputs. See `ButtonPressStats.py` for an example.

## Extending Use To Other Games

This can be used to visualize and encode the inputs for any wii game. To do this, you will need to write an equivalent "core" for your respective game. To do this, create a new file in the `./Cores/` folder named with the appropriate [GAMEID](https://www.gametdb.com/Wii/list) and find/read the inputs and desired information that is stored in RAM.

A template file, `./Cores/GAMEID.py` might look something like this: 
```
import dolphin_memory_engine as dme
from typing import List
from sys import path
path.insert(0, '..')
from WiimoteDataParser import WiimoteTypes, WiimoteData

def get_controller_data() -> List[WiimoteData]:
    return [
      WiimoteData(
        ...
      )
    ]

def get_additional_data() -> str:
    return ""
```

Use the other core files as references for how to read RAM using DME in python.

#### :warning: Ensure that your controller data is in the proper ranges.
Many games will store processed input in RAM. For example: storing the nunchuk stick as a float from -1.0 to 1.0 or the accelerometer data as an integer from -512 to 511. To display these inputs properly, they must be converted to the expected ranges. In this case, an integer from 0 to 255 for the nunchuk stick, or an integer from 0 to 1023 for the accelerometer data. 

For details on the valid ranges for `WiimoteData`, see the default values in `WiimoteDataParser.py`. You can also look at the other core files as examples, or report an issue here on GitHub for me to add support for your game.

## Future Improvements (To do):
- option to NOT recolour textures and take them at face ARGB value (ignore like position)
- re-implement encoding videos with additional data
- allow saving videos with multiple layouts (have the layout change if the number of controllers changes)
- default layouts per controller type, and automatically switch to game specific layouts
- Output data for lag frames too
- Add a mini IR display layout element
- Add multiple controllers to the 3D display
- Use frame buffers in the 3D display so it can be encoded like the 2D display
