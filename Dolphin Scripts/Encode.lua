-- Author: Xander
-- This script automatically encodes a TAS given both a start and end frame.
-- It will frame+audio dump, join them into a single mp4, and delete the raw dump files.
-- This saves as /Dolphin/User/Dump/encode#.mp4 where # is 1, then 2, then 3, etc.
-- This requires FFmpeg installed and on your PATH.
-- Note: it overwrites/deletes the file /Dolphin/out.mp4

local startFrame = 84327
local endFrame = 86210

local n = 1
local filename = ""

local function fileExists(filepath)
    f = io.open(filepath)
    if f == nil then
        return false
    end
    f:close()
    return true
end

function onScriptStart()
    SetFrameAndAudioDump(false)
    repeat
        filename = "./User/Dump/encode" .. n .. ".mp4"
        n = n + 1
    until not fileExists(filename)
end

function onScriptUpdate()
    local f = GetFrameCount()
    if f < startFrame then
        SetScreenText("Ready to encode " .. filename .. " starting on frame " .. startFrame .. " (in " .. (startFrame - f) .. " frames)")
    elseif f == startFrame then
        SetFrameAndAudioDump(true)
    elseif startFrame < f and f < endFrame then
        SetScreenText("Recording " .. filename .. " " .. (f - startFrame) .. " / " .. (endFrame - startFrame))
    elseif f == endFrame then
        SetFrameAndAudioDump(false)
        SetScreenText("")
    elseif f == endFrame + 1 then
        os.execute("ffmpeg -i ./User/Dump/Frames/framedump0.avi -i ./User/Dump/Audio/dspdump.wav -c:a aac out.mp4")
        os.execute("mv ./User/Dump/Frames/framedump0.avi ./User/Dump/Frames/framedump"..n..".avi")
        os.execute("mv ./User/Dump/Audio/dspdump.wav ./User/Dump/Audio/dspdump"..n..".wav")
        os.execute("rm ./User/Dump/Audio/dtkdump.wav")
        os.execute("mv ./out.mp4 " .. filename)
        CancelScript()
    end
end

function onScriptCancel()
    SetScreenText("")
end
