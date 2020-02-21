# WiimoteInputVisualizer
To output input data, you need [Dolphin 5.0 - Lua Core](https://github.com/SwareJonge/Dolphin-Lua-Core/releases). Place the lua scripts in the appropraite Scripts folder. Some sample data produced by the lua scripts has been provided.

There are 3 different button press types that display button presses slightly differently. You can change this according to your liking at the top of `WiimoteInputEncoder.py`.

To use the python scripts, put `data.json` in the same directory as them. Their functions are as follows:
- `SaveVideo.py` will export a recording to `output.avi` using the XVID codec by default
- `PlaybackInputVideo.py` will open a window and play through the input
- `LiveDisplay.py` [BETA] will open a window and update the input display every time it detects a change in `data.json`

Requirements:
- python 3
  - OpenCV2
  - watchdog

To do:
- Make a *better* live display by using [lunatic-python](https://github.com/bastibe/lunatic-python)
- Make it easy to add new buttons and customize layout
