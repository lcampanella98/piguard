from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import warnings
import datetime
import imutils
import json
import time
import cv2
import numpy
from motion_det import MotionDetector
 

if __name__ == '__main__':
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--conf", required=True,
            help="path to the JSON configuration file")
    args = vars(ap.parse_args())
     
    # filter warnings, load the configuration and initialize the Dropbox
    warnings.filterwarnings("ignore")
    conf = json.load(open(args["conf"]))

    # initialize the camera and grab a reference to the raw camera capture
    camera = PiCamera()
    camera.resolution = tuple(conf["resolution"])
    camera.framerate = conf["fps"]
    rawCapture = PiRGBArray(camera, size=tuple(conf["resolution"]))

    motion_detector = MotionDetector(conf)

    
    print("[INFO] warming up...")
    time.sleep(self.conf["camera_warmup_time"])

    # capture frames from the camera
    for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        motion_detector.next_frame(f.array)
        rawCapture.truncate(0)

