# WiimoteInputVisualizer
To output input data, you need [Dolphin 5.0 - Lua Core](https://github.com/SwareJonge/Dolphin-Lua-Core/releases). Place `SMG_Core.lua` and `json.lua` in the root directory of Dolphin, and put `SMG_Export_Inputs.lua` in the Scripts folder. Some sample data produced by the lua scripts has been provided.

Run `WiimoteInputEncoder.py` with a file named `data.json` in the same directory to create a video with the inputs. There are 3 different button press types that display button presses slightly differently. You can choose according to your liking at the top of the python script.

Requirements:
- python 3
- OpenCV2

To do: Make a live display reading a file while writing it (if possible)