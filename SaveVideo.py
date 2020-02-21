import WiimoteInputEncoder as encoder

inputFname = "data.json"
codec = "XVID"
outputFname = "output.avi"
FPS = 60

encoder.save(encoder.getData(inputFname), codec, outputFname, FPS)
