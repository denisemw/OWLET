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
        self.gaze = GazeTracking(2.7, 4, 1, 1, 1, cwd) # eventually replace this with means from babies
        
       # self.videoFile =  None #"Natalie_calib.mp4"
       # self.cap3 =  None   # capturing the video from the given path
     #   self.frameRate = 4 # cap3.get(5) # 4 # 60 frames per sec, so framerate = 4 is 15 steps per sec  #cap3.get(5) #frame rate
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
        self.lengths = []
        self.timestamp = 0
        self.show_output = show_output
        self.cwd = cwd
        

    def calibrate_eyes(self, file, calib_starttime):
        cap3 = cv2.VideoCapture(file)
        hor_look = 2
        ver_look = 2
        
        frameId = cap3.get(1) #current frame number
        
        fps = cap3.get(5)
                
        frameval = math.ceil(fps) // 30
        
        while (cap3.isOpened() and self.timestamp < (calib_starttime + 25000)):
            ret, frame = cap3.read()
            start = calib_starttime - 1000
            end = calib_starttime + 25000
            self.timestamp = cap3.get(cv2.CAP_PROP_POS_MSEC)
            if (ret != True):
                break
            if frameId % frameval == 0:
                frame = cv2.resize(frame, (960,540))

            # We send this frame to GazeTracking to analyze it
                self.gaze.refresh(frame)

                
                frame = self.gaze.annotated_frame()
                hor_look2 = self.gaze.horizontal_gaze_scaled()                
                hor_look, ver_look, ver_look_left, ver_look_right = self.gaze.xy_gaze_position()
                
                eyearea = self.gaze.get_eye_area()
                #leftarea, rightarea = self.gaze.get_LR_eye_area()
                eyeratio = self.gaze.get_eye_area_ratio()
                
                # length = self.gaze.face_length()
                # if length is not None:
                    # self.lengths.append(length)
                
                if eyearea is not None:
                    self.areas.append(eyearea)
                    
                if eyeratio is not None:
                    self.eye_areas.append(eyeratio)

                
                blink = self.gaze.eye_ratio()
                if blink != 0:
                    self.blinks.append(blink)
                # prior_hor_look = hor_look
                # prior_ver_look = ver_look
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
                    
               # frame = cv2.flip(frame, 1)
                if self.show_output:
                    cv2.putText(frame, "Calibrating...", (20, 30), cv2.FONT_HERSHEY_DUPLEX, 0.9, (255, 255, 0), 1)
                    cv2.imshow("Calibration", frame)
            if cv2.waitKey(1) == 27:
                break
        cap3.release()
        cv2.destroyAllWindows()
        for i in range (1,5):
                    cv2.waitKey(1)
        
    def get_eye_area_ratio(self):
        # try:
            l=np.array(self.eye_areas)
            blinks = l[(l>np.quantile(l,0)) & (l<np.quantile(l,1))].tolist()
            blinks.sort()
            mean = sum(blinks)/len(blinks)
            maximum = blinks[-1]
            minimum = blinks[0]
            # print(mean, maximum, minimum)
            return (mean, maximum, minimum)
        # except Exception:
        #     return 2.7, 3.5, 2

    def get_eye_ratio(self):
        # try:
            l=np.array(self.blinks)
            blinks = l[(l>np.quantile(l,0)) & (l<np.quantile(l,1))].tolist()
            blinks.sort()
            mid = len(blinks)//2
            mean = blinks[mid] #sum(blinks)/len(blinks)
            maximum = blinks[-1]
            minimum = blinks[0]

            # print(mean, maximum, minimum)
            return (mean, maximum, minimum)
        # except Exception:
        #     return 2.7, 3.5, 2
    
    def get_avg_length(self):
        # try:
            # l=np.array(self.lengths)
            # final_areas = l[(l>np.quantile(l,.1)) & (l<np.quantile(l,.9))].tolist()
            # mean = sum(final_areas)/len(final_areas)
            mean = 100
            return (mean)
        
    def get_eye_area(self):
        # try:
            l=np.array(self.areas)
            final_areas = l[(l>np.quantile(l,.1)) & (l<np.quantile(l,.9))].tolist()
            mean = sum(final_areas)/len(final_areas)
            return (mean)
        # except Exception:
        #     return None
        
    # returns non sclae
    def get_min_max_hor(self):
        #res = [i for i in self.hor_ratios if i]
        # try:
            looks=np.array(self.hor_ratios)
            mid = len(looks)//2
            looks=looks[0:mid]
            # looks = l[(l>np.quantile(l,0.1)) & (l<np.quantile(l,0.9))].tolist()
            looks.sort()
            min_look = looks[0]
            max_look = looks[-1]
            range_vals = max_look - min_look
            middle = (min_look + max_look)/2
            # print ("left look" + str(min_look))
            # print ("right look" + str(max_look))
            return min_look, max_look, range_vals, middle
        # except:
        #     return .42, .58, .16, .5
        
        
    def get_min_max_hor2(self):
        #res = [i for i in self.hor_ratios if i]
        # try:
            looks=np.array(self.hor_ratios2)
            mid = len(looks)//2
            looks=looks[0:mid]
            # looks = l[(l>np.quantile(l,0.1)) & (l<np.quantile(l,0.9))].tolist()
            looks.sort()
            min_look = looks[0]
            max_look = looks[-1]
            range_vals = max_look - min_look
            middle = (min_look + max_look)/2
            # print ("left look" + str(min_look))
            # print ("right look" + str(max_look))
            return min_look, max_look, range_vals, middle
        # except:
        #     return .42, .58, .16, .5

    def get_min_max_ver(self):
        # try:
            looks=np.array(self.ver_ratios)
            mid = len(looks)//2
            looks=looks[mid:len(looks)]
            # looks = l[(l>np.quantile(l,0.05)) & (l<np.quantile(l,0.95))].tolist()
            looks.sort()
            toplook = looks[0]
            downlook = looks[-1]
            # print ("top look" + str(toplook))
            # print ("down look" + str(downlook))
            range_vals = downlook - toplook
            
            looks=np.array(self.ver_ratios_left)
            mid = len(looks)//2
            looks=looks[mid:len(looks)]
            # looks = l[(l>np.quantile(l,0.05)) & (l<np.quantile(l,0.95))].tolist()
            looks.sort()
            toplook_left = looks[0]
            downlook = looks[-1]
            # print ("top look" + str(toplook))
            # print ("down look" + str(downlook))
            range_vals_left = downlook - toplook
            
            looks=np.array(self.ver_ratios_right)
            mid = len(looks)//2
            looks=looks[mid:len(looks)]
            # looks = l[(l>np.quantile(l,0.05)) & (l<np.quantile(l,0.95))].tolist()
            looks.sort()
            toplook_right = looks[0]
            downlook = looks[-1]
            # print ("top look" + str(toplook))
            # print ("down look" + str(downlook))
            range_vals_right = downlook - toplook
            middle = (toplook + downlook)/2
            return toplook, downlook, range_vals, middle, range_vals_left, range_vals_right, toplook_left, toplook_right
        # except:
        #     return .48, .52, .04, .5

    def get_min_max_left(self):
        res = self.left_ratios
        min_val = min(res)
        max_val = max(res)
        range_vals = max_val - min_val
        middle = (max_val + min_val)/2
        return min_val, max_val, range_vals, middle

    def get_min_max_right(self):
        res = self.right_ratios
        min_val = min(res)
        max_val = max(res)
        range_vals = max_val - min_val
        middle = (max_val + min_val)/2
        return min_val, max_val, range_vals, middle







