from __future__ import division
import os
import cv2
import dlib
from .eye_cnn import EyeCNN
import numpy as np
# import face_recognition


class GazeTrackingCNN(object):
    """
    This class tracks the user's gaze.
    It provides useful information like the position of the eyes
    and pupils and allows to know if the eyes are open or closed
    """

    def __init__(self, mean, maximum, minimum, ratio, cwd):
        self.frame = None
        self.eye_left = None
        self.eye_right = None
        self.face_index = 0
        self.face = None
        self.counter = 0
        self.faces = []
        # _face_detector is used to detect faces
        self._face_detector = dlib.get_frontal_face_detector()
        cnn_model_path = os.path.abspath(os.path.join(cwd, "eyetracker/mmod_human_face_detector.dat"))
        self._face_detector = dlib.cnn_face_detection_model_v1(cnn_model_path)
        self.eye_scale = mean
        self.blink_thresh = maximum * 1.1
        self.blink_thresh2 = minimum * .9
        self.leftpoint = None
        self.rightpoint = None
        self.leftright_eyeratio = ratio
        self.eye_distance = None
        self.nose_distance = None
        self.landmarks = None
        if ratio==0:
            self.leftright_eyeratio = 1
        # _predictor is used to get facial landmarks of a given face
        self.cwd = cwd; #os.path.abspath(os.path.dirname(__file__))
        model_path = os.path.abspath(os.path.join(cwd, "eyetracker/shape_predictor_68_face_landmarks.dat"))
        model_path = os.path.abspath(os.path.join(cwd, "eyetracker/shape_predictor_68_face_landmarks_GTX.dat"))
        self._predictor = dlib.shape_predictor(model_path)
        self.top, self.bottom, self.left, self.right = 0, 540, 0, 960
        # self._predictor = dlib.shape_predictor(model_path)
        # eyepath = os.path.abspath(os.path.join(cwd, "=haarcascade_eye.xml"))
        # self.eye_classifier = cv2.CascadeClassifier(eyepath)

    @property
    def pupils_located(self):
        """Check that the pupils have been located"""
        try:
            int(self.eye_left.pupil.x)
            int(self.eye_left.pupil.y)
            int(self.eye_right.pupil.x)
            int(self.eye_right.pupil.y)
            return True
        except Exception:
            #    return True
            return False

    def _analyze(self):
        """Detects the face and initialize Eye objects"""
     
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        
        # this may improve video quality in poor lighting conditions
        # frame = cv2.addWeighted(frame, 1, frame, .7, -20) 

        # cols, rows = frame.shape
        # indices = np.where(frame < 230)
        # indices = np.logical_and(frame > 50, frame < 230)
        # brightness = np.sum(frame[indices]) / (255 * cols * rows)
        # ratio = brightness / .5
        # frame2 = frame.copy()
        # if ratio < 1:
        #     frame2 = cv2.convertScaleAbs(frame2, alpha = 1/ratio, beta = 0)
        # print(roi.shape)
        # print(frame.shape)
        # input()
        if self.counter==0 or self.counter%5==0:
            self.faces = self._face_detector(frame,0)
        self.counter += 1
        ## if there are two faces detected, take the lower face
        if len(self.faces) > 1 and (self.faces[1].rect.bottom() > self.faces[0].rect.bottom()):
            self.face_index = 1
        # if len(self.faces) > 1 and (self.faces[1].bottom() > self.faces[0].bottom()):
        #     self.face_index = 1
        ## if there are two faces detected, take the lower face
        # elif len(self.faces) > 1 and (self.faces[1].bottom() <= self.faces[0].bottom()):
        #     self.face_index = 0
        elif len(self.faces) > 1 and (self.faces[1].rect.bottom() <= self.faces[0].rect.bottom()):
            self.face_index = 0
        else:
            self.face_index = 0
        
        try:
            # print(self.face_index)
            d = self.faces[self.face_index]
            de = dlib.rectangle(d.rect.left(),d.rect.top(),d.rect.right(),d.rect.bottom())
            # landmarks = self._predictor(frame, self.faces[self.face_index])
            # print(self.top, self.bottom, self.left, self.right)
            landmarks = self._predictor(frame, de)
            self.landmarks = landmarks
            self.eye_left = EyeCNN(frame, landmarks, 0, self.leftpoint)
            self.eye_right = EyeCNN(frame, landmarks, 1, self.rightpoint)
            self.face = self.faces[self.face_index]
            self.chin = landmarks.part(8).y
            try:
                self.leftpoint = (self.eye_left.pupil.x, self.eye_left.pupil.y)
                self.rightpoint = (self.eye_right.pupil.x, self.eye_right.pupil.y)
            except:
                self.leftpoint = None
                self.rightpoint = None

        except IndexError:
                self.eye_left = None
                self.eye_right = None
                self.face = None

    def refresh(self, frame):
        """Refreshes the frame and analyzes it.
        Arguments:
            frame (numpy.ndarray): The frame to analyze
        """
        self.frame = frame
        self._analyze()
        draw_pupils, left_coords, right_coords = self.annotated_frame()
        
        return draw_pupils, left_coords, right_coords 

    def get_eye_distance(self):
        try:
            if self.landmarks:
                left_eye = np.array([self.landmarks.part(36).x, self.landmarks.part(36).y])
                right_eye = np.array([self.landmarks.part(45).x, self.landmarks.part(45).y])
                nose = np.array([self.landmarks.part(30).x, self.landmarks.part(30).y])
                distance1 = np.linalg.norm(left_eye - nose)
                distance2 = np.linalg.norm(right_eye - nose)
                avg_distance = distance1/distance2
                if self.eye_distance is not None:
                    avg_distance = (self.eye_distance + avg_distance)/2
                self.eye_distance = avg_distance
                return(self.eye_distance)
        except:
            return 1

    def get_nose_distance(self):
        try:
            if self.landmarks:
                forehead = np.array([self.landmarks.part(27).x, self.landmarks.part(27).y])
                nose = np.array([self.landmarks.part(30).x, self.landmarks.part(30).y])
                distance1 = np.linalg.norm(forehead - nose)
                left_eye = np.array([self.landmarks.part(36).x, self.landmarks.part(36).y])
                right_eye = np.array([self.landmarks.part(45).x, self.landmarks.part(45).y])
                distance2 = np.linalg.norm(right_eye - left_eye)

                avg_distance = distance1/distance2
                if self.nose_distance is not None:
                    avg_distance = (self.nose_distance + avg_distance)/2
                self.nose_distance = avg_distance

                return(self.nose_distance)
        except:
            return None

    def get_landmarks(self):
        """Refreshes the frame and analyzes it.
        Arguments:
            frame (numpy.ndarray): The frame to analyze
        """
        LANDMARKS = set(list([18, 20, 23, 25, 27, 30, 33, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48]))
                # LANDMARKS = set(list(range(0,18)))
        points = []

        if self.landmarks:
            for point in LANDMARKS:
                x = self.landmarks.part(point).x
                y = self.landmarks.part(point).y
                points.append((x,y))

            return points
        else:
            return None
    
    def pupil_left_coords(self):
        """Returns the xy coordinates and radius of the left pupil"""
        if self.pupils_located:
            x = self.eye_left.origin[0] + self.eye_left.pupil.x
            y = self.eye_left.origin[1] + self.eye_left.pupil.y
            r = self.eye_left.pupil.radius
            return (x, y), r
        else:
            return (None, None), None

    def pupil_right_coords(self):
        """Returns the xy coordinates and radius  of the right pupil"""
        if self.pupils_located:
            x = self.eye_right.origin[0] + self.eye_right.pupil.x
            y = self.eye_right.origin[1] + self.eye_right.pupil.y
            r = self.eye_right.pupil.radius
            return (x, y), r
        else:
            return (None, None), None
        
    def check_face(self):
        """Returns whether a face was found or not"""
        return ((self.face_index == 4 or self.face is None) and \
                self.eye_left is None and self.eye_right is None)

    def face_coords(self):
        """Returns the coordinates of the baby's face"""
        try:
            faces = self._face_detector(self.frame)
            x = faces[self.face_index].left()
            y = faces[self.face_index].top()
            w = faces[self.face_index].right() # - x
            h = faces[self.face_index].bottom() # - y
            return (x, y, w, h)
        except IndexError:
            return (None, None, None, None)
        
    def get_eye_area(self):
        """Returns the average area of the baby's right and left eyes"""
        try:
            leftArea = self.eye_left.area  
            rightArea = self.eye_right.area
            avg = (leftArea + rightArea)/2
            return avg
        except Exception:
            return 1
        
    def get_LR_eye_area(self):
        """Returns the  areas of the baby's right and left eyes"""
        try:
            leftArea = self.eye_left.area 
            rightArea = self.eye_right.area
            return leftArea, rightArea
        except Exception:
            return None
        
        
    def get_eye_area_ratio(self):
        """Returns the ratio of the baby's right and left eye areas"""
        try:
            leftArea = self.eye_left.area  
            rightArea = self.eye_right.area
            ratio = (leftArea / rightArea)
                # print(ratio)
            # cv2.putText(self.frame, str(rattio) (20, 90), cv2.FONT_HERSHEY_DUPLEX, 0.9, color, 1)
            return ratio
        except Exception:
            return 1
        
            
    def xy_gaze_position(self):
        """Returns values reflecting the average horizontal  
        and vertical direction of the pupils. The extreme
        values are determined during calibration or are
        set to average values imputed from prior videos
        """
        if self.pupils_located:
            
            xleft = (self.eye_left.pupil.x ) /  self.eye_left.width 
            xright = (self.eye_right.pupil.x ) / self.eye_right.width 
            xavg = (xleft + xright)/2
            # print(self.eye_left.pupil.y, self.eye_left.height)

            left_eye = np.array([self.eye_left.pupil.x, self.eye_left.pupil.y])
            distance1 = np.linalg.norm(left_eye - self.eye_left.top)
            distance2 = np.linalg.norm(left_eye - self.eye_left.bottom)
            left_distance = distance1 + distance2
            yleft = distance1/left_distance

            right_eye = np.array([self.eye_right.pupil.x, self.eye_right.pupil.y])
            distance1 = np.linalg.norm(right_eye - self.eye_right.top)
            distance2 = np.linalg.norm(right_eye - self.eye_right.bottom)
            right_distance = distance1 + distance2
            yright = distance1/right_distance

            # yleft = (self.eye_left.pupil.x / self.eye_left.pupil.y) 
            # yright = (self.eye_right.pupil.y / self.eye_right.pupil.y)

            # yright = (self.eye_right.pupil.y / self.eye_right.height)
            yavg = (yleft + yright)/2
            
            scale =  self.eye_scale / self.eye_ratio()
            # scale = self.get_nose_distance() 
            
            yavg = scale * yavg 
            # print(yavg)
            return xavg, yavg, yleft, yright
        else:
            return None, None, None, None
        
        
    def horizontal_gaze_scaled(self):
        """Returns a value reflecting the horizontal 
        gaze direction. This is calcuated by integrating 
        the pupil position with the degree that the head 
        is rotated, estimated by the eye area ratio
        """
        if self.pupils_located:
            left, right = self.horizontal_gaze() #left = (self.eye_left.pupil.x ) / self.eye_left.width # (self.eye_left.center[0] * 2)
            area_ratio = (self.eye_left.area /self.eye_right.area) / self.leftright_eyeratio
            scaled_avg = ((left + right)/2)*area_ratio
            return (scaled_avg)
        else:
            return None

    def horizontal_gaze(self):
        """Returns values reflecting the horizontal direction
        of the left and right pupils. The extreme values are 
        determined during calibration or are set to average 
        values imputed from prior videos.
        """
        if self.pupils_located:
            pupil_left = (self.eye_left.pupil.x ) / self.eye_left.width # (self.eye_left.center[0] * 2) 
            pupil_right = (self.eye_right.pupil.x ) /  self.eye_right.width #  (self.eye_right.center[0] * 2)
            return pupil_left, pupil_right
        else:
            return None, None

    def is_blinking(self):
        """Returns true if the current blinking ratio is greater than 
        the threshold set during calibration
        """
        if self.pupils_located:
            blinking_ratio = self.eye_ratio()
            return blinking_ratio > self.blink_thresh or blinking_ratio < self.blink_thresh2 
        
    def eye_ratio(self):
        """Returns the average width/height (blinking ratio) of left/right eyes"""
        if self.pupils_located:      
            blinking_ratio = (self.eye_left.blinking + self.eye_right.blinking)/2 # (left_ratio + right_ratio)/2
        else:
            blinking_ratio = 1
        return blinking_ratio
        

    def annotated_frame(self):
        """Returns the frame with pupils highlighted"""
        # frame = self.frame.copy()

        if self.pupils_located:

            left_coords, r_left = self.pupil_left_coords()
            right_coords, r_right = self.pupil_right_coords()
            return True, left_coords, right_coords
            # cv2.circle(frame, left_coords, 3, color, 1)
            # cv2.circle(frame, right_coords, 3, color, 1)    
        return False, None, None
            
            # uncomment to display points around the eyes and face
            # points = [36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]
            # cv2.line(frame, (x_left - 5, y_left), (x_left + 5, y_left), color)
            # cv2.line(frame, (x_left, y_left - 5), (x_left, y_left + 5), color)
            # cv2.line(frame, (x_right - 5, y_right), (x_right + 5, y_right), color)
            # cv2.line(frame, (x_right, y_right - 5), (x_right, y_right + 5), color)
            # pt1 = (self.face.left(), self.face.top())
            # pt2 = (self.face.right(), self.face.bottom())
            # cv2.rectangle(frame, pt1, pt2, (0, 255, 0))
            # for point in points:
            #     x = self.landmarks.part(point).x
            #     y = self.landmarks.part(point).y
            #     cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)
        # return frame
