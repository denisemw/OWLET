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
        self.initialize_potential_gaze_list()
        self.gaze = None
        self.threshold = None
        self.num_looks_away = 0
        self.frame = None
        self.prior_left = (None, None)
        self.prior_right = (None, None)
        self.haslooked = False
        self.text = ""
        self.add_stim_markers = False
        self.stim_df = None
        self.start = 0
        self.calib_start = 0
        self.calib_end = 30000
        self.end = 10000000
        self.found_match = False
        self.min_xval, self.max_xval, self.range_xvals, self.middle_x = .5, .8, .3, .65
        self.min_xval2, self.max_xval2, self.range_xvals2, self.middle_x2 = .4, .9, .5, .65
        self.min_yval, self.max_yval, self.range_yvals, self.middle_y, self.range_yvals_left, \
            self.range_yvals_right, self.min_yval_left, self.min_yval_right  = .025, .06, .035, .0425, .035, .035, .025, .025
        self.mean, self.maximum, self.minimum = 2.5, 3.5, 1.5 
        self.mean_eyeratio, self.maxeyeratio, self.mineyeratio =1.0, 1.35, .65
        self.eyearea = -999

            
    def calibrate_gaze(self, calib_file, show_output):
        """
        Initializes a calibration object and calibrates the extreme scaled
        and unscaled xy gaze positions, the mean/max/min eye blinking ratios, 
        the mean/max/min left/right eye ratios
        
        Arguments:
            calib_file (str): The path of the calibration video
        """
        
        
        sub_file , ext = os.path.splitext(calib_file)
        subDir = os.path.dirname(calib_file)
        csv_file = str(sub_file) + "_settings.csv"

        
        if Path(csv_file).is_file():
            df = pd.read_csv(csv_file)
            df.loc[0, "min_xval"]
            self.calib_starttime, self.calib_endtime, self.min_xval, self.max_xval, self.range_xvals, self.middle_x = df.iloc[0, 0:6]
            
            self.min_yval, self.max_yval, self.range_yvals, self.middle_y, self.range_yvals_left, \
                self.range_yvals_right, self.min_yval_left, self.min_yval_right = df.iloc[0, 6:14]
                
            self.min_xval2, self.max_xval2, self.range_xvals2, self.middle_x2 = df.iloc[0, 14:18]
            
            self.mean, self.maximum, self.minimum, self.eyearea = df.iloc[0, 18:22]
            
            self.mean_eyeratio, self.maxeyeratio, self.mineyeratio = df.iloc[0, 22:25]
        
        else:
            calib = LookingCalibration(show_output)
            ### FIX THIS ###
            # calib_audio = "/Users/werchd01/Dropbox/ORCA/Calibration.wav" 
            # self.convert_video_to_audio_ffmpeg(sub)
            # match_audio(self, calib_file, task):
            
            # if self.found_match:
            #     calib_starttime, calib_endtime, sub_audio_length, task_audio_length = self.find_offset(calib_file, calib_audio)
            # else:
            calib_starttime = 0
            calib_endtime = 30000
            calib.calibrate_eyes(calib_file, calib_starttime)
            
            ## get subject name from calib_file
            # sub_file = calib_file
            self.calib_starttime = calib_starttime
            self.calib_endtime = calib_endtime
            self.min_xval, self.max_xval, self.range_xvals, self.middle_x = calib.get_min_max_hor()
            
            self.min_yval, self.max_yval, self.range_yvals, self.middle_y, self.range_yvals_left, \
                self.range_yvals_right, self.min_yval_left, self.min_yval_right = calib.get_min_max_ver()
            
            self.min_xval2, self.max_xval2, self.range_xvals2, self.middle_x2 = calib.get_min_max_hor2()
            
            self.mean, self.maximum, self.minimum = calib.get_eye_ratio()
            
            self.eyearea = calib.get_eye_area()
            
            self.mean_eyeratio, self.maxeyeratio, self.mineyeratio = calib.get_eye_area_ratio()
            colnames = ['calib_starttime', 'calib_endtime', 'min_xval',	'max_xval',	'range_xvals',	'middle_x',	'min_yval',	'max_yval',	'range_yvals',	
                        'middle_y',	'range_yvals_left',	'range_yvals_right',	'min_yval_left',	'min_yval_right',	
                        'min_xval2',	'max_xval2',	'range_xvals2',	'middle_x2',	'mean',	'maximum',	
                        'minimum',	'eyearea',	'mean_eyeratio',	'maxeyeratio',	'mineyeratio']
            
            data = [self.calib_starttime, self.calib_endtime, self.min_xval, self.max_xval, self.range_xvals, self.middle_x,
                    self.min_yval, self.max_yval, self.range_yvals, self.middle_y, self.range_yvals_left,
                    self.range_yvals_right, self.min_yval_left, self.min_yval_right,
                    self.min_xval2, self.max_xval2, self.range_xvals2, self.middle_x2,
                    self.mean, self.maximum, self.minimum,
                    self.eyearea, self.mean_eyeratio, self.maxeyeratio, self.mineyeratio]
    
            calib_settings = pd.DataFrame([ data], columns =colnames)
            
            
            calib_settings.to_csv(csv_file, index = False)
        

        
    def initialize_eye_tracker(self, width, height):
        """
        Initializes a GazeTracking object, and sets the saccade threshold,
        the x/y scale values for the polynomial transfer function, and the
        initial gaze/pupil locations
        """
        self.gaze = GazeTrackingCNN(self.mean, self.maximum, self.minimum, self.mean_eyeratio)
        self.threshold = self.range_xvals/6
        if self.range_xvals < .1:
            self.threshold = .1/6 
        if self.range_yvals < .1:
            self.threshold = .1/6  
        self.x_scale_value = 960/(self.range_xvals * .8)
        self.x_scale_value2 = 960/(self.range_xvals2 * .8)
        self.y_scale_value = 540/(self.range_yvals * .8)
        self.y_scale_value_left = 540/(self.range_yvals_left * .8)
        self.y_scale_value_right = 540/(self.range_yvals_right * .8)
        self.cur_x, self.prior_x = self.middle_x, self.middle_x
        self.prior_xright, self.prior_xleft = self.middle_x, self.middle_x
        self.prior_x_scaled = self.middle_x2
        self.cur_y, self.prior_y = self.middle_y, self.middle_y
        self.prior_yright, self.prior_yleft = self.middle_y, self.middle_y     
        self.cur_y_left, self.prior_y_left = self.middle_y, self.middle_y
        self.cur_y_right, self.prior_y_right = self.middle_y, self.middle_y
            
        
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
    
    
    def convert_video_to_audio_ffmpeg(self, video_file, output_ext="wav"):
        """Converts video to audio directly using `ffmpeg` command
        with the help of subprocess module"""
            
        ff_path = "ffmpeg/ffmpeg"
        # if hasattr(sys, '_MEIPASS'):
        #    ffmpeg_path = os.path.join(sys._MEIPASS, ff_path)
        # else:
        #    ffmpeg_path = os.path.join(cwd, ff_path)
            
        filename, ext = os.path.splitext(video_file)
        
        subprocess.call([ff_path, "-y", "-i", video_file, f"{filename}.{output_ext}"], 
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

    def match_audio(self, sub, task):
        
        try:

            self.convert_video_to_audio_ffmpeg(sub)
            self.convert_video_to_audio_ffmpeg(task)
            
            subaudio = sub[0:-4] + ".wav" 
            taskaudio = task[0:-4] + ".wav" 
            self.found_match = False
            
            start, end, length, task_length = self.find_offset(subaudio, taskaudio)
            # print(start, end, length, task_length)
    
            if (end-2000) <= length and start != 0:
                self.start = start
                self.end = end
                self.found_match = True
            os.remove(subaudio)
            return self.found_match
        except:
            self.found_match = False
            self.start = 0
            self.calib_start = 0
            self.calib_end = 30000
            self.end = 10000000
            return False
   
    def initialize_cur_gaze_list(self):
        """Initializes lists for the current gaze positions"""
        self.cur_fix_hor = deque(maxlen=6)
        # self.cur_fix_hor_scaled = deque(maxlen=6)
        self.cur_fix_ver = deque(maxlen=6)
        self.cur_fix_xleft = deque(maxlen=6)
        self.cur_fix_xright = deque(maxlen=6)
        # self.cur_fix_ver_left = deque(maxlen=6)
        # self.cur_fix_ver_right = deque(maxlen=6)
        
    def initialize_potential_gaze_list(self):
        """Initializes the potential gaze positions to None"""
        self.potential_hor = None 
        self.potential_hor_scaled = None
        self.potential_fix_xleft = None 
        self.potential_fix_right = None 
        self.potential_ver_left= None 
        self.potential_ver_right = None 
        
    def append_cur_gaze_list(self, hor, ver, xleft, xright):
        """
        Appends the current gaze positions to the lists for the current gaze positions
        
        Arguments:
            hor (float): The average x pupil position
            hor_scaled (float): The average scaled x gaze position
            ver (float): The average y gaze position
            xleft (float): The left x pupil position
            xright (float): The right x pupil position
            yleft (float): The left y gaze position
            yright (float): The right y gaze position
        """
        self.cur_fix_hor.append(hor)
        # self.cur_fix_hor_scaled.append(hor_scaled)
        self.cur_fix_ver.append(ver)
        self.cur_fix_xleft.append(xleft)
        self.cur_fix_xright.append(xright)
        # self.cur_fix_ver_left.append(yleft)
        # self.cur_fix_ver_right.append(yright)
        
    def append_potential_gaze_list(self, hor, left, right):
        """
        Sets the potential gaze positions to the values given
        
        Arguments:
            hor (float): The average x pupil position
            hor_scaled (float): The average scaled x gaze position
            left (float): The left x pupil position
            right (float): The right x pupil position
            yleft (float): The left y gaze position
            yright (float): The right y gaze position
        """
        self.potential_hor = (hor)
        # self.potential_hor_scaled = (hor_scaled)
        self.potential_fix_xleft = (left)
        self.potential_fix_xright = (right)
        # self.potential_ver_left = (yleft)
        # self.potential_ver_right = (yright)

        
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
        # self.prior_x_scaled, self.prior_y = self.get_gazepoint(self.cur_fix_hor_scaled, self.cur_fix_ver, self.prior_x_scaled, self.prior_y)
        # self.prior_y_left, self.prior_y_right = self.get_gazepoint(self.cur_fix_ver_left, self.cur_fix_ver_right, self.prior_y_left, self.prior_y_right)
        self.prior_xleft, self.prior_xright = self.get_gazepoint(self.cur_fix_xleft, self.cur_fix_xright, self.prior_xleft, self.prior_xright)
        
        # gets the horizontal gaze position scaled by eye area
        cur_x_left, cur_x_right = self.gaze.horizontal_gaze()
        # curx2 = self.gaze.horizontal_gaze_scaled()
        # curx2 = curx2_original
        
        # tmplist = self.cur_fix_hor_scaled.copy()     
        
        # if curx2_original is not None:
        #     tmplist.append(curx2_original)

        # if len(tmplist) > 1:
        #     curx2 = sum(tmplist[-2:] )/2
                            
        # gets the current, non-smoothed horizontal and vertical gaze positions
        cur_x, cur_y, cur_y_left, cur_y_right = self.gaze.xy_gaze_position()
        area_ratio = self.gaze.get_eye_area_ratio()  
        self.text = "looking"
        # print(cur_x, curx2)
        # if cur_y is not None and len(self.cur_fix_ver) > 0:
        #     tmplist2 = self.cur_fix_ver.copy()
        #     tmplist3 = self.cur_fix_ver_left.copy()
        #     tmplist4 = self.cur_fix_ver_right.copy()
        #     tmplist2.append(cur_y)
        #     tmplist3.append(cur_y_left)
        #     tmplist4.append(cur_y_right)
        #     if len(tmplist2) > 3:
        #         cur_y = sum(tmplist2[-4:] )/4
        #         cur_y_left = sum(tmplist3[-4:] )/4
        #         cur_y_right = sum(tmplist4[-4:] )/4
        #     elif len(tmplist2) > 0:
        #         cur_y = sum(tmplist2)/len(tmplist2)
        #         cur_y_left = sum(tmplist3)/len(tmplist3)
        #         cur_y_right = sum(tmplist4)/len(tmplist4)
    
        self.is_looking = True

        eye_distance = self.gaze.get_eye_distance()
        nose_distance = self.gaze.get_nose_distance()
        
                # head is so far turned that baby is not looking at screen
        if eye_distance is not None and (eye_distance < .5 or eye_distance > 1.5):
            self.is_looking = False
            self.num_looks_away += 1
            # self.text = 'away'

        # elif nose_distance is not None and (nose_distance < .26 or nose_distance > .36):
        #     self.is_looking = False
        #     self.num_looks_away += 1
            # self.text = 'away'
        # head is so far turned that baby is not looking at screen
        elif area_ratio is not None and (area_ratio < .7 or area_ratio > 1.3):
            self.is_looking = False
            self.num_looks_away += 1
            # self.text='away'

        elif self.gaze.pupils_located == False or self.gaze.is_blinking():
            self.is_looking = False
            self.num_looks_away += 1
            
        # # check if not looking at the screen
        # elif curx2 < (self.min_xval2 - self.range_xvals2/1) or curx2 > (self.max_xval2 + self.range_xvals2/1):
        #     self.is_looking = False
        #     self.num_looks_away = 3
            
        # check for horizontal saccade   
        elif (cur_x >= (self.min_xval - self.range_xvals/2) and cur_x <= (self.max_xval + self.range_xvals/2) ) and \
        (self.prior_x is not None) and (abs(cur_x - self.prior_x) >= self.threshold): 
            
            self.num_looks_away = 0  
            val = self.threshold/2
            diff_left = abs(cur_x_left - self.prior_xleft)
            diff_right = abs(cur_x_right - self.prior_xright)
            # one eye jumped largely, so isn't a real saccade
            if diff_left < val or diff_right < val or diff_left/diff_right < .4 or diff_left/diff_right > 2.5:# or \
            # (diff_left2 > 0 and diff_right2 < 0) or (diff_left2 < 0 and diff_right2 > 0): # or \
                self.append_cur_gaze_list(self.prior_x, self.prior_y, self.prior_xleft, self.prior_xright)
                self.initialize_potential_gaze_list()
            else:
                self.append_cur_gaze_list(cur_x, cur_y, cur_x_left, cur_x_right)

            # elif self.potential_hor is not None:
            #     # if n-1 gaze is closer to current gaze than n-2 gaze,
            #     # then set the current gaze lists to the potential lists
            #     if abs(cur_x - self.potential_hor) <  abs(cur_x - self.prior_x):
            #         self.cur_fix_hor = [self.potential_hor]
            #         self.cur_fix_ver_left = [self.potential_ver_left]
            #         self.cur_fix_ver_right = [self.potential_ver_right]
            #         self.cur_fix_hor_scaled = [self.potential_hor_scaled]
            #         self.cur_fix_xleft = [self.potential_fix_xleft]
            #         self.cur_fix_xright = [self.potential_fix_xright]

            #         self.text = "saccade"
            #     self.append_cur_gaze_list(cur_x, curx2, cur_y, cur_x_left, cur_x_right, cur_y_left, cur_y_right)
            #     self.initialize_potential_gaze_list()
            # else:
            #     self.append_potential_gaze_list(cur_x, curx2, cur_x_left, cur_x_right, cur_y_left, cur_y_right)
            #     self.append_cur_gaze_list(self.prior_x, self.prior_x_scaled, self.prior_y, self.prior_xleft, self.prior_xright, self.prior_y_left, self.prior_y_right)
                
        # check for horizontal saccade with scaled gaze
        # elif (self.prior_x_scaled is not None) and (abs(curx2 - self.prior_x_scaled) >= (self.range_xvals2/4)): 
        #     print("here")
        #     self.num_looks_away = 0  
        #     self.cur_fix_hor = [cur_x]
        #     self.cur_fix_ver = [cur_y]
        #     self.cur_fix_ver_left = [cur_y_left]
        #     self.cur_fix_ver_right = [cur_y_right]
        #     self.cur_fix_hor_scaled = [curx2]
        #     self.cur_fix_xleft = [cur_x_left]
        #     self.cur_fix_xright = [cur_x_right]
        #     self.initialize_potential_gaze_list()
            
        else:
            self.append_cur_gaze_list(cur_x, cur_y, cur_x_left, cur_x_right)
            
            
            # uncomment if left/right gaze is desired for VPC or Listening while Looking tasks
            # if curx2_original > (self.middle_x2 + self.range_xvals2/4) or (cur_x > (self.middle_x + self.range_xvals)/4):
            #     self.text = "Right"
            # elif curx2_original < (self.middle_x2 - .06) or (cur_x < (self.middle_x - .06)):
            #     self.text = "Left"
            # else:
            #     self.text = ""
            self.num_looks_away = 0
            
        if self.haslooked == False and cur_x is not None:
            self.haslooked = True
        self.prior_x, self.prior_y = cur_x, cur_y  
        self.prior_xleft, self.prior_xright = cur_x_left, cur_x_right
        # self.prior_y_left, self.prior_y_right = cur_y_left, cur_y_right
        
        return frame

                
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
            frame: the updated subject frame with pupils highlighted
            frame2: the updated task frame annotated with gaze information
            cur_x: the raw value indicating the average x pupil position
            cur_y: the raw value indicating the average y gaze position
            xcoord: the estimated x coordinate of the point-of-gaze
            ycoord: the estimated y coordinate of the point-of-gaze
            saccade: a binary value indicating whether the infant saccaded
            self.text: the tag of the frame status (looking, saccade, or away)
        """
        color = (255, 255, 0)
        xcoord, ycoord = None, None
        # cur_y_left, cur_y_right = self.get_gazepoint(self.cur_fix_ver_left, self.cur_fix_ver_right, self.prior_y_left, self.prior_y_right)
        cur_x, cur_y = self.get_gazepoint(self.cur_fix_hor, self.cur_fix_ver, self.prior_x, self.prior_y)
        # cur_x2, cur_y = self.get_gazepoint(self.cur_fix_hor_scaled, self.cur_fix_ver, self.prior_x_scaled, self.prior_y)

        # if the baby has looked, get the current gaze point and put it on the frame
        if self.haslooked == True and (self.is_looking == True or self.num_looks_away < 3):
            xcoord = abs(int((cur_x - self.min_xval) * self.x_scale_value) - 940 )
            # xcoord2 = abs(int((cur_x2 - self.min_xval2) * self.x_scale_value2) - 940 )
            # ycoord_left = abs(int((cur_y_left - self.min_yval_left) * self.y_scale_value_left) -530 ) 
            # ycoord_right = abs(int((cur_y_right - self.min_yval_right) * self.y_scale_value_right) -530 ) 
            # ycoord = int((ycoord_left + ycoord_right)/2)
            ycoord = abs(int((cur_y - self.min_yval) * self.y_scale_value) -530 ) 
            if ycoord < 0 or ycoord > 540:
                ycoord = abs(int((self.middle_y - self.min_yval) * self.y_scale_value) -530 ) 
            if xcoord < 0 or xcoord > 960:
                self.text = "away"
            if self.text == "saccade":
                left_coords, r_left = self.gaze.pupil_left_coords()
                right_coords, r_right = self.gaze.pupil_right_coords()
                
            # if xcoord < 480 and xcoord >= 0: self.text="left"          
            # elif xcoord > 480 and xcoord <= 960: self.text="right"

            if frame.shape[1] == 1920:
                cv2.circle(frame, (xcoord+960, ycoord), 15, color, 2)  
                # cv2.circle(frame, (xcoord2+960, ycoord), 15, (255,0,255), 2)  
        else:
            # if gaze is lost for 100ms or more, reset current and potential lists
            if self.num_looks_away > 2:
                self.initialize_cur_gaze_list()
                self.initialize_potential_gaze_list()
                self.text = "away"
            # otherwise keep the look and impute from the average of the last 33-100ms (if it exists)
            else:
                if cur_x is not None:
                    self.append_cur_gaze_list(cur_x, cur_y, self.prior_xleft, self.prior_xright)
        
        cv2.putText(frame, self.text, (20, 60), cv2.FONT_HERSHEY_DUPLEX, 0.9, color, 1)
        cv2.putText(frame, str(round(timestamp,0)), (20, 30), cv2.FONT_HERSHEY_DUPLEX, 0.9, color, 1)
        # area_ratio = self.gaze.get_eye_area_ratio()  
        # eye_distance = self.gaze.get_eye_distance()
        # nose_distance = self.gaze.get_nose_distance()
        # cv2.putText(frame, str(round(area_ratio,2)), (20, 90), cv2.FONT_HERSHEY_DUPLEX, 0.9, color, 1)
        # cv2.putText(frame, str(round(eye_distance,2)), (20, 120), cv2.FONT_HERSHEY_DUPLEX, 0.9, color, 1)
        # cv2.putText(frame, str(round(nose_distance,2)), (20, 150), cv2.FONT_HERSHEY_DUPLEX, 0.9, color, 1)

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
    
    def calib_statistics(self, calib_file, subDir):
        df = self.process_subject(calib_file, subDir, False, None, True)

        
        Xcoords, pixelsX = [480, 960, 0, 480, 480], [480, 960, 0, 480, 480]           
        Ycoords , pixelsY= [270, 270, 270, 540, 0], [270, 270, 270, 540, 0]
        
        minDistX, minDistY = [999, 999, 999, 999, 999], [999, 999, 999, 999, 999]

        
        xCoordList = df.loc[:, 'X-coord']
        yCoordList = df.loc[:, 'Y-coord']
        
        xCoordList = list(filter(lambda item: item is not None and not math.isnan(item), xCoordList))
        yCoordList = list(filter(lambda item: item is not None and not math.isnan(item), yCoordList))

        for i in range(5):
            if len(xCoordList) > 0:
                diffX = min(xCoordList, key=lambda x:abs(x-Xcoords[i]))
                minDistX[i] = diffX-Xcoords[i]
                pixelsX[i] = diffX
            else:
                minDistX[i] = None
                pixelsX[i] = None
            if len(yCoordList) > 0:
                diffY = min(yCoordList, key=lambda y:abs(y-Ycoords[i]))
                minDistY[i] = diffY-Ycoords[i]
                pixelsY[i] = diffY
            else:
                minDistY[i] = None
                pixelsY[i] = None
                
        pixelsX = list(filter(lambda item: item is not None, pixelsX))
        pixelsY = list(filter(lambda item: item is not None, pixelsY))
        
        if len(pixelsX) > 0:
            Xdeviation  = int(np.mean(pixelsX))
        else: Xdeviation = None
        if len(pixelsY) > 0:
            Ydeviation = int(np.mean(pixelsY))
        else: Ydeviation = None
        
        if Xdeviation is not None and Ydeviation is not None:
            overallDeviation = int((Xdeviation + Ydeviation) / 2)
        else: overallDeviation = None
        sub_file , ext = os.path.splitext(calib_file)
        
        sub = os.path.basename(sub_file)[:-4]
        data = [sub, overallDeviation, Xdeviation, Ydeviation]
        cols =  ['Subject_ID', 'Deviation.average',
                   'Deviation.X', 'Deviation.Y' ]
        stats = pd.DataFrame([ data], columns =cols)
        
        csv_file = str(sub_file) + "_accuracy.csv"
        stats.to_csv(csv_file, index = False)
        
        # img_file = str(subDir) + "/" + str(sub) + ".jpg"
        
        # points = [ (480, 270),(860, 270), (100, 270), (480, 465), (480, 75) ]
        # for point in points:
        #     cv2.circle(img, point, int(overallDeviation), (0, 0, 255), 1)
        # cv2.imwrite(img_file, img)        
        

    def process_subject(self, videofile, task_file):
        """Calculates the ratio between the width and height of the eye frame,
        shich can be used to determine whether the eye is closed or open.
        It's the division of the width of the eye, by its height.

        Arguments:
            videofile: the subject video 
            subDir: the directory of the subject video
            show_output: boolean indicating whether to show output while processing
            task_file: the (optional) video of the task
            calib: boolean indicating whether this is a calibration video that is being processed

        Returns:
            The computed ratio
        """
    
        sub_file, ext = os.path.splitext(videofile)
        if os.path.exists(sub_file):
            sub = os.path.basename(sub_file)
            ret2 = True
            
            outfile = videofile.replace(ext, "_annotated.mp4")     
            cap = cv2.VideoCapture(videofile)   # capturing the baby video from the given path
            fps = cap.get(5)

            if fps > 30: fps2 = 30
            else: fps2  = fps

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            cap2 = cv2.VideoCapture(task_file)   # capturing the task video from the given path
            out = cv2.VideoWriter(outfile, fourcc, fps2, (1920, 540))
            frameval = math.ceil(fps) // 30 # downsamples videos to 30 fps
            if frameval < 1: frameval = 1
            output = StringIO()
            csv_writer = writer(output)
            csv_writer.writerow(['Subject_ID', 'Time', 'Frame', 'X-coord', 'Y-coord', 'Tag', 'Trial'])
            self.initialize_eye_tracker(960, 540)
            
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
                    if time >= self.start and time <= self.end:
                        if resize: frame = cv2.resize(frame, (960,540))                           
                        draw_pupils, left_coords, right_coords  = self.gaze.refresh(frame)
                        frame = self.determine_gaze(frame)
                        if draw_pupils: 
                            cv2.circle(frame, left_coords, 3, (255, 255, 0), 1)
                            cv2.circle(frame, right_coords, 3, (255, 255, 0), 1)  
                            # cv2.rectangle(frame,(self.gaze.left,self.gaze.top),(self.gaze.right,self.gaze.bottom),(0,255,0),2)
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
            if task_file is not None: cap2.release()
            out.release()
            cv2.destroyAllWindows()
            output.seek(0) 
            df = pd.read_csv(output)
            return df, True
        return None, False
            
    def format_output(self, videofile, df, aoi_file, stim_df):
        sub, ext = os.path.splitext(videofile)
        if aoi_file is not None:
            aois =  pd.read_csv(aoi_file)
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
        csv_file = videofile.replace(ext, ".csv")
        df.to_csv(csv_file, index = False)
