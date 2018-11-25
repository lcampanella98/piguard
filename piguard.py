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

    motion_detector = MotionDetector(rawCapture, camera, conf)
    motion_detector.detect_motion()
