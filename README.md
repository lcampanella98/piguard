# piguard
Real time monitoring system for raspberry pi

Run with command:
python3 piguard.py --conf conf.json

Detect motion on raspberry pi camera
Record video as long as motion is detected

if not recording:
	Motion detected for x frames in a row -> start recording
		start recording:
			- generate video file name

if recording:
	Motion not detected for y frames in a row -> stop recording
		stop recording:
			- save current video file

Diagnostics: save total frames operational and total recorded frames
	Difference is space savings in frames



