import math
import numpy as np
import cv2
from pupil import Pupil


class Eye(object):
    """
    This class creates a new frame to isolate the eye and
    initiates the pupil detection.
    """

    LEFT_EYE_POINTS = [36, 37, 38, 39, 40, 41]
    RIGHT_EYE_POINTS = [42, 43, 44, 45, 46, 47]
    LEFT_EYE_POINTS = [0, 1, 2, 3, 4, 5]
    RIGHT_EYE_POINTS = [6, 7, 8, 9, 10, 11]

    CHIN_NOSE = [8, 33]
    NOSE = [33, 28]
    

    def __init__(self, original_frame, landmarks, side, pupilpoint):
        self.frame = None
        self.origin = None
        self.center = None
        self.height = None
        self.width = None
        self.pupil = None
        self.min_x = None
        self.max_x = None
        self.min_y = None
        self.max_y = None
        self.region = None
        self.point = pupilpoint

        self._analyze(original_frame, landmarks, side)


    def _isolate(self, frame, landmarks, points, side):
        """Isolate an eye, to have a frame without other part of the face.

        Arguments:
            frame (numpy.ndarray): Frame containing the face
            landmarks (dlib.full_object_detection): Facial landmarks for the face region
            points (list): Points of an eye (from the 68 Multi-PIE landmarks)
            side: Indicates whether it's the left eye (0) or the right eye (1)
        """

        region = np.array([(landmarks[point][0], landmarks[point][1]) for point in points])
        region = region.astype(np.int32)

        margin = 0

        if side==0:
            region[0][0] =  region[0][0] + margin

      
        if side==1:
            region[3][0] =  region[3][0] -margin
       
        self.region = region
        
        height, width = frame.shape[:2]   
        black_frame = np.zeros((height, width), np.uint8)
        mask = np.full((height, width), 255, np.uint8)
        cv2.fillPoly(mask, [region], (0, 0, 0))
        eye_frame = cv2.bitwise_not(black_frame, frame.copy(), mask=mask)


        margin = 5
        self.min_x = int(np.min(region[:, 0]) - margin)
        self.max_x = int(np.max(region[:, 0]) + margin)
        self.min_y = int(np.min(region[:, 1]) - margin )
        self.max_y = int(np.max(region[:, 1]) + margin)
        
        self.frame = eye_frame[self.min_y:self.max_y, self.min_x:self.max_x]
        height, width = self.frame.shape[:2]
        n_white_pix = np.sum(self.frame == 255)
        self.area = (height*width) - n_white_pix
        
        self.origin = (self.min_x, self.min_y)
        x = math.floor(width/2)
        y = math.floor(height/2)
        self.center = (x,y)
        


        height, width = self.frame.shape[:2]
        x = math.floor(width/2)
        y = math.floor(height/2)
        self.center = (x,y)


    def _blinking_ratio(self, landmarks, points, side):
        """Calculates the ratio between the width and height of the eye frame,
        shich can be used to determine whether the eye is closed or open.
        It's the division of the width of the eye, by its height.

        Arguments:
            landmarks (dlib.full_object_detection): Facial landmarks for the face region
            points (list): Points of an eye (from the 68 Multi-PIE landmarks)

        Returns:
            The computed ratio
        """
        try:
            if side == 0:
                self.width = math.dist((landmarks[0][0], landmarks[0][1]), (landmarks[3][0],landmarks[3][1]))
                a = math.dist( (landmarks[2][0], landmarks[2][1]), (landmarks[4][0], landmarks[4][1]))
                b = math.dist( (landmarks[1][0], landmarks[1][1]), (landmarks[5][0], landmarks[5][1]))
                ratio = (2.0 * self.width) / (a + b)
                self.height = (a+b)/2
                self.inner_y = landmarks[3][1]
                self.inner_x = landmarks[3][0]
                
            else:
                self.width = math.dist( (landmarks[6][0], landmarks[6][1]), (landmarks[9][0], landmarks[9][1]))
                a = math.dist( (landmarks[7][0], landmarks[7][1]), (landmarks[11][0], landmarks[11][1]))
                b = math.dist( (landmarks[8][0], landmarks[8][1]), (landmarks[10][0], landmarks[10][1]))
                ratio = (2.0 * self.width) / (a + b)
                self.height = (a+b)/2
                self.inner_y = landmarks[6][1]
                self.inner_x = landmarks[6][0]

        except Exception:
            ratio = None

        return ratio

    def _analyze(self, original_frame, landmarks, side):
        """Isolates the eye in a new frame and initializes Pupil object.

        Arguments:
            original_frame (numpy.ndarray): Frame passed by the user
            landmarks (dlib.full_object_detection): Facial landmarks for the face region
            side: Indicates whether it's the left eye (0) or the right eye (1)
        """
        if side == 0:
            points = self.LEFT_EYE_POINTS
        elif side == 1:
            points = self.RIGHT_EYE_POINTS
        else:
            return

        self.blinking = self._blinking_ratio(landmarks, points, side)
        self._isolate(original_frame, landmarks, points, side)
        self.pupil = Pupil(self.frame, self.point, False)

