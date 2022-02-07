from __future__ import division
import os
import cv2
import dlib
from .eye import Eye


class GazeTracking(object):
    """
    This class tracks the user's gaze.
    It provides useful information like the position of the eyes
    and pupils and allows to know if the eyes are open or closed
    """

    def __init__(self, mean, maximum, minimum, ratio, length):
        self.frame = None
        self.eye_left = None
        self.eye_right = None
        self.face_index = 0
        self.face = None
        # _face_detector is used to detect faces
        self._face_detector = dlib.get_frontal_face_detector()
        self.eye_scale = mean
        self.blink_thresh = maximum * 1.1
        self.blink_thresh2 = minimum * .9
        self.leftpoint = None
        self.rightpoint = None
        self.leftright_eyeratio = ratio
        self.length = length

        # _predictor is used to get facial landmarks of a given face
        cwd = os.path.abspath(os.path.dirname(__file__))
        model_path = os.path.abspath(os.path.join(cwd, "trained_models/shape_predictor_68_face_landmarks.dat"))
        self._predictor = dlib.shape_predictor(model_path)
        eyepath = os.path.abspath(os.path.join(cwd, "trained_models/haarcascade_eye.xml"))
        self.eye_classifier = cv2.CascadeClassifier(eyepath)

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
        
        faces = self._face_detector(frame)
            
        ## if there are two faces detected, take the lower face
        if len(faces) > 1 and (faces[1].bottom() > faces[0].bottom()):
            self.face_index = 1
        ## if there are two faces detected, take the lower face
        elif len(faces) > 1 and (faces[1].bottom() <= faces[0].bottom()):
            self.face_index = 0
        else:
            self.face_index = 0
        
        try:
            landmarks = self._predictor(frame, faces[self.face_index])
            self.landmarks = landmarks
            self.eye_left = Eye(frame, landmarks, 0, self.leftpoint)
            self.eye_right = Eye(frame, landmarks, 1, self.rightpoint)
            self.face = faces[self.face_index]
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
            return None
        
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
            return ratio
        except Exception:
            return None
        
            
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

            yleft = (self.eye_left.pupil.y / self.eye_left.inner_y) 
            yright = (self.eye_right.pupil.y / self.eye_right.inner_y)
            yavg = (yleft + yright)/2
            
            scale =  self.eye_scale / self.eye_ratio()
            yavg = yavg * scale

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
        frame = self.frame.copy()

        if self.pupils_located:
            color = (255, 255, 0)
            left_coords, r_left = self.pupil_left_coords()
            right_coords, r_right = self.pupil_right_coords()
            cv2.circle(frame, left_coords, 3, color, 1)
            cv2.circle(frame, right_coords, 3, color, 1)    
            
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
        return frame
