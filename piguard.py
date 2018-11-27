from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import json
import time
from motion_det import MotionDetector
 

if __name__ == '__main__':
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--conf", required=True,
            help="path to the JSON configuration file")
    args = vars(ap.parse_args())
     
    # load the configuration
    conf = json.load(open(args["conf"]))

    # initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()
    camera.resolution = tuple(conf["resolution"])
    camera.framerate = conf["fps"]
    rawCapture = PiRGBArray(camera, size=tuple(conf["resolution"]))

    motion_detector = MotionDetector(conf)

    
    print("[INFO] warming up...")
    time.sleep(conf["camera_warmup_time"])

    t = time.time()
    nf = 0
    # capture frames from the camera
    for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        nf += 1
        if time.time()-t>=1:
            t = time.time()
            print("{} frames".format(nf))
            nf = 0
        motion_detector.next_frame(f.array)
        rawCapture.truncate(0)

