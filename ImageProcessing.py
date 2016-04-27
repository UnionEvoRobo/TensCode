import cv2
from matplotlib import pyplot as plt
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
        self.__frame_updater = Thread(target=self.__update_frame, args=())
        self.__frame_updater.start()

        self.puffs = []
        self.__get_puffs()  # names I never thought I'd give a method for $1000

    def get_frame(self):
        """
        Get the current frame from the camera
        :return: A 3d numpy array with colors as BGR
        """
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
            try:
                self.capture = cv2.VideoCapture(cam)
            except:
                print "Camera {} is bad".format(cam)
            if self.capture:
                ret, frame = self.capture.read()
                cv2.imshow('Camera View', frame)
                k = cv2.waitKey(1) & 0xFF
                uc = raw_input("Is this the correct camera?")
                if uc.upper() == 'N':
                    cv2.destroyAllWindows()
                else:
                    print("Using camera {}".format(cam))
                    cv2.destroyAllWindows()
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
            self.puffs.append([puff_low_limit, puff_high_limit])


    def __get_puff_bounds(self):
        """
        Open a window with the video feed and a mask applied which uses the
        input of the user through trackbars to control HSV values.
        :return: the lower and upper limits chosen by the user
        """
        done_choosing = False
        # original RGB vals
        puff_low_limit = np.array([0,0,0], np.uint8)
        puff_hi_limit = np.array([255,255,255], np.uint8)
        def update_plb(x):
            puff_low_limit[0] = x

        def update_plg(x):
            puff_low_limit[1] = x

        def update_plr(x):
            puff_low_limit[2] = x

        def update_phb(x):
            puff_hi_limit[0] = x

        def update_phg(x):
            puff_hi_limit[1] = x

        def update_phr(x):
            puff_hi_limit[2] = x

        # Get first frame and mask it
        frame = self.get_frame()
        mask = cv2.inRange(frame, puff_low_limit, puff_hi_limit)
        # Show first frame
        cv2.imshow("Puff View", mask)
        # Add trackbar
        cv2.createTrackbar("Low Blue", "Puff View", 0, 255, update_plb)
        cv2.createTrackbar("Low Green", "Puff View", 0, 255, update_plg)
        cv2.createTrackbar("Low Red", "Puff View", 0, 255, update_plr)
        cv2.createTrackbar("High Blue", "Puff View", 0, 255, update_phb)
        cv2.createTrackbar("High Green", "Puff View", 0, 255, update_phg)
        cv2.createTrackbar("High Red", "Puff View", 0, 255, update_phr)

        while not done_choosing:
            frame = self.get_frame()
            mask = cv2.inRange(frame, puff_low_limit, puff_hi_limit)
            mask = cv2.bitwise_and(frame, frame, mask=mask)
            cv2.imshow("Puff View", mask)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                cv2.destroyAllWindows()
                break

        done_choosing = True if raw_input("Done (Y/N)").upper() == "Y" else False

        return puff_low_limit, puff_hi_limit


    def __update_frame(self):
        """
        Update the current frame instance variable by retrieving the next frame
        from the camera. Meant to run as a separate thread.
        """
        while True:
            ret, self.current_frame = self.capture.read()

    def __find_tens(self):
        pass

    def __shutdown(self):
        cv2.destroyAllWindows()
        self.capture.release()

# Helpful method to show a given mask from the camera.
def show_mask():
    low_h = input("Low hue")
    low_s = input("Low sat")
    low_v = input("Low val")
    high_h = input("High hue")
    high_s = input("High sat")
    high_v = input("High val")
    low = np.array([low_h, low_s, low_v])
    high = np.array([high_h, high_s, high_v])
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        frame = cv2.medianBlur(frame,5)
        mask = cv2.inRange(frame, low, high)
        cv2.imshow("Cam View", frame)
        cv2.imshow("Mask View", mask)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            cv2.destroyAllWindows()
            cap.release()
            break
    return low, high

# A helpful method to find the color of a pixel from the feed from the camera
def get_color_at():
    def print_loc(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONUP:
            bgr = [int(i) for i in frame[y , x]]
            print "X:{} Y:{} | {}".format(x, y, bgr)
            prev_img[:] = np.array(bgr, np.uint8)
            print prev_img
    cap = cv2.VideoCapture(0)
    prev_img = np.zeros((300,512,3),np.uint8)
    cv2.namedWindow("Preview")
    cv2.namedWindow("Cam View")
    while True:
        ret, frame = cap.read()
        cv2.imshow("Cam View", frame)
        cv2.imshow("Preview", prev_img)
        cv2.setMouseCallback("Cam View", print_loc)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            cv2.destroyAllWindows()
            cap.release()
            break

if __name__ == "__main__":
    window = cv2.namedWindow("Webcam")
    getter = WebcamImageGetter()
    while (getter.get_frame() == None):
        # print "the frame we're getting is none"
        pass
    while (True):
        cv2.imshow("Webcam", getter.get_frame())
        cv2.waitKey(1)
