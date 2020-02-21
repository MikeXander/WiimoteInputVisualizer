local core = {}

local function getGameID()
    local address = 0x0
    return ReadValueString(address, 6)
end
core.getGameID = getGameID

-- Most addresses are offset from this pointer
local function getRefPointer()
    local address = nil
    if getGameID() == "RMGE01" then address = 0xF8EF88
    elseif getGameID() == "RMGJ01" then address = 0xF8F328
    elseif getGameID() == "RMGP01" then address = 0xF8EF88
    end
    if address == nil then return nil
    else return GetPointerNormal(address)
    end
end
core.getRefPointer = getRefPointer

local function getPos()
  local offset1 = 0x3EEC
  local address = getRefPointer()
  if address == nil then
		return {X = 0, Y = 0, Z = 0}
  end
  return {X = ReadValueFloat(address + offset1), Y = ReadValueFloat(address + offset1 + 4), Z = ReadValueFloat(address + offset1 + 8)}
end
core.getPos = getPos

local function getPrevPos()
  local offset1 = 0x18DC
  local address = getRefPointer()
  if address == nil then
		return {X = 0, Y = 0, Z = 0}
  end
  return {X = ReadValueFloat(address + offset1), Y = ReadValueFloat(address + offset1 + 4), Z = ReadValueFloat(address + offset1 + 8)}
end
core.getPrevPos = getPrevPos

local function getSpd()
  local PrevXpos = getPrevPos().X
  local PrevYpos = getPrevPos().Y
  local PrevZpos = getPrevPos().Z
  local Xpos = getPos().X
  local Ypos = getPos().Y
  local Zpos = getPos().Z
  return {Y = (Ypos - PrevYpos), XZ = math.sqrt(((Xpos - PrevXpos)^2) + (Zpos - PrevZpos)^2), XYZ = math.sqrt(((Xpos - PrevXpos)^2) + ((Ypos - PrevYpos)^2) + (Zpos - PrevZpos)^2)}
end
core.getSpd = getSpd

local function getTextRelatedStuff()
  local pointer = 0x9A9240
  local address = GetPointerNormal(pointer)
  if ReadValue32(pointer) == 0 then
    return {textProgress = 0, alphaReq = 0, fadeRate = 0}
  end
  return {textProgress = ReadValue32(address + 0x2D39C), alphaReq = ReadValueFloat(address + 0x2D3B0), fadeRate = ReadValueFloat(address + 0x2D3B4)}
end
core.getTextRelatedStuff = getTextRelatedStuff

local function setPos(x, y, z)
    local offset1 = 0x18DC--0x3EEC
    local address = getRefPointer()
    if address ~= nil then
        WriteValueFloat(address + offset1, x)
        WriteValueFloat(address + offset1 + 4, y)
        WriteValueFloat(address + offset1 + 8, z)
    end
end
core.setPos = setPos

local function changePos(dx, dy, dz)
    local pos = getPos()
    setPos(pos.X + dx, pos.Y + dy, pos.Z + dz)
end
core.changePos = changePos

local function getStick()
    local x_addr = 0x61D3A0
    local y_addr = 0x61D3A4
    return {X = ReadValueFloat(x_addr), Y = ReadValueFloat(y_addr)}
end
core.getStick = getStick

local function getButtons()
    local buttons1 = 0x61D342
    local buttons2 = 0x61D343
    local p2_buttons = 0x61EF3A
    return {P1_main = ReadValue8(buttons1), P1_alt = ReadValue8(buttons2), P2 = ReadValue8(p2_buttons)}
end
core.getButtons = getButtons

-- Ingame velocity
local function getBaseVelocity()
    local offset = 0x3EEC + 0x78
    local address = getRefPointer()
    if address == nil then
    	return {X = 0, Y = 0, Z = 0}
    end
    return {X = ReadValueFloat(address + offset), Y = ReadValueFloat(address + offset + 4), Z = ReadValueFloat(address + offset + 8)}
end
core.getBaseVelocity = getBaseVelocity

-- this is just a Positive version of gravity
local function getUpGrav()
    local offset = 0x6A3C
    local address = getRefPointer()
    if address == nil then
    	return {X = 0, Y = 0, Z = 0}
    end
    return {X = ReadValueFloat(address + offset), Y = ReadValueFloat(address + offset + 4), Z = ReadValueFloat(address + offset + 8)}
end
core.getUpGrav = getUpGrav

local function getGravity()
    local offset = 0x1B10
    local address = getRefPointer()
    if address == nil then
    	return {X = 0, Y = 0, Z = 0}
    end
    return {X = ReadValueFloat(address + offset), Y = ReadValueFloat(address + offset + 4), Z = ReadValueFloat(address + offset + 8)}
end
core.getGravity = getGravity

local function getTilt()
    local offset = 0x3EEC + 0xC0
    local address = getRefPointer()
    if address == nil then
    	return {X = 0, Y = 0, Z = 0}
    end
    return {X = ReadValueFloat(address + offset), Y = ReadValueFloat(address + offset + 4), Z = ReadValueFloat(address + offset + 8)}
end
core.getTilt = getTilt

return core
