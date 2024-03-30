# WiimoteInputVisualizer
This is a set of scripts that first reads and exports input data from RAM, and then post-processes it to create a video with an input overlay.

This was inspired by [this gamecube input display](https://github.com/bkacjios/m-overlay) and uses their textures as the base for the textures here.

A sample video with the input visualizer can be found here: https://youtu.be/tLIT5Hxa80E
![Sample Image](https://cdn.discordapp.com/attachments/302599698500550659/679752173583859762/SMG_Input_Overlay_Example.png)

### Update (2024)
Currently this is being reworked, the instructions below are partially true, and lots of functionality has been lost. Now, to record a video with a single wiimote that only contains button presses:
1. Download and install requirements below
2. Put `Export_Wiimote_Inputs.lua` inside the Dolphin-Lua scripts folder
3. Run the script, move `_inputs.csv` to the same folder as these scripts
4. Run `SaveVideo.py` (you can edit this script too for a few settings)
To edit the visualizer, you can replace the images in the `Textures` folder (keep the names), and edit `Layouts/wiimote.layout` (these are just text files, note that a negative position will hide a button).

### Old Instructions
To export the input data, you need [Dolphin 5.0 - Lua Core](https://github.com/SwareJonge/Dolphin-Lua-Core/releases). Place `SMG_Core.lua` and `json.lua` in the same folder as `Dolphin.exe`, and place the other scripts in `/Sys/Scripts/`. Then run `SMG_Export_Inputs.lua` from within Dolphin-Lua. Some sample data produced by the lua scripts has been provided.

Once `data.json` has your desired inputs, put it in the same directory as the python scripts and run one of them. Their functions are as follows:
- `SaveVideo.py` will export a recording of the inputs to `output.avi` using the XVID codec by default
- `PlaybackInputVideo.py` will open a window and play through the input
- `LiveDisplay.py` reads inputs directly from Dolphin's RAM and displays them

There are 3 different button press types that display button presses slightly differently. You can change this according to your liking at the top of `WiimoteInputEncoder.py`.

### Requirements:
- [Dolphin 5.0 - Lua Core](https://github.com/SwareJonge/Dolphin-Lua-Core/releases)
- [python 3](https://www.python.org/downloads/)
  - numpy
  - pygame
  - opencv-python
  - pillow
  - dolphin-memory-engine
- Video editing software to combine the overlay and gameplay

### Extending Use To Other Games

This can be used to encode a video of the inputs for other games as well. To do this, you will need to write an equivalent "Core" for your respective game (find and read the inputs/desired information are stored in RAM) and export the controller data in a similar fashion. You will need a lua version to export the data for a video, or a python version for the live display. As an example, in Super Smash Bros. Brawl the joystick is a set of 2 bytes at `0x805BAD30`. Converting that, however, to a float between -1 and 1 is left as an exercise for the reader.

### To do:
- Allow saving video with multiple layouts
- Finish generalizing input for other wiimote types

