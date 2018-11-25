#!/bin/bash

export LD_LIBRARY_PATH=~/mjpg-streamer/mjpg-streamer-experimental
$LD_LIBRARY_PATH/mjpg_streamer -o "output_http.so -w /var/www/html" -i "input_raspicam.so" &
