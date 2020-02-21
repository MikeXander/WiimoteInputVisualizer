-- Author: Xander

local core = require "SMG_core"
local json = require "json"
local file
local lastFrame = 0

function onScriptStart()
end

function onScriptCancel()
	SetScreenText("")
end

-- returns an object containing various velocity, position, and related info
local function getVelObj()
	local data = {
		position = core.getPos(),
		velocity = core.getBaseVelocity(),
		gravity = core.getGravity(),
		up_grav = core.getUpGrav(),
		tilt = core.getTilt(),
	}
	return data
end

local function getButtonsObj()
    local data = core.getButtons()

    local function isPressed(button, inputs)
        return button & inputs == button
    end

    -- main buttons
    local TWO = 1 -- lmao
    local ONE = 2
    local B = 4
    local A = 8
    local MINUS = 16
    local Z = 32
    local C = 64
    local HOME = 128

    -- other buttons
    local LEFT = 1
    local RIGHT = 2
    local DOWN = 4
    local UP = 8
    local PLUS = 16

    local buttons = {
		two = isPressed(TWO, data.P1_main),
		one = isPressed(ONE, data.P1_main),
		p1b = isPressed(B, data.P1_main),
		p1a = isPressed(A, data.P1_main),
		minus = isPressed(MINUS, data.P1_main),
		z = isPressed(Z, data.P1_main),
		c = isPressed(C, data.P1_main),
		home = isPressed(HOME, data.P1_main),
		left = isPressed(LEFT, data.P1_alt),
		right = isPressed(RIGHT, data.P1_alt),
		down = isPressed(DOWN, data.P1_alt),
		up = isPressed(UP, data.P1_alt),
		plus = isPressed(PLUS, data.P1_alt),
		p2a = isPressed(A, data.P2),
		p2b = isPressed(B, data.P2)
	}
	return buttons
end

function onScriptUpdate()
	local data = {
		frame = GetFrameCount(),
		stick = core.getStick(),
		buttons = getButtonsObj(),
		vel = getVelObj(),
	}

	local text = json.encode(data)

	-- ensure it updates on each new frame
	if data.frame ~= lastFrame then
		file = io.open("data.json", "w")
		io.output(file)
		io.write("["..text.."]\n")
		io.close(file)
	end
	lastFrame = data.frame

	SetScreenText(text)
end
