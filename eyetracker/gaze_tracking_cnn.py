from __future__ import division
import os
import cv2
import dlib
from .eye_cnn import EyeCNN
import numpy as np
# import face_recognition
CONFIDENCE_THRESHOLD = 7

class GazeTrackingCNN(object):
    """
    This class tracks the user's gaze.
    It provides useful information like the position of the eyes
    and pupils and allows to know if the eyes are open or closed
    """

    MODEL_POINTS = np.array([
        (0.0, 0.0, 0.0),          # Nose tip
        (0.0, -330.0, -65.0),     # Chin
        (-225.0, 170.0, -135.0),  # Left eye left corner
        (225.0, 170.0, -135.0),   # Right eye right corner
        (-150.0, -150.0, -125.0), # Left Mouth corner
        (150.0, -150.0, -125.0)   # Right mouth corner
    ], dtype=np.float64)
    
    DIST_COEFFS = np.zeros((4,1))

    FOCAL_LENGTH = 960
    CAMERA_MATRIX = np.array([
        [FOCAL_LENGTH, 0, 960 / 2],
        [0, FOCAL_LENGTH, 540 / 2],
        [0, 0, 1]
    ], dtype=np.float64)
    
    def __init__(self, mean, maximum, minimum, ratio, cwd):
        self.frame = None
        self.eye_left = None
        self.eye_right = None
        self.face_index = 0
        self.face = None
        # _face_detector is used to detect faces
        self._face_detector = dlib.get_frontal_face_detector()
        self.tracker = None
        self.tracking = False
        cnn_model_path = os.path.abspath(os.path.join(cwd, "eyetracker/mmod_human_face_detector.dat"))
        self._face_detector = dlib.cnn_face_detection_model_v1(cnn_model_path)
        self.eye_scale = mean
        self.blink_thresh_upper = maximum * 1.1
        self.blink_thresh_lower = minimum * .9
        self.leftpoint = None
        self.rightpoint = None
        self.leftright_eyeratio = ratio
        self.eye_distance = None
        self.landmarks = None
        if ratio==0:
            self.leftright_eyeratio = 1
        # _predictor is used to get facial landmarks of a given face
        model_path = os.path.abspath(os.path.join(cwd, "eyetracker/shape_predictor_68_face_landmarks_GTX.dat"))
        self._predictor = dlib.shape_predictor(model_path)
        


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
    def detect_and_init_tracker(self, frame):
        detections = self._face_detector(frame, 1)

        if len(detections) == 0:
            return False, None

            ## if there are two faces detected, take the lower face
        if len(detections) > 1 and (detections[1].rect.bottom() > detections[0].rect.bottom()):
            self.face_index = 1
        elif len(detections) > 1 and (detections[1].rect.bottom() <= detections[0].rect.bottom()):
            self.face_index = 0
        else:
            self.face_index = 0

        # Choose face (e.g., largest or lowest)
        self.face = detections[self.face_index]
        self.tracker = dlib.correlation_tracker()
        bbox = dlib.rectangle(
            int(self.face.rect.left()),
            int(self.face.rect.top()),
            int(self.face.rect.right()),
            int(self.face.rect.bottom())
        )
        self.tracker.start_track(frame,bbox)
        self.tracking = True
        return True,  bbox

    def update_tracker(self, frame):
        confidence = self.tracker.update(frame)
        self.face = self.tracker.get_position()
        bbox = dlib.rectangle(
            int(self.face.left()),
            int(self.face.top()),
            int(self.face.right()),
            int(self.face.bottom())
        )
        # Convert to integers
     

        return confidence, bbox
    
    def _analyze(self):
        """Detects the face and initialize Eye objects"""
     
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        if not self.tracking:
            success, bbox = self.detect_and_init_tracker(frame)
        else:
            confidence, bbox = self.update_tracker(frame)
            success = True
            if confidence < CONFIDENCE_THRESHOLD:
                self.tracking = False
                self.tracker = None
                success, bbox = self.detect_and_init_tracker(frame)

        if success:
            self.landmarks = self._predictor(frame, bbox)
            self.eye_left = EyeCNN(frame, self.landmarks, 0, self.leftpoint)
            self.eye_right = EyeCNN(frame, self.landmarks, 1, self.rightpoint)
            try:
                self.leftpoint = (self.eye_left.pupil.x, self.eye_left.pupil.y)
                self.rightpoint = (self.eye_right.pupil.x, self.eye_right.pupil.y)
            except:
                self.leftpoint = None
                self.rightpoint = None
        else:
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

    def get_image_points(self):
        image_points = np.array([
            (self.landmarks.part(30).x, self.landmarks.part(30).y),  # Nose
            (self.landmarks.part(8).x, self.landmarks.part(8).y),    # Chin
            (self.landmarks.part(36).x, self.landmarks.part(36).y),  # Left eye
            (self.landmarks.part(45).x, self.landmarks.part(45).y),  # Right eye
            (self.landmarks.part(48).x, self.landmarks.part(48).y),  # Left mouth
            (self.landmarks.part(54).x, self.landmarks.part(54).y)   # Right mouth
        ], dtype=np.float64)

        success, rotation_vec, translation_vec = cv2.solvePnP(
            self.MODEL_POINTS,
            image_points,
            self.CAMERA_MATRIX,
            self.DIST_COEFFS,
            flags=cv2.SOLVEPNP_ITERATIVE
        )

        rotation_matrix, _ = cv2.Rodrigues(rotation_vec)
        # forward = rotation_matrix @ np.array([[0], [0], [1]])
        # fx, fy, fz = forward.flatten()
        # score = fz / np.linalg.norm(forward)

        proj_matrix = np.hstack((rotation_matrix, translation_vec))

        _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(proj_matrix)

        pitch, yaw, roll = euler_angles.flatten()
        roll = (roll + 180) % 360 - 180
        # print(score)
        return yaw, pitch, roll 

    
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
    
    def pupil_left_coords(self):
        """Returns the xy coordinates and radius of the left pupil"""
        if self.eye_left and self.eye_right:
            if self.eye_left.pupil.x and self.eye_left.pupil.y and self.eye_right.pupil.x and self.eye_right.pupil.y:
                x = self.eye_left.origin[0] + self.eye_left.pupil.x
                y = self.eye_left.origin[1] + self.eye_left.pupil.y
                r = self.eye_left.pupil.radius
                return (x, y), r
            else:
                return (None, None), None
        else:
            return (None, None), None

    def pupil_right_coords(self):
        """Returns the xy coordinates and radius  of the right pupil"""
        if self.eye_left and self.eye_right:
            if self.eye_left.pupil.x and self.eye_left.pupil.y and self.eye_right.pupil.x and self.eye_right.pupil.y:
                x = self.eye_right.origin[0] + self.eye_right.pupil.x
                y = self.eye_right.origin[1] + self.eye_right.pupil.y
                r = self.eye_right.pupil.radius
                return (x, y), r
            else:
                return (None, None), None
        else:
            return (None, None), None
        
        
    def get_eye_area(self):
        """Returns the average area of the baby's right and left eyes"""
        try:
            leftArea = self.eye_left.area  
            rightArea = self.eye_right.area
            avg = (leftArea + rightArea)/2
            return avg
        except Exception:
            return 1
        
    def get_eye_area_ratio(self):
        """Returns the ratio of the baby's right and left eye areas"""
        try:
            leftArea = self.eye_left.area  
            rightArea = self.eye_right.area
            ratio = (leftArea / rightArea)

            return ratio
        except Exception:
            return 1
        
            
    def xy_gaze_position(self):
        """Returns values reflecting the average horizontal  
        and vertical direction of the pupils. The extreme
        values are determined during calibration or are
        set to average values imputed from prior videos
        """
        if self.eye_left and self.eye_right:
            if self.eye_left.pupil.x and self.eye_left.pupil.y and self.eye_right.pupil.x and self.eye_right.pupil.y:            
                xleft = (self.eye_left.pupil.x ) /  self.eye_left.width 
                xright = (self.eye_right.pupil.x ) / self.eye_right.width 
                xavg = (xleft + xright)/2

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

                yavg = (yleft + yright)/2
                
                scale =  self.eye_scale / self.eye_ratio()
                
                yavg = scale * yavg 
                return xavg, yavg
            else:
                return None, None
        else:
            return None, None
        


    def horizontal_gaze(self):
        """Returns values reflecting the horizontal direction
        of the left and right pupils. The extreme values are 
        determined during calibration or are set to average 
        values imputed from prior videos.
        """
        if self.eye_left and self.eye_right:
            if self.eye_left.pupil.x and self.eye_left.pupil.y and self.eye_right.pupil.x and self.eye_right.pupil.y:
                pupil_left = (self.eye_left.pupil.x ) / self.eye_left.width # (self.eye_left.center[0] * 2) 
                pupil_right = (self.eye_right.pupil.x ) /  self.eye_right.width #  (self.eye_right.center[0] * 2)
                return pupil_left, pupil_right
            else:
                return None, None
        else:
            return None, None

    def is_blinking(self):
        """Returns true if the current blinking ratio is greater than 
        the threshold set during calibration
        """
        if self.eye_left and self.eye_right:
            blinking_ratio = self.eye_ratio()
            return blinking_ratio > self.blink_thresh_upper or blinking_ratio < self.blink_thresh_lower
        
    def eye_ratio(self):
        """Returns the average width/height (blinking ratio) of left/right eyes"""
        if self.eye_left and self.eye_right:
            if self.eye_left.pupil.x and self.eye_left.pupil.y and self.eye_right.pupil.x and self.eye_right.pupil.y:            blinking_ratio = (self.eye_left.blinking + self.eye_right.blinking)/2 # (left_ratio + right_ratio)/2
        else:
            blinking_ratio = 1
        return blinking_ratio
        

    def annotated_frame(self):
        """Returns the frame with pupils highlighted"""

        try: 
            # if self.eye_left.pupil.x and self.eye_left.pupil.y and self.eye_right.pupil.x and self.eye_right.pupil.y:

            left_coords, _ = self.pupil_left_coords()
            right_coords, _ = self.pupil_right_coords()
            return True, left_coords, right_coords
        except:
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
