# WiimoteInputVisualizer
This is a set of scripts that first reads and exports input data from RAM, and then post-processes it to create a video with an input overlay.

This was inspired by [this gamecube input display](https://github.com/bkacjios/m-overlay) and uses their textures as the base for the textures here.

A sample video with the input visualizer can be found here: https://youtu.be/tLIT5Hxa80E
![Sample Image](https://cdn.discordapp.com/attachments/302599698500550659/679752173583859762/SMG_Input_Overlay_Example.png)

To export the input data, you need [Dolphin 5.0 - Lua Core](https://github.com/SwareJonge/Dolphin-Lua-Core/releases). Place `SMG_Core.lua` and `json.lua` in the same folder as `Dolphin.exe`, and place the other scripts in `/Sys/Scripts/`. Then run `SMG_Export_Inputs.lua` from within Dolphin-Lua. Some sample data produced by the lua scripts has been provided.

Once `data.json` has your desired inputs, put it in the same directory as the python scripts and run one of them. Their functions are as follows:
- `SaveVideo.py` will export a recording of the inputs to `output.avi` using the XVID codec by default
- `PlaybackInputVideo.py` will open a window and play through the input
- `LiveDisplay.py` [Experimental] will open a window and update the input display every time it detects a change in `data.json`

There are 3 different button press types that display button presses slightly differently. You can change this according to your liking at the top of `WiimoteInputEncoder.py`.

### Requirements:
- [Dolphin 5.0 - Lua Core](https://github.com/SwareJonge/Dolphin-Lua-Core/releases)
- [python 3](https://www.python.org/downloads/)
  - OpenCV2
  - watchdog
- Video editing software to combine the overlay and gameplay

### Extending Use To Other Games

This can be used to encode a video of the inputs for other games as well. To do this, you will need to write the equivalent of `SMG_Core.lua` for your respective game by finding where the inputs are stored in RAM and then export them in a similar fashion. As an example, in Super Smash Bros. Brawl the joystick is a set of 2 bytes at `0x805BAD30`. Converting that, however, to a float between -1 and 1 is left as an exercise for the reader.

### To do:
- Make it easy to add new buttons and customize layout
- Make a *better* live display ~~by using [lunatic-python](https://github.com/bastibe/lunatic-python)~~
- Make more core files for other games

