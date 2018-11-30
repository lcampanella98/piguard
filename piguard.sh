#!/bin/bash

sudo modprobe bcm2835-v4l2
export LD_LIBRARY_PATH=~/mjpg-streamer/mjpg-streamer-experimental
$LD_LIBRARY_PATH/mjpg_streamer -o "output_http.so -w /var/www/html" -i "input_opencv.so --filter cvfilter_py.so --fargs ./piguard_filter.py"
