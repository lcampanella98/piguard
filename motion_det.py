# import the necessary packages
import datetime
import imutils
import time
import cv2
import numpy
import threading
import queue

class WriteMessage:
    def __init__(self, writer, frame):
        self.writer = writer
        self.frame = frame

class VideoWriterWorker:

    def __init__(self, queue):
        self.queue = queue

    def worker(self):
        while True:
            msg = self.queue.get()
            if msg.frame is None:
                msg.writer.release()
            else:
                msg.writer.write(msg.frame)

            self.queue.task_done()



class MotionDetector:

    def __init__(self, conf):
        self.conf = conf
        self.codec = cv2.VideoWriter_fourcc('M','J','P','G')

        self.total_frames = 0
        self.total_recorded_frames = 0
        self.analyze_every_n_frames = 2
        self.update_status_file_every_n_frames = 100
        self.avg_recording_fps = 11 
        self.bytes_per_frame_approx = 22876
        
        self.queue = queue.Queue()
        self.writer_worker = VideoWriterWorker(self.queue)
        self.writer_thread = threading.Thread(target=self.writer_worker.worker, daemon=True)
        self.writer_thread.start()

        self.init_vars()

    def update_log_file(self):
        # log total space captured, total space recorded, and total space saved (inferred)
        with open(self.conf["stats_file_path"], 'w') as f:
            f.write(str(self.bytes_per_frame_approx * self.total_frames) + '\t' + str(self.bytes_per_frame_approx * self.total_recorded_frames))

    
    def get_frames_saved(self):
        return self.total_recorded_frames - self.total_frames

    def get_video_writer(self, timestamp, w, h):
        self.last_video_time = timestamp
        file_path = self.conf["base_video_path"] + '/' + str(self.last_video_time) + '.avi' 
        print(file_path)
        return cv2.VideoWriter(file_path, self.codec, self.avg_recording_fps, (w, h),  True) 

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
 
        self.cnts = []
        # loop over the contours
        for c in cnts:
                # if the contour is too small, ignore it
                if cv2.contourArea(c) < self.conf["min_area"]:
                        continue
 
                self.cnts.append(c)
                has_motion = True

        return has_motion
    
    def init_vars(self):
        self.total_frames = 0
        self.total_recorded_frames = 0
        self.last_video_time = None
        self.cnts = []

        self.video_writer = None
        self.avg = None
        self.num_consec_motion_frames = 0
        self.num_consec_nonmotion_frames = 0
        self.has_motion = False

    def is_recording(self):
        return self.video_writer is not None

    def start_measure_framerate(self):
        self.t0 = time.time()
        self.f0 = self.total_frames

    def end_measure_framerate(self):
        return round((self.total_frames - self.f0) / (time.time() - self.t0))
    
    def draw_on_frame(self, frame, timestamp):
        # draw the text and timestamp on the frame
        ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
        cv2.putText(frame, "Room Status: {}".format(self.get_display_text(self.has_motion)), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                .35, (0, 0, 255), 1)

        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        # scale = self.conf["resolution"][0] / self.SCALE_WIDTH_PX
        for c in self.cnts:
            #(x, y, w, h) = tuple([round(scale * d) for d in cv2.boundingRect(c)]) # scale rectangle to dimensions 
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)


    def next_frame(self, frame):
        timestamp = datetime.datetime.now()

        # resize the frame, convert it to grayscale, and blur it
        #frame_resize = numpy.copy(frame)
        #frame_resize = imutils.resize(frame_resize, width=self.SCALE_WIDTH_PX)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # if the average frame is None, initialize it
        if self.avg is None:
                print("[INFO] starting background model...")
                self.avg = gray.copy().astype("float")
                return frame 
 
        # accumulate the weighted average between the current frame and
        # previous frames 
        cv2.accumulateWeighted(gray, self.avg, 0.5)

        if self.total_frames % self.analyze_every_n_frames == 0:
            # analyze current frame for motion
            self.has_motion = self.frame_has_motion(gray, self.avg)

        if self.has_motion:
            self.num_consec_motion_frames += 1
            self.num_consec_nonmotion_frames = 0
        else:
            self.num_consec_motion_frames = 0
            self.num_consec_nonmotion_frames += 1
        
        
        self.draw_on_frame(frame, timestamp)

        
        if self.conf["save_video"]:
            if self.is_recording(): # we are recording
                if self.num_consec_nonmotion_frames >= self.conf["num_nonmotion_frames_stop_recording"]:
                    # stop recording
                    print("[INFO] Stopping recording...")
                    self.queue.put(WriteMessage(self.video_writer, None))
                    self.video_writer = None
                    self.avg_recording_fps = self.end_measure_framerate() # use avg fps during last recording as fps of next recording
                else:
                    self.total_recorded_frames += 1
                    self.queue.put(WriteMessage(self.video_writer, numpy.copy(frame)))
            else: # we are not recording
                if self.num_consec_motion_frames >= self.conf["num_motion_frames_start_recording"]:
                    # start recording
                    print("[INFO] Starting recording...")
                    self.video_writer = self.get_video_writer(timestamp, self.conf["resolution"][0], self.conf["resolution"][1])
                    self.queue.put(WriteMessage(self.video_writer, numpy.copy(frame)))
                    self.total_recorded_frames += 1
                    self.start_measure_framerate()

        if self.total_frames % self.update_status_file_every_n_frames == 0:
            self.update_log_file()

        self.total_frames += 1

        return frame

