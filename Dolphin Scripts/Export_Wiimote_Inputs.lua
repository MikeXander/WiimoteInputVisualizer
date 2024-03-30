-- Author: Xander
-- This script records the inputs from a single wiimote without a nunchuk (buttons only)

-- Notes:
-- 1. Make sure to cancel this script before closing dolphin to ensure that the file is saved properly
-- 2. there are multiple input polls per frame, this records the inputs on the LAST poll.

-- ========================== EDIT THESE =================================================
local startFrame = -1 -- -1 means it will record inputs as soon as this script is loaded
local endFrame = -1  -- -1 means it will keep going until the script is cancelled
local fileName = "_inputs.csv" -- this saves in the same folder as your dolphin.exe
-- =======================================================================================

local file = nil
local firstInput = true
local lastFrame = -1
local data = "frame,buttons\n" -- initialize header

function onScriptStart()
	file = io.open(fileName, "w")
	io.output(file)
end

function onScriptCancel()
	SetScreenText("")
	io.close(file)
end

function onScriptUpdate()
	local frame = GetFrameCount()
	if frame < startFrame then
		SetScreenText("\nHaven't started exporting inputs...")
		return
	elseif endFrame > -1 and endFrame + 1 < frame then
		SetScreenText("Finished exporting inputs")
		return
	end

	-- output 1 line per frame, saving the previous frame's data
	-- this will write the header on the first onScriptUpdate call
	if frame ~= lastFrame then
		io.write(data) 
	end
	lastFrame = frame

	local btns = ""
	for btn, pressed in pairs(GetButtons()) do
		if pressed then
			btns = btns .. " " .. btn
		end
	end
	data = string.format("%d,%s\n", frame, btns)

	if frame == endFrame + 1 then
		CancelScript()
		return
	end

	SetScreenText("\nRecording inputs: " .. data)
end
