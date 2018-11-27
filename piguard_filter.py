from motion_det import MotionDetector
import json
import time

class PiguardFilter:

    CONF_PATH = "/home/pi/piguard/conf.json"
    
    def __init__(self):
        self.conf = json.load(open(self.CONF_PATH))
        self.motion_detector = MotionDetector(self.conf)

    def process(self, frame):
        return self.motion_detector.next_frame(frame)

def init_filter():
    f = PiguardFilter()
    return f.process;
