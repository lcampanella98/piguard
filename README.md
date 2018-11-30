# piguard
Real time monitoring system for raspberry pi

## Install Instructions
1. Get a raspberry pi 3b+ and camera module
2. Clone this repo to the home directory
3. Install python 3, opencv 3, apache, php, and mjpg-streamer (https://github.com/jacksonliam/mjpg-streamer)
4. Open ~/piguard/stream.sh and edit the LD_LIBRARY_PATH variable to the mjpg-streamer-experimental directory
5. copy ~/piguard/www to /var/www
6. open a browser window to localhost

Run with:
./piguard.sh

Detect motion on raspberry pi camera
Record video as long as motion is detected

if not recording:
	* Motion detected for x frames in a row -> start recording
		* start recording and generate video file name

			
if recording:
	* Motion not detected for y frames in a row -> stop recording
	  * stop recording and save current video file

Diagnostics: 
	* save total frames operational and total recorded frames
	  * Difference is space savings in frames
	* compute execution time of motion-detection algorithm
	* compute time saved using separate thread to write video



