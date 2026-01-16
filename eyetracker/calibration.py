"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
Assumptions: this code only works when the mom is higher than the baby
"""

import cv2
from .gaze_tracking_cnn import GazeTrackingCNN
import numpy as np
import math


class LookingCalibration(object):

    def __init__(self, cwd):
        self.gaze = GazeTrackingCNN(2.7, 4, 1, 1, cwd) # eventually replace this with means from babies
        self.hor_ratios = []
        self.ver_ratios = []
        self.blinks = []
        self.eye_areas = []
        self.check_range_zero = 0

    def calibrate_eyes(self, file):
        cap3 = cv2.VideoCapture(file)
        hor_look = 2
        ver_look = 2
        print(cap3.get(5))

        
        while (cap3.isOpened() ):
            ret, frame = cap3.read()

            self.timestamp = cap3.get(cv2.CAP_PROP_POS_MSEC)
            
            if (ret != True):
                break
            frame = cv2.resize(frame, (960,540))
            self.gaze.refresh(frame)
            frame = self.gaze.annotated_frame()
            hor_look, ver_look = self.gaze.xy_gaze_position()
            
            eyeratio = self.gaze.get_eye_area_ratio()

            if eyeratio is not None:
                self.eye_areas.append(eyeratio)

            blink = self.gaze.eye_ratio()
            if blink != 0:
                self.blinks.append(blink)

            if (hor_look is not None and not self.gaze.is_blinking()):
                if eyeratio is not None and (eyeratio > .77 and eyeratio < 1.3):
                    self.hor_ratios.append(hor_look)
            if (ver_look is not None and not self.gaze.is_blinking()):
                if eyeratio is not None and (eyeratio > .77 and eyeratio < 1.3):
                    self.ver_ratios.append(ver_look)

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

            if self.check_range_zero == 0: return 1.0
            return mean
        except:
            return 1.0


    def get_eye_ratio(self):

        try:
            self.blinks.sort()
            mid = len(self.blinks)//2
            mean = self.blinks[mid] #sum(blinks)/len(blinks)
            maximum = self.blinks[-1]
            minimum = self.blinks[0]
            if self.check_range_zero == 0: return (2.5, 3.5, 1.5 )
            return (mean, maximum, minimum)
        except:
            return (2.5, 3.5, 1.5 )

        
    def get_min_max_hor(self):
        try:
            min_look = min(self.hor_ratios)
            max_look = max(self.hor_ratios)
            range_vals = max_look - min_look
            middle = (min_look + max_look)/2
            if self.check_range_zero == 0: return .5, .8, .3, .65
            return min_look, max_look, range_vals, middle
        except:
            return .5, .8, .3, .65



    def get_min_max_ver(self):
        try:
            toplook = min(self.ver_ratios)
            downlook = max(self.ver_ratios)
            range_vals = downlook - toplook
            middle = (toplook + downlook)/2
            
           
            if self.check_range_zero == 0: return .025, .06, .035, .0425
    
            return toplook, downlook, range_vals, middle,
        except:
            return .025, .06, .035, .0425








