"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
Assumptions: this code only works when the mom is higher than the baby
"""

import cv2
from gaze_tracking import GazeTracking
import numpy as np
import math


class LookingCalibration(object):

    def __init__(self, show_output, cwd):
        self.frame = None
        self.eye_left = None
        self.eye_right = None
        self.gaze = GazeTracking(2.7, 4, 1, 1, cwd) # eventually replace this with means from babies
        self.hor_ratios = []
        self.hor_ratios2 = []
        self.left_ratios = []
        self.right_ratios = []
        self.ver_ratios = []
        self.ver_ratios_left = []
        self.ver_ratios_right = []
        self.blinks = []
        self.areas = []
        self.eye_areas = []
        self.timestamp = 0
        self.show_output = show_output
        self.cwd = cwd
        self.check_range_zero = 0

    def calibrate_eyes(self, file, calib_starttime):
        cap3 = cv2.VideoCapture(file)
        hor_look = 2
        ver_look = 2
        print(cap3.get(5))

        
        while (cap3.isOpened() ):
            ret, frame = cap3.read()
            start = calib_starttime - 1000
            # print(frame)
            


            self.timestamp = cap3.get(cv2.CAP_PROP_POS_MSEC)
            
            if (ret != True):
                break
            if self.timestamp >= start: 
                # print(self.timestamp)
                frame = cv2.resize(frame, (960,540))

                self.gaze.refresh(frame)
                frame = self.gaze.annotated_frame()
                hor_look2 = self.gaze.horizontal_gaze_scaled()                
                hor_look, ver_look, ver_look_left, ver_look_right = self.gaze.xy_gaze_position()
                
                eyearea = self.gaze.get_eye_area()
                eyeratio = self.gaze.get_eye_area_ratio()
                
                if eyearea is not None:
                    self.areas.append(eyearea)
                    
                if eyeratio is not None:
                    self.eye_areas.append(eyeratio)

                
                blink = self.gaze.eye_ratio()
                if blink != 0:
                    self.blinks.append(blink)

                if (hor_look is not None and not self.gaze.is_blinking()):
                    if eyeratio is not None and (eyeratio > .77 and eyeratio < 1.3):
                        self.hor_ratios.append(hor_look)
                        self.hor_ratios2.append(hor_look2)
                    # print("hor look: " + str(hor_look))
                if (ver_look is not None and not self.gaze.is_blinking()):
                    if eyeratio is not None and (eyeratio > .77 and eyeratio < 1.3):
                        self.ver_ratios.append(ver_look)
                        self.ver_ratios_left.append(ver_look_left)
                        self.ver_ratios_right.append(ver_look_right)
                    
                if self.show_output:
                    cv2.putText(frame, "Calibrating...", (20, 30), cv2.FONT_HERSHEY_DUPLEX, 0.9, (255, 255, 0), 1)
                    cv2.imshow("Calibration", frame)
            if cv2.waitKey(1) == 27:
                break
        cap3.release()
        cv2.destroyAllWindows()
        for i in range (1,5):
                    cv2.waitKey(1)
                  
        if len(self.hor_ratios) > 0:
            min_look = min(self.hor_ratios)
            max_look = max(self.hor_ratios)
            self.check_range_zero = max_look - min_look
            print("range ", self.check_range_zero)
        else:
            self.check_range_zero = 0
    def get_eye_area_ratio(self):

        try:
            mean = np.mean(self.eye_areas) 
            maximum = max(self.eye_areas) 
            minimum = min(self.eye_areas) 
            # if self.check_range_zero == 0: return (1.0, 1.35, .65)
            return (mean, maximum, minimum)
        except:
            return (1.0, 1.35, .65)


    def get_eye_ratio(self):

        try:
            self.blinks.sort()
            mid = len(self.blinks)//2
            mean = self.blinks[mid] #sum(blinks)/len(blinks)
            maximum = self.blinks[-1]
            minimum = self.blinks[0]
            # if self.check_range_zero == 0: return (2.5, 3.5, 1.5 )
            return (mean, maximum, minimum)
        except:
            return (2.5, 3.5, 1.5 )
        
    def get_eye_area(self):
        try:
            if self.check_range_zero == 0: return -999
            return (np.mean(self.areas))
        except:
            return -999

        
    def get_min_max_hor(self):
        try:
            min_look = min(self.hor_ratios)
            max_look = max(self.hor_ratios)
            range_vals = max_look - min_look
            middle = (min_look + max_look)/2
            # if self.check_range_zero == 0: return .5, .8, .3, .65
            return min_look, max_look, range_vals, middle
        except:
            return .5, .8, .3, .65

    def get_min_max_hor2(self):
        try:
            min_look = min(self.hor_ratios2)
            max_look = max(self.hor_ratios2)
            range_vals = max_look - min_look
            middle = (min_look + max_look)/2
            # if self.check_range_zero == 0: return .4, .9, .5, .65
            return min_look, max_look, range_vals, middle
        except:
            return .4, .9, .5, .65


    def get_min_max_ver(self):
        try:
            toplook = min(self.ver_ratios)
            downlook = max(self.ver_ratios)
            range_vals = downlook - toplook
            middle = (toplook + downlook)/2
            
            toplook_left = min(self.ver_ratios_left)
            downlook_left = max(self.ver_ratios_left)
            range_vals_left = downlook_left - toplook_left
            
            toplook_right = np.min(self.ver_ratios_right)
            downlook_right = np.max(self.ver_ratios_right)
            range_vals_right = downlook_right - toplook_right
            # if self.check_range_zero == 0: return .025, .06, .035, .0425, .035, .035, .025, .025
    
            return toplook, downlook, range_vals, middle, range_vals_left, range_vals_right, toplook_left, toplook_right
        except:
            return .025, .06, .035, .0425, .035, .035, .025, .025








