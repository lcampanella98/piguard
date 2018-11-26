# import the necessary packages
import datetime
import imutils
import time
import cv2
import numpy

class MotionDetector:

    SCALE_WIDTH_PX = 500

    def __init__(self, conf):
        self.conf = conf
        self.codec = cv2.VideoWriter_fourcc('M','J','P','G')

        self.total_frames = 0
        self.total_recorded_frames = 0
        self.even_frame = False # at 30 fps, no need to analyze every frame. analyze every other frame 

        self.init_vars()
    
    def get_frames_saved(self):
        return self.total_recorded_frames - self.total_frames

    def get_video_writer(self, timestamp, w, h):
        self.last_video_time = timestamp
        file_path = self.conf["base_video_path"] + '/' + str(self.last_video_time) + '.avi' 
        print(file_path)
        return cv2.VideoWriter(file_path, self.codec, self.conf['fps'], (w, h),  True) 

    def get_display_text(self, has_motion):
        if has_motion:
            return "Occupied"
        return "Unoccupied"

    def frame_has_motion(self, cur_frame, bg_frame):
        has_motion = False

        # compute absolute difference between current 
        # frame and background frame
        frameDelta = cv2.absdiff(cur_frame, cv2.convertScaleAbs(bg_frame))

        # threshold the delta image, dilate the thresholded image to fill
        # in holes, then find contours on thresholded image
        thresh = cv2.threshold(frameDelta, self.conf["delta_thresh"], 255,
                cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
 
        # loop over the contours
        for c in cnts:
                # if the contour is too small, ignore it
                if cv2.contourArea(c) < self.conf["min_area"]:
                        continue
 
                has_motion = True

                # compute the bounding box for the contour, draw it on the frame,
                # and update the text
                (x, y, w, h) = cv2.boundingRect(c)
                x = round(x * self.conf["resolution"][0] / self.SCALE_WIDTH_PX)
                y = round(y * self.conf["resolution"][1] / self.SCALE_WIDTH_PX)
                w = round(w * self.conf["resolution"][0] / self.SCALE_WIDTH_PX)
                h = round(h * self.conf["resolution"][1] / self.SCALE_WIDTH_PX)
                cv2.rectangle(cur_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        return has_motion
    
    def init_vars(self):
        self.total_frames = 0
        self.total_recorded_frames = 0
        self.last_video_time = None

        self.video_writer = None
        self.avg = None
        self.num_consec_motion_frames = 0
        self.num_consec_nonmotion_frames = 0
        self.has_motion = False

    def draw_on_frame(self, frame, timestamp):
        # draw the text and timestamp on the frame
        ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
        cv2.putText(frame, "Room Status: {}".format(self.get_display_text(self.has_motion)), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                .35, (0, 0, 255), 1)

    def next_frame(self, frame):
        timestamp = datetime.datetime.now()

        self.even_frame = not self.even_frame
        if not self.even_frame: # skip every other frame
            self.draw_on_frame(frame, timestamp)
            return frame

        # resize the frame, convert it to grayscale, and blur it
        frame_resize = numpy.copy(frame)
        frame_resize = imutils.resize(frame_resize, width=self.SCALE_WIDTH_PX)
        gray = cv2.cvtColor(frame_resize, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # if the average frame is None, initialize it
        if self.avg is None:
                print("[INFO] starting background model...")
                self.avg = gray.copy().astype("float")
                return frame 
 
        # accumulate the weighted average between the current frame and
        # previous frames 
        cv2.accumulateWeighted(gray, self.avg, 0.5)

        # analyze current frame for motion
        self.has_motion = self.frame_has_motion(gray, self.avg)

        if self.has_motion:
            self.num_consec_motion_frames += 1
            self.num_consec_nonmotion_frames = 0
        else:
            self.num_consec_motion_frames = 0
            self.num_consec_nonmotion_frames += 1
        
        
        self.draw_on_frame(frame, timestamp)

        
        if self.video_writer: # we are recording
            if self.num_consec_nonmotion_frames >= self.conf["num_nonmotion_frames_stop_recording"]:
                # stop recording
                print("[INFO] Stopping recording...")
                self.video_writer.release()
                self.video_writer = None
            else:
                self.video_writer.write(frame)
        else: # we are not recording
            if self.num_consec_motion_frames >= self.conf["num_motion_frames_start_recording"]:
                # start recording
                print("[INFO] Starting recording...")
                self.video_writer = self.get_video_writer(timestamp, self.conf["resolution"][0], self.conf["resolution"][1])
                self.video_writer.write(frame)

        return frame

