import cv2
import numpy as np
from threading import Thread

__author__ = 'James Boggs & Julian Jocque'


class BoardObserver(object):
    """
    As labelled, observes the board and allows other code to get the location
    of the tensegrity. Uses OpenCV to track colored puff balls on the
    tensegrity. Uses multi-threading to constantly be updating the location
    of the tensegrity and still respond to the rest of the code.
    """

    def __init__(self, camera_num=2):
        # Stuff to get the camera running
        self.__current_frame = None
        self.__find_camera()
        self.__frame_updater = Thread(target=self.__update_frame())
        self.__frame_updater.start()

        self.__get_puffs()  # names I never thought I'd give a method for $1000

        num_puffs = input("How many puff balls to track? ")
        for puff in range(num_puffs):
            puff_low_limit = np.array([0, 0, 0])
            puff_high_limit = np.array([255, 255, 255])

    def get_frame(self):
        if self.current_frame != [] and self.current_frame is not None:
            return np.copy(self.current_frame)
        else:
            return None

    def __find_camera(self):
        """
        Searches through cameras to find one that works. Asks the user to
        verify that the found camera is correct before using it.
        """
        max_cams = 4
        for cam in range(max_cams):
            print "Testing camera {}".format(cam)
            self.capture = cv2.VideoCapture(cam)
            if self.capture:
                cv2.imshow('Camera View', self.capture.retrieve())
                uc = raw_input("Is this the correct camera?")
                if uc.upper() == 'N':
                    cv2.destroyAllWindows()
                else:
                    print("Using camera {}".format(cam))
                    break
        assert self.capture is not None, "Couldn't find camera"

    def __get_puffs(self):
        """
        For each puff to be tracked, allow the user to specify the mask
        boundaries and see the results in real time.
        """
        num_puffs = input("How many puff balls to track? ")
        for puff in range(num_puffs):
            puff_low_limit, puff_high_limit = self.__get_puff_bounds()

    def __get_puff_bounds(self):
        """
        Open a window with the video feed and a mask applied which uses the
        input of the user through trackbars to control HSV values.
        :return: the lower and upper limits chosen by the user
        """


    def __update_frame(self):
        """
        Update the current frame instance variable by retrieving the next frame
        from the camera. Meant to run as a separate thread.
        """
        while True:
            ret, self.current_frame = self.capture.read()

    def __find_tens(self):
        pass


if __name__ == "__main__":
    window = cv2.namedWindow("Webcam")
    getter = WebcamImageGetter()
    while (getter.get_frame() == None):
        # print "the frame we're getting is none"
        pass
    while (True):
        cv2.imshow("Webcam", getter.get_frame())
        cv2.waitKey(1)
