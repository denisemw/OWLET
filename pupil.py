import numpy as np
import cv2



class Pupil(object):
    """
    This class detects the iris of an eye and estimates
    the position of the pupil
    """

    def __init__(self, eye_frame, center, eyeonly):
        self.iris_frame = None
        self.x = None
        self.y = None
        self.radius = None
        self.eyeonly = eyeonly
        self.detect_iris(eye_frame.copy())
        

    @staticmethod
    def get_color(eye_frame):   
        """Detects the average color of the non-white portions of the 
        eye frame, which is used to estimate the threshold.

        Arguments:
            eye_frame (numpy.ndarray): Frame containing an eye and nothing else
        Returns:
            The mean and standard deviation of the eye frame color
        """
        indices = np.where(eye_frame != 255)
        mn, sd = cv2.meanStdDev(eye_frame[indices])
        color = mn[0][0]
        color_sd = sd[0][0]
        return (color, color_sd)
     

    def detect_iris(self, eye_frame):
        """Detects the iris and estimates the position of the pupil by
        calculating the centroid of the iris.

        Arguments:
            eye_frame (numpy.ndarray): Frame containing an eye and nothing else
        """

        try:
            eye_frame1 = cv2.GaussianBlur(eye_frame, (5, 5), 5)
            eye_frame1 = cv2.bilateralFilter(eye_frame1, 10, 15, 15)

             
            indices = np.where(eye_frame < 127)
            color, sd2 = self.get_color(eye_frame1[indices])

            # threshold can be modified for babies with very dark or light eyes
            threshold = color #* 2

            eye_frame2 = cv2.threshold(eye_frame1, threshold, 255, cv2.THRESH_BINARY)[1]
    

            contours, _ = cv2.findContours(eye_frame2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=False)
            hull = cv2.convexHull(contours[-2])
            moments = cv2.moments(hull)

            x = int(moments['m10'] / moments['m00'])
            y = int(moments['m01'] / moments['m00'])

            self.x, self.y, self.radius = x, y, 3 

        except:
              self.x = None
              self.y = None
              self.radius = None
              print("cant find pupils")
                

