"""
Main code and demonstration of OWLET - an open source.
Check the README.md for complete documentation.
Assumptions: this code only works when the mom is higher than the baby
"""


import math
import pandas as pd
import numpy as np
import cv2
import librosa
from scipy import signal
import subprocess
import os
import sys
from io import StringIO 
from csv import writer 
from .gaze_tracking_cnn import GazeTrackingCNN
from .calibration import LookingCalibration
from pathlib import Path
from collections import deque

class OWLET_CNN(object):
    
    def __init__(self):
        """Returns the frame with pupils highlighted"""
        
        self.initialize_cur_gaze_list()
        self.gaze = None
        self.threshold = None
        self.num_looks_away = 0
        self.haslooked = False
        self.text = ""
        self.stim_df = None
        self.min_xval, self.max_xval, self.range_xvals, self.middle_x = .5, .8, .3, .65
        self.min_yval, self.max_yval, self.range_yvals, self.middle_y = .025, .06, .035, .0425
        self.mean, self.maximum, self.minimum = 2.5, 3.5, 1.5 
        self.mean_eyeratio  =1.0 
        self.found_match = False
        self.start = 0

    def calibrate_gaze(self, cwd, calib_file):
        """
        Initializes a calibration object and calibrates the extreme scaled
        and unscaled xy gaze positions, the mean/max/min eye blinking ratios, 
        the mean/max/min left/right eye ratios
        
        Arguments:
            calib_file (str): The path of the calibration video
        """
        csv_file = calib_file.replace(".mp4", "_settings.csv")
        print(csv_file)

        if Path(csv_file).is_file():
            df = pd.read_csv(csv_file)
            
            self.min_xval, self.max_xval, self.range_xvals, self.middle_x = df.iloc[0, 0:4]      
            self.min_yval, self.max_yval, self.range_yvals, self.middle_y = df.iloc[0, 4:8]
            self.mean, self.maximum, self.minimum, self.mean_eyeratio = df.iloc[0, 8:12]
        
        else:
            calib = LookingCalibration(cwd)
            # calib = ManualCalibration(redo=True)

            calib.calibrate_eyes(calib_file)


            self.min_xval, self.max_xval, self.range_xvals, self.middle_x = calib.get_min_max_hor()
            self.min_yval, self.max_yval, self.range_yvals, self.middle_y = calib.get_min_max_ver()
            self.mean, self.maximum, self.minimum = calib.get_eye_ratio()
            self.mean_eyeratio = calib.get_eye_area_ratio()
            colnames = ['min_xval',	'max_xval',	'range_xvals',	'middle_x',	
                        'min_yval',	'max_yval',	'range_yvals',	'middle_y',	
                       	'mean',	'maximum',	'minimum',	'mean_eyeratio']
            
            data = [self.min_xval, self.max_xval, self.range_xvals, self.middle_x,
                    self.min_yval, self.max_yval, self.range_yvals, self.middle_y,
                    self.mean, self.maximum, self.minimum, self.mean_eyeratio]
    
            calib_settings = pd.DataFrame([ data], columns =colnames)
            calib_settings.to_csv(csv_file, index = False)
            

        
    def initialize_eye_tracker(self, cwd):
        """
        Initializes a GazeTracking object, and sets the saccade threshold,
        the x/y scale values for the polynomial transfer function, and the
        initial gaze/pupil locations
        """
        self.gaze = GazeTrackingCNN(self.mean, self.maximum, self.minimum, self.mean_eyeratio, cwd)
        self.threshold = self.range_xvals/6
        if self.range_xvals < .1 or self.range_yvals < .1:
            self.threshold = .1/6 
        self.x_scale_value = 960/(self.range_xvals * 1)
        self.y_scale_value = 540/(self.range_yvals * .8)
        self.cur_x, self.prior_x = self.middle_x, self.middle_x
        self.prior_xright, self.prior_xleft = self.middle_x, self.middle_x
        self.cur_y, self.prior_y = self.middle_y, self.middle_y
            
            
        
    def get_gazepoint(self, gazelist1, gazelist2, x, y):
        """
        Returns the x and y positions averaged over the last 6 data points
        
        Arguments:
            gazelist1 (list): The list of x gaze positions
            gazelist2 (list): The list of y gaze positions
            x (float): The current x gaze position
            y (float): The current y gaze position
            
        Returns: 
            the average x and y gaze point
        """
        xval, yval = x, y
        # if len(gazelist1) > 3:
        #     xval = sum(gazelist1[-4:])/4
        #     if len(gazelist2) > 3:
        #         yval = sum(gazelist2[-4:] )/4
        #     else:
        #         yval = sum(gazelist2)/len(gazelist2)
        if len(gazelist1) > 0:
            xval = sum(gazelist1)/len(gazelist1)
            yval = sum(gazelist2)/len(gazelist2)
        return xval, yval
    
    
    def convert_video_to_audio_ffmpeg(self, video_file, cwd, output_ext="wav"):
        """Converts video to audio directly using `ffmpeg` command
        with the help of subprocess module"""
            
        ff_path = "ffmpeg/ffmpeg"
        if hasattr(sys, '_MEIPASS'):
           ffmpeg_path = os.path.join(sys._MEIPASS, ff_path)
        else:
           ffmpeg_path = os.path.join(cwd, ff_path)
            
        filename, _ = os.path.splitext(video_file)
        
        subprocess.call([ffmpeg_path, "-y", "-i", video_file, f"{filename}.{output_ext}"], 
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT)
        

    def find_offset(self, subject_audio, task_audio):
        """
        Returns the offset between the subject video and the start of the task
        based on matching the audio patterns using FFT and cross correlations
        
        Arguments:
            subject_audio (wav file): The audio file name of the subject audio
            task_audio (wav file): The audio file name of the task audio
            window (int): The window in which to search for a match within
            
        Returns:
            The time until the task begins in the subject video
        """
        y_within, sr_within = librosa.load(subject_audio, sr=None)

        y_find, sr_find = librosa.load(task_audio, sr=sr_within)
    
        c = signal.correlate(y_within, y_find, mode='valid', method='fft')
        peak = np.argmax(c)
        start = round(peak / sr_within, 2) * 1000
        sub_audio_length = librosa.get_duration(y=y_within, sr=sr_within) * 1000
        task_audio_length = librosa.get_duration(y=y_find, sr=sr_find) * 1000
        
        if c[peak] < 60:
            start = 0
        end = start + (task_audio_length)

        return start, end, sub_audio_length, task_audio_length

    def match_audio(self, sub, task, cwd):
        
        try:

            self.convert_video_to_audio_ffmpeg(sub, cwd)
            self.convert_video_to_audio_ffmpeg(task, cwd)
            
            subaudio = sub[0:-4] + ".wav" 
            taskaudio = task[0:-4] + ".wav" 
            self.found_match = False
            
            start, end, length, task_length = self.find_offset(subaudio, taskaudio)
            # print(start, end, length, task_length)
    
            if (end-2000) <= length and start != 0:
                self.start = start
                self.found_match = True
            os.remove(subaudio)
            return self.found_match
        except:
            self.found_match = False
            self.start = 0
            return False
   
    def initialize_cur_gaze_list(self):
        """Initializes lists for the current gaze positions"""
        self.cur_fix_hor = deque(maxlen=6)
        self.cur_fix_ver = deque(maxlen=6)
        self.cur_fix_xleft = deque(maxlen=6)
        self.cur_fix_xright = deque(maxlen=6)


    def append_cur_gaze_list(self, hor, ver, xleft, xright):
        """
        Appends the current gaze positions to the lists for the current gaze positions
        
        Arguments:
            hor (float): The average x pupil position
            ver (float): The average y gaze position
            xleft (float): The left x pupil position
            xright (float): The right x pupil position

        """
        self.cur_fix_hor.append(hor)
        self.cur_fix_ver.append(ver)
        self.cur_fix_xleft.append(xleft)
        self.cur_fix_xright.append(xright)

        
    def determine_gaze(self, frame):
        """
        Detects the current gaze position and sets
        all of the gaze points and tags for whether
        the baby is looking, saccading, or away.
        
        Arguments:
            frame (numpy.ndarray): The current subject frame to analyze
            
        Returns:
            frame (numpy.ndarray): The subject frame with pupils annotated
        """
        
        # this is getting the average gaze point of the last X number of trials, which we use to check for saccades
        self.prior_x, self.prior_y = self.get_gazepoint(self.cur_fix_hor, self.cur_fix_ver, self.prior_x, self.prior_y)
        self.prior_xleft, self.prior_xright = self.get_gazepoint(self.cur_fix_xleft, self.cur_fix_xright, self.prior_xleft, self.prior_xright)
        
        # gets the horizontal gaze position scaled by eye area
        cur_x_left, cur_x_right = self.gaze.horizontal_gaze()
                            
        # gets the current, non-smoothed horizontal and vertical gaze positions
        cur_x, cur_y = self.gaze.xy_gaze_position()
        area_ratio = self.gaze.get_eye_area_ratio()  
        self.text = "looking"

    
        self.is_looking = True

        eye_distance = self.gaze.get_eye_distance()
        
                # head is so far turned that baby is not looking at screen
        if eye_distance is not None and (eye_distance < .67 or eye_distance > 1.5):
            self.is_looking = False
            self.num_looks_away += 1

        # head is so far turned that baby is not looking at screen
        elif area_ratio is not None and (area_ratio < .5 or area_ratio > 2):
            self.is_looking = False
            self.num_looks_away += 1

        elif self.gaze.pupils_located == False or self.gaze.is_blinking():
            self.is_looking = False
            self.num_looks_away += 1
            
        # check for horizontal saccade   
        elif (cur_x >= (self.min_xval - self.range_xvals/2) and cur_x <= (self.max_xval + self.range_xvals/2) ) and \
        (self.prior_x is not None) and (abs(cur_x - self.prior_x) >= self.threshold): 
            self.num_looks_away = 0  
            val = self.threshold/2
            diff_left = abs(cur_x_left - self.prior_xleft)
            diff_right = abs(cur_x_right - self.prior_xright)
            # one eye jumped largely, so isn't a real saccade
            if diff_left < val or diff_right < val or diff_left/diff_right < .4 or diff_left/diff_right > 2.5:# or \
                self.append_cur_gaze_list(self.prior_x, self.prior_y, self.prior_xleft, self.prior_xright)
            else:
                self.append_cur_gaze_list(cur_x, cur_y, cur_x_left, cur_x_right)
            
        else:
            self.append_cur_gaze_list(cur_x, cur_y, cur_x_left, cur_x_right)
            
            self.num_looks_away = 0
            
        if self.haslooked == False and cur_x is not None:
            self.haslooked = True

        self.prior_x, self.prior_y = cur_x, cur_y  
        self.prior_xleft, self.prior_xright = cur_x_left, cur_x_right
        if self.is_looking==False:
            self.text = "away"
        
                
    def update_frame(self, frame, timestamp):
        """
        Estiamtes the current point-of-gaze using a polynomial transfer function
        and the scale values determiend during calibration. Draws the estimated 
        gaze position, tags, and current timestamp on the subject video frame.
        
        Arguments:
            frame (numpy.ndarray): The current subject frame
            frame2 (numpy.ndarray): The current task frame
            timestamp (int): The current timestamp of the subject video
            
        Returns:
            frame: the updated  frame 
            xcoord: the estimated x coordinate of the point-of-gaze
            ycoord: the estimated y coordinate of the point-of-gaze
            self.text: the tag of the frame status (looking, saccade, or away)
        """
        color = (255, 255, 0)
        xcoord, ycoord = None, None
        cur_x, cur_y = self.get_gazepoint(self.cur_fix_hor, self.cur_fix_ver, self.prior_x, self.prior_y)


        # if the baby has looked, get the current gaze point and put it on the frame
        if self.haslooked == True and (self.is_looking == True or self.num_looks_away < 3):
            xcoord = abs(int((cur_x - self.min_xval) * self.x_scale_value) - 940 )
            ycoord = abs(int((cur_y - self.min_yval) * self.y_scale_value) -530 ) 
            if ycoord < 0 or ycoord > 540:
                ycoord = abs(int((self.middle_y - self.min_yval) * self.y_scale_value) -530 ) 
            if xcoord < 0 or xcoord > 960:
                self.text = "away"
            if frame.shape[1] == 1920:
                cv2.circle(frame, (xcoord+960, ycoord), 15, color, 2)  
        else:
            # if gaze is lost for 100ms or more, reset current and potential lists
            if self.num_looks_away > 2:
                self.initialize_cur_gaze_list()
                self.text = "away"
            # otherwise keep the look and impute from the average of the last 33-100ms (if it exists)
            else:
                if cur_x is not None:
                    self.append_cur_gaze_list(cur_x, cur_y, self.prior_xleft, self.prior_xright)
        
        cv2.putText(frame, self.text, (20, 60), cv2.FONT_HERSHEY_DUPLEX, 0.9, color, 1)
        cv2.putText(frame, str(round(timestamp,0)), (20, 30), cv2.FONT_HERSHEY_DUPLEX, 0.9, color, 1)

        return frame, xcoord, ycoord, self.text


    def read_stim_markers(self, stim_file):
        stim_df = pd.read_csv(stim_file)
        if "Time" not in stim_df:
            if "time" in stim_df:
                stim_df.rename(columns = {'time':'Time'}, inplace = True)
            else:
                return False, None
        if "Label" not in stim_df:
            if "label" in stim_df:
                stim_df.rename(columns = {'label':'Label'}, inplace = True)
            else:
                return False, None
        stim_df.sort_values("Time")
        return True, stim_df
    


    def process_subject(self, cwd, videofile, task_file):
        """Calculates the ratio between the width and height of the eye frame,
        shich can be used to determine whether the eye is closed or open.
        It's the division of the width of the eye, by its height.

        Arguments:
            cwd: the directory where OWLET is running
            videofile: the subject video 
            task_file: the (optional) video of the task
            calib: boolean indicating whether this is a calibration video that is being processed

        Returns:
            The computed ratio
        """
    

        sub_file, ext = os.path.splitext(videofile)
        sub = os.path.basename(sub_file)
        ret2 = True
        taskname = ""
        if task_file is not None:
            taskname = str(os.path.basename(task_file)[0:-4])
            if taskname in str(sub_file):
                taskname = ""
            else:
                taskname = "_" + taskname
        
        outfile = str(sub_file) + taskname + "_annotated.mp4"                
        cap = cv2.VideoCapture(videofile)   # capturing the baby video from the given path
        fps = cap.get(5)

        if fps > 30: fps2 = 30
        else: fps2  = fps

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        if task_file is not None:
            cap2 = cv2.VideoCapture(task_file)   # capturing the task video from the given path
            out = cv2.VideoWriter(outfile, fourcc, fps2, (1920, 540))
        else: 
            out = cv2.VideoWriter(outfile, fourcc, fps2, (960, 540))
        
        frameval = math.ceil(fps) // 30 # downsamples videos to 30 fps
        if frameval < 1: frameval = 1
        
        output = StringIO()
        csv_writer = writer(output)
        
        colnames = ['Subject_ID', 'Time', 'Frame', 'X-coord', 'Y-coord', 'Tag', 'Trial']
        csv_writer.writerow(colnames)

        self.initialize_eye_tracker(cwd)

        
        ret, frame = cap.read()
        height, width, _ = frame.shape
        resize = (height != 540 or width!=960)
        
        while (cap.isOpened()):
            ret, frame = cap.read()
            frameId = cap.get(1) #current frame number
            if (ret == False or ret2 == False): 
                break
            if (frameId % frameval == 0):
                time = cap.get(cv2.CAP_PROP_POS_MSEC)
                if time >= self.start:
                    if resize: frame = cv2.resize(frame, (960,540))  
                
                    
                    draw_pupils, left_coords, right_coords  = self.gaze.refresh(frame)
                    self.determine_gaze(frame)

                    if draw_pupils and left_coords and right_coords: 
                        cv2.circle(frame, left_coords, 3, (255, 255, 0), 1)
                        cv2.circle(frame, right_coords, 3, (255, 255, 0), 1)                      
                    # concat frames
                    if task_file is not None:
                        ret2, frame2 = cap2.read()   
                        if ret2==False: break
                        frame2 = cv2.resize(frame2, (960,540))
                        final = cv2.hconcat([frame, frame2])
                    else: final = frame
                        
                    final, xcoord, ycoord, text = self.update_frame(final, time)
                    out.write(final)

                    csv_writer.writerow([sub, time, frameId, xcoord, ycoord, text, ""])
                    
                    key = cv2.waitKey(1)
                    # press 'q' to quit
                    if key == ord('q'):
                        break                           
                    
        cap.release()
        if task_file is not None:
            cap2.release()
        out.release()
        cv2.destroyAllWindows()
                
        output.seek(0) 
        df = pd.read_csv(output)
        return df

    def format_output(self, videofile, task_file, expDir, df, aoi_file, stim_df):
        sub, ext = os.path.splitext(videofile)
        taskname = ""
        if task_file is not None:
            taskname = str(os.path.basename(task_file)[0:-4])
            if taskname in str(sub):
                taskname = ""
            else:
                taskname = "_" + taskname
            
        if aoi_file != "":
            aois =  pd.read_csv(os.path.abspath(os.path.join(expDir, aoi_file)))
            df["Tag"] = None
            # Use a vectorized operation
            for _, aoi in aois.iterrows():
                mask = (
                    (df["X-coord"] >= aoi["X1"]) & (df["X-coord"] < aoi["X2"]) &
                    (df["Y-coord"] >= aoi["Y1"]) & (df["Y-coord"] < aoi["Y2"])
                )
                df.loc[mask, "Tag"] = aoi["AOI"]

   
        else:
            df["Tag"] = None  # Initialize column
            df.loc[df["X-coord"] < 480, "Tag"] = "Left"
            df.loc[(df["X-coord"] >= 480) & (df["X-coord"] < 960), "Tag"] = "Right"


        
        if stim_df is not None:
            row_marker = 0

            for i in range(len(df)):
                if row_marker >= len(stim_df):
                    break
                cur_time = stim_df.loc[row_marker, "Time"] + self.start
                cur_label = stim_df.loc[row_marker, "Label"]
                if df.loc[i, "Time"] >= cur_time:
                    df.loc[i, "Trial"] = cur_label
                    row_marker += 1                        
        csv_file =str(sub) + taskname + ".csv"
        df.to_csv(csv_file, index = False)
