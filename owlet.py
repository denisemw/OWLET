"""
Main code and demonstration of OWLET - an open source.
Check the README.md for complete documentation.
Assumptions: this code only works when the mom is higher than the baby
"""


import math
import pandas as pd
import numpy as np
import cv2
from gaze_tracking import GazeTracking
from calibration import LookingCalibration
# from processET import ET_processing
import os
from scipy import signal
import librosa



class OWLET(object):
    
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
        self.length = 1
        self.text = ""

        
        self.min_xval, self.max_xval, self.range_xvals, self.middle_x = .5, .8, .3, .65
        self.min_xval2, self.max_xval2, self.range_xvals2, self.middle_x2 = .4, .9, .5, .65
        self.min_yval, self.max_yval, self.range_yvals, self.middle_y, self.range_yvals_left, \
            self.range_yvals_right, self.min_yval_left, self.min_yval_right  = .025, .06, .035, .0425, .035, .035, .025, .025
        self.mean, self.maximum, self.minimum = 2.5, 3.5, 1.5 
        self.mean_eyeratio, self.maxeyeratio, self.mineyeratio =1.0, 1.35, .65
        self.eyearea = -999

            
    def calibrate_gaze(self, calib_file):
        """
        Initializes a calibration object and calibrates the extreme scaled
        and unscaled xy gaze positions, the mean/max/min eye blinking ratios, 
        the mean/max/min left/right eye ratios
        
        Arguments:
            calib_file (str): The path of the calibration video
        """
        calib = LookingCalibration()
        calib.calibrate_eyes(calib_file)
        self.min_xval, self.max_xval, self.range_xvals, self.middle_x = calib.get_min_max_hor()
        self.min_yval, self.max_yval, self.range_yvals, self.middle_y, self.range_yvals_left, \
            self.range_yvals_right, self.min_yval_left, self.min_yval_right = calib.get_min_max_ver()
        
        self.min_xval2, self.max_xval2, self.range_xvals2, self.middle_x2 = calib.get_min_max_hor2()
        self.mean, self.maximum, self.minimum = calib.get_eye_ratio()
        self.eyearea = calib.get_eye_area()
        self.mean_eyeratio, self.maxeyeratio, self.mineyeratio = calib.get_eye_area_ratio()     
        self.length = calib.get_avg_length()
        print(self.min_xval, self.max_xval)
        print(self.min_xval2, self.max_xval2)
        
    def initialize_eye_tracker(self):
        """
        Initializes a GazeTracking object, and sets the saccade threshold,
        the x/y scale values for the polynomial transfer function, and the
        initial gaze/pupil locations
        """
        self.gaze = GazeTracking(self.mean, self.maximum, self.minimum, self.mean_eyeratio, self.length)
        self.threshold = self.range_xvals/6
        if self.range_xvals < .1:
            self.threshold = .1/6 
        self.x_scale_value = 960/(self.range_xvals * .9)
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
        xval = x
        yval = y 
        if len(gazelist1) > 5:
            xval = sum(gazelist1[-6:])/6
            if len(gazelist2) > 5:
                yval = sum(gazelist2[-6:] )/6
            else:
                yval = sum(gazelist2)/len(gazelist2)
        elif len(gazelist1) > 0:
            xval = sum(gazelist1)/len(gazelist1)
            yval = sum(gazelist2)/len(gazelist2)
        return xval, yval
    
    def find_offset(self,subject_audio, task_audio, window):
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
        y_find, _ = librosa.load(task_audio, sr=sr_within)
    
        c = signal.correlate(y_within, y_find[:sr_within*window], mode='valid', method='fft')
        peak = np.argmax(c)
        offset = round(peak / sr_within, 2)
    
        return offset
   
    def initialize_cur_gaze_list(self):
        """Initializes lists for the current gaze positions"""
        self.cur_fix_hor = []
        self.cur_fix_hor_scaled = []
        self.cur_fix_ver = []
        self.cur_fix_xleft = []
        self.cur_fix_xright = []
        self.cur_fix_ver_left = []
        self.cur_fix_ver_right = []
        
    def initialize_potential_gaze_list(self):
        """Initializes the potential gaze positions to None"""
        self.potential_hor = None 
        self.potential_hor_scaled = None
        self.potential_fix_xleft = None 
        self.potential_fix_right = None 
        self.potential_ver_left= None 
        self.potential_ver_right = None 
        
    def append_cur_gaze_list(self, hor, hor_scaled, ver, xleft, xright, yleft, yright):
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
        self.cur_fix_hor_scaled.append(hor_scaled)
        self.cur_fix_ver.append(ver)
        self.cur_fix_xleft.append(xleft)
        self.cur_fix_xright.append(xright)
        self.cur_fix_ver_left.append(yleft)
        self.cur_fix_ver_right.append(yright)
        
    def append_potential_gaze_list(self, hor, hor_scaled, left, right, yleft, yright):
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
        self.potential_hor_scaled = (hor_scaled)
        self.potential_fix_xleft = (left)
        self.potential_fix_xright = (right)
        self.potential_ver_left = (yleft)
        self.potential_ver_right = (yright)

        
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
        # gets the current left and right horizontal pupil positions
        self.gaze.refresh(frame)
        frame = self.gaze.annotated_frame()
        
        # this is getting the average gaze point of the last X number of trials, which we use to check for saccades
        self.prior_x, self.prior_y = self.get_gazepoint(self.cur_fix_hor, self.cur_fix_ver, self.prior_x, self.prior_y)
        self.prior_x_scaled, self.prior_y = self.get_gazepoint(self.cur_fix_hor_scaled, self.cur_fix_ver, self.prior_x_scaled, self.prior_y)
        self.prior_y_left, self.prior_y_right = self.get_gazepoint(self.cur_fix_ver_left, self.cur_fix_ver_right, self.prior_y_left, self.prior_y_right)
        self.prior_xleft, self.prior_xright = self.get_gazepoint(self.cur_fix_xleft, self.cur_fix_xright, self.prior_xleft, self.prior_xright)
        
        # gets the horizontal gaze position scaled by eye area
        cur_x_left, cur_x_right = self.gaze.horizontal_gaze()
        curx2_original = self.gaze.horizontal_gaze_scaled()
        curx2 = curx2_original
        
        tmplist = self.cur_fix_hor_scaled.copy()
        
        
        if curx2_original is not None:
            tmplist.append(curx2_original)

        if len(tmplist) > 1:
            curx2 = sum(tmplist[-2:] )/2
                            
        # gets the current, non-smoothed horizontal and vertical gaze positions
        cur_x, cur_y, cur_y_left, cur_y_right = self.gaze.xy_gaze_position()
        area_ratio = self.gaze.get_eye_area_ratio()  
        self.text = "looking"
        
        if cur_y is not None and len(self.cur_fix_ver) > 0:
            tmplist2 = self.cur_fix_ver.copy()
            tmplist3 = self.cur_fix_ver_left.copy()
            tmplist4 = self.cur_fix_ver_right.copy()
            tmplist2.append(cur_y)
            tmplist3.append(cur_y_left)
            tmplist4.append(cur_y_right)
            if len(tmplist2) > 3:
                cur_y = sum(tmplist2[-4:] )/4
                cur_y_left = sum(tmplist3[-4:] )/4
                cur_y_right = sum(tmplist4[-4:] )/4
            elif len(tmplist2) > 0:
                cur_y = sum(tmplist2)/len(tmplist2)
                cur_y_left = sum(tmplist3)/len(tmplist3)
                cur_y_right = sum(tmplist4)/len(tmplist4)
    
        self.is_looking = True
        
        # head is so far turned that baby is not looking at screen
        if area_ratio is not None and (area_ratio < .5 or area_ratio > 1.5):
            self.is_looking = False
            self.num_looks_away += 1

        elif self.gaze.pupils_located == False or self.gaze.is_blinking():
            self.is_looking = False
            self.num_looks_away += 1
            
        # check if not looking at the screen
        elif curx2 < (self.min_xval2 - self.range_xvals2/1) or curx2 > (self.max_xval2 + self.range_xvals2/1):
            self.is_looking = False
            self.num_looks_away = 3
            # print("scaled x out of screen range")
            
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
                self.append_cur_gaze_list(self.prior_x, self.prior_x_scaled, self.prior_y, self.prior_xleft, self.prior_xright, self.prior_y_left, self.prior_y_right)
                self.initialize_potential_gaze_list()

            elif self.potential_hor is not None:
                # if n-1 gaze is closer to current gaze than n-2 gaze,
                # then set the current gaze lists to the potential lists
                if abs(cur_x - self.potential_hor) <  abs(cur_x - self.prior_x):
                    self.cur_fix_hor = [self.potential_hor]
                    self.cur_fix_ver_left = [self.potential_ver_left]
                    self.cur_fix_ver_right = [self.potential_ver_right]
                    self.cur_fix_hor_scaled = [self.potential_hor_scaled]
                    self.cur_fix_xleft = [self.potential_fix_xleft]
                    self.cur_fix_xright = [self.potential_fix_xright]

                    self.text = "saccade"
                self.append_cur_gaze_list(cur_x, curx2, cur_y, cur_x_left, cur_x_right, cur_y_left, cur_y_right)
                self.initialize_potential_gaze_list()
            else:
                self.append_potential_gaze_list(cur_x, curx2, cur_x_left, cur_x_right, cur_y_left, cur_y_right)
                self.append_cur_gaze_list(self.prior_x, self.prior_x_scaled, self.prior_y, self.prior_xleft, self.prior_xright, self.prior_y_left, self.prior_y_right)
                
        # check for horizontal saccade with scaled gaze
        elif (self.prior_x_scaled is not None) and (abs(curx2 - self.prior_x_scaled) >= (self.range_xvals2/4)): 
            self.num_looks_away = 0  
            self.cur_fix_hor = [cur_x]
            self.cur_fix_ver = [cur_y]
            self.cur_fix_ver_left = [cur_y_left]
            self.cur_fix_ver_right = [cur_y_right]
            self.cur_fix_hor_scaled = [curx2]
            self.cur_fix_xleft = [cur_x_left]
            self.cur_fix_xright = [cur_x_right]
            self.initialize_potential_gaze_list()
        else:
            self.append_cur_gaze_list(cur_x, curx2, cur_y, cur_x_left, cur_x_right, cur_y_left, cur_y_right)
            # print(curx2)
            
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
        self.prior_x, self.prior_x_scaled, self.prior_y = cur_x, curx2_original, cur_y  
        self.prior_xleft, self.prior_xright = cur_x_left, cur_x_right
        self.prior_y_left, self.prior_y_right = cur_y_left, cur_y_right
        
        return frame
                
    def update_frame(self, frame, frame2, timestamp):
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
        saccade = 0  
        xcoord, ycoord = None, None
        cur_y_left, cur_y_right = self.get_gazepoint(self.cur_fix_ver_left, self.cur_fix_ver_right, self.prior_y_left, self.prior_y_right)
        cur_x, cur_y = self.get_gazepoint(self.cur_fix_hor, self.cur_fix_ver, self.prior_x, self.prior_y)
        
        # if the baby has looked, get the current gaze point and put it on the frame
        if self.haslooked == True and (self.is_looking == True or self.num_looks_away < 3):
            xcoord = abs(int((cur_x - self.min_xval) * self.x_scale_value) - 960 )
            ycoord_left = abs(int((cur_y_left - self.min_yval_left) * self.y_scale_value_left) -540 ) 
            ycoord_right = abs(int((cur_y_right - self.min_yval_right) * self.y_scale_value_right) -540 ) 
            ycoord = int((ycoord_left + ycoord_right)/2)
            
            if ycoord < 0 or ycoord > 540:
                ycoord = abs(int((self.middle_y - self.min_yval) * self.y_scale_value) -540 ) 
            if xcoord < 0 or xcoord > 960:
                self.text = "away"
            if self.text == "saccade":
                saccade = 1
                left_coords, r_left = self.gaze.pupil_left_coords()
                right_coords, r_right = self.gaze.pupil_right_coords()
                
                # changes color of eyes
                cv2.circle(self.frame, left_coords, 3, (0, 0, 255), 1)
                cv2.circle(self.frame, right_coords, 3, (0, 0, 255), 1) 

            cv2.circle(frame2, (xcoord, ycoord), 15, color, 2)  
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
        
        cv2.putText(frame2, self.text, (20, 60), cv2.FONT_HERSHEY_DUPLEX, 0.9, color, 1)
        cv2.putText(frame2, str(round(timestamp,0)), (20, 30), cv2.FONT_HERSHEY_DUPLEX, 0.9, color, 1)
        return frame, frame2, cur_x, cur_y, xcoord, ycoord, saccade, self.text




def main():

    sub_count = 0
    sub_list = []
    for file in os.listdir("gaze_tracking/task/"):
        if file.endswith(".mp4") or file.endswith(".mov"):
            sub_list.append(file)
            print(os.path.join("gaze_tracking/task/", file))
    cwd = os.path.abspath(os.path.dirname(__file__))
  
    for sub in sub_list:
        try:  
            # change to 0 to skip calibration and use preset values instead
            calibrate = 1
            
            videoFilename = "gaze_tracking/task/" + sub 
            taskFilename = "gaze_tracking/task/task_videos/task_" + sub 
            calib_filename = "gaze_tracking/task/calibration_files/calibration_" + sub 
            outfilename = "gaze_tracking/task/annotated_videos/annotated_" + sub
            calib_file = os.path.abspath(os.path.join(cwd, calib_filename))
            videoFile = os.path.abspath(os.path.join(cwd, videoFilename))
            taskFile = os.path.abspath(os.path.join(cwd, taskFilename))
            outfile = os.path.abspath(os.path.join(cwd, outfilename))
            
            cap = cv2.VideoCapture(videoFile)   # capturing the baby video from the given path
            cap2 = cv2.VideoCapture(taskFile)   # capturing the task video from the given path
            fps = cap.get(5)
            if fps > 30: fps2 = 30
            else: fps2  = fps
            
            frameval = math.ceil(fps) // 30
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            
            out = cv2.VideoWriter(outfile, fourcc, fps2, (1920, 540))
            
            df = pd.DataFrame(columns = ['Subject_ID', 'Time', 'Frame', 'X-coord', 'Y-coord', 'Saccade', 'Tag'])

            count=0
            owlet = OWLET()
            if calibrate == 1: 
                owlet.calibrate_gaze(calib_file)
            owlet.initialize_eye_tracker()
    
            while (cap.isOpened()):
                frameId = cap.get(1) #current frame number
                ret, frame = cap.read()
                ret2, frame2 = cap2.read()               
    
                if (ret == False or ret2 == False):
                    break
                if (frameId % frameval == 0):
                    timestamp = cap.get(cv2.CAP_PROP_POS_MSEC)
                    frame = cv2.resize(frame, (960,540))
                    frame2 = cv2.resize(frame2, (960,540))
                    
                    frame = owlet.determine_gaze(frame)
                    frame, frame2, cur_x, cur_y, xcoord, ycoord, saccade, text = \
                        owlet.update_frame(frame, frame2, timestamp)

                    frame = cv2.flip(frame, 1)
                    final = cv2.hconcat([frame2, frame])
                    cv2.imshow(sub, final)
                    out.write(final)
                    df.loc[count] = [sub, timestamp, frameId, xcoord, ycoord, saccade, text]

                    count+=1
                    key = cv2.waitKey(1)
                    # press 'q' to quit
                    if key == ord('q'):
                        break
                    # press 'p' to pause/unpause
                    if key == ord('p'):
                        while (1):
                            newkey = cv2.waitKey(1)
                            if newkey == ord('p'):
                                break
                    if cv2.waitKey(1) == 27:
                        break
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
        
            cap.release()    
            out.release()
            print("Done: " + sub)
            cv2.destroyAllWindows()
            
            file4 = "gaze_tracking/task/csv_output/" + sub + ".csv"
            filename4 = os.path.abspath(os.path.join(cwd, file4))
            
            df.to_csv(filename4, index = False)
            sub_count += 1
        except Exception as e:
            print(e)
            continue

if __name__=='__main__':
    main()