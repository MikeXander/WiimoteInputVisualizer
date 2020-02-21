# File watcher source: https://www.thepythoncorner.com/2019/01/how-to-create-a-watchdog-in-python-to-look-for-filesystem-changes/
import WiimoteInputEncoder as encoder
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

FILEPATH = ".\data.json" 
FILENAME = "data.json"

encoder.initDisplay()

if __name__ == "__main__":
    my_event_handler = PatternMatchingEventHandler("*", "", False, True)

def on_modified(event):
    if event.src_path == FILEPATH:
        encoder.showLastFrame(FILENAME)

my_event_handler.on_modified = on_modified

path = "."
my_observer = Observer()
my_observer.schedule(my_event_handler, path)
my_observer.start()

try:
    while True:
        time.sleep(1)
        if encoder.exitCondition(): #cv2 requirement
            encoder.closeWindow()
            break
except KeyboardInterrupt:
    my_observer.stop()
    my_observer.join()
    encoder.closeWindow()

