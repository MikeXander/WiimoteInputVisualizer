-- Author: Xander
-- This script records the inputs for any number of wiimotes
-- with either the nunchuk, classic, or no extension

-- Notes:
-- 1. Make sure to cancel this script before closing dolphin to ensure that the file is saved properly
-- 2. there are multiple input polls per frame, this records the inputs on the LAST poll.

-- ========================== EDIT THESE =================================================
local startFrame = -1 -- -1 means it will record inputs as soon as this script is loaded
local endFrame = -1  -- -1 means it will keep going until the script is cancelled
local fileName = "_inputs.csv" -- this saves in the same folder as your dolphin.exe
-- =======================================================================================

-- This saves a CSV-like file with variable length rows (can change as extensions/controllers change)
-- Each row always starts with: Frame, Number of Controllers, ...
-- and then depending on what wiimotes are enabled and what extensions they have
-- these are the respective headers based on extension type
local HEADERS = {
	[0] = "ControllerID, ExtensionID, Buttons, IR, Accel", -- None
	[1] = "ControllerID, ExtensionID, Buttons, IR, Accel, Stick, NunchukAccel", -- Nunchuk
	[2] = "ControllerID, ExtensionID, Buttons, LStick, RStick" -- Classic
}

local file = nil
local firstInput = true
local lastFrame = -1
local wmdata = nil -- {[ControllerID] = "id,extension,data..."}

function onScriptStart()
	file = io.open(fileName, "w")
	io.output(file)
	io.write("frame,num controllers,data...\n") -- initialize header
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

	local ControllerID, ExtensionID = GetWiimoteExtension()
	if ControllerID < 4 then -- ignore GCCs (can probably add support later)
		return
	end

	-- output 1 line per frame, saving the previous frame's data
	if frame ~= lastFrame and wmdata ~= nil then
		local output = ""
		local n = 0
		for cid, data in pairs(wmdata) do
			output = output .. "," .. data
			n = n + 1
		end
		output = string.format("%d,%d%s\n", lastFrame, n, output)
		io.write(output)
		SetScreenText("\nRecording inputs: " .. output)
		wmdata = {}
	end
	lastFrame = frame

	local btns = ""
	for btn, pressed in pairs(GetButtons()) do
		if pressed then
			btns = btns .. " " .. btn
		end
	end
	if wmdata == nil then
		wmdata = {}
	end

	-- Header: ControllerID, ExtensionID, Buttons, IR, Accel
	if ExtensionID == 0 then -- wiimote
		irx, iry = GetIR()
		ax, ay, az = GetAccel()
		wmdata[ControllerID] = string.format(
			"%d,%d,%s,%d %d,%d %d %d",
			ControllerID,
			ExtensionID,
			btns,
			irx or -1, iry or -1, -- optional safeguard
			ax or -1, ay or -1, az or -1
		)
	
	-- Header: ControllerID, ExtensionID, Buttons, IR, Accel, Stick, NunchukAccel
	elseif ExtensionID == 1 then -- nunchuk
		irx, iry = GetIR()
		ax, ay, az = GetAccel()
		jx, jy = GetMainStick()
		nax, nay, naz = GetNunchukAccel()
		wmdata[ControllerID] = string.format(
			"%d,%d,%s,%d %d,%d %d %d,%d %d,%d %d %d",
			ControllerID,
			ExtensionID,
			btns,
			irx or -1, iry or -1,
			ax or -1, ay or -1, az or -1,
			jx, jy,
			nax, nay, naz
		)
	
	-- Header: ControllerID, ExtensionID, Buttons, LStick, RStick
	elseif ExtensionID == 2 then -- classic
		lx, ly = GetMainStick()
		rx, ry = GetCStick()
		wmdata[ControllerID] = string.format(
			"%d,%d,%s,%d %d,%d %d",
			ControllerID,
			ExtensionID,
			btns,
			lx, ly,
			rx, ry
		)
	end

	if frame == endFrame + 1 then
		CancelScript()
		return
	end
end
