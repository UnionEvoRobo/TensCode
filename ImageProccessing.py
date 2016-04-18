import cv2, numpy
from threading import Thread

__author__ = 'James Boggs & Julian Jocque'


class BoardObserver(object):
    """
    As labelled, observes the board and allows other code to get the location
    of the tensegrity. Uses OpenCV to track colored puff balls on the
    tensegrity.
    """

    def __init__(self):
        self.image_getter = WebcamImageGetter()
        self.image_analyzer = ImageAnalyzer()


# This is a webcam image getter which opens a thread to constantly update it's
# current image. This effectively fixes the problem of having to grab 5 frames
# and will dramatically increase the speed of the tensegrity tracker!
#
# Author: Julian Jocque
# Date: 7/18/14
class WebcamImageGetter:
    def __init__(self, width=1280 / 2, height=960 / 2, camera_num=2):
        self.currentFrame = None
        self.CAMERA_WIDTH = width
        self.CAMERA_HEIGHT = height
        self.CAMERA_NUM = 0

        if camera_num is None:
            maxcams = 4
            for i in range(maxcams):
                curcam = (i + self.CAMERA_NUM) % maxcams
                print "trying camera", curcam
                self.capture = cv2.VideoCapture(curcam)
                if self.capture:
                    print "using camera", curcam
                    break
            assert self.capture != None, "couldn't find camera"
        else:
            self.capture = cv2.VideoCapture(camera_num)

        # OpenCV by default gets a half resolution image so we manually set the correct resolution
        self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, self.CAMERA_WIDTH)
        self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, self.CAMERA_HEIGHT)
        Thread(target=self.update_frame, args=()).start()

    # Continually updates the frame
    def update_frame(self):
        while (True):
            ret, self.currentFrame = self.capture.read()

    def get_frame(self):
        if self.currentFrame != [] and self.currentFrame is not None:
            return numpy.copy(self.currentFrame)
        else:
            return None


class ImageAnalyzer(object):
    """
    Provides methods to take in an image as a numpy array and spit out the
    location and  heading of the tensegrity.
    """



if __name__ == "__main__":
    window = cv2.namedWindow("Webcam")
    getter = WebcamImageGetter()
    while (getter.get_frame() == None):
        # print "the frame we're getting is none"
        pass
    while (True):
        cv2.imshow("Webcam", getter.get_frame())
        cv2.waitKey(1)
