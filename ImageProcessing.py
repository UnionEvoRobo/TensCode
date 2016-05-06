from math import asin
import cv2
import time
import math
from matplotlib import pyplot as plt  # This is necessary!
from Point import Point
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

    def __init__(self):
        # Stuff to get the camera running
        self.__current_frame = None
        self.__find_camera()
        self.__frame_updater = Thread(target=self.__update_frame, args=())
        self.__frame_display = Thread
        self.__frame_updater.start()

        self.puffs = []
        self.__get_puffs()  # names I never thought I'd give a method for $1000

    def get_frame(self):
        """
        Get the current frame from the camera
        :return: A 3d numpy array with colors as BGR
        """
        if self.__current_frame != [] and self.__current_frame is not None:
            return np.copy(self.__current_frame)
        else:
            return None

    def display_frame(self):
        while True:
            frame = self.get_frame()
            try:
                puff_centers = self.__get_puff_centers(frame)
            except ZeroDivisionError as e:
                print e
                continue
            except IndexError as e:
                print e
                continue
            for center in puff_centers:
                up_left = (center.x - 5, center.y - 5)
                bot_right = (center.x + 5, center.y + 5)
                cv2.rectangle(frame, up_left, bot_right, [0,0,0], 2)
            tens_center = self.__get_tens_center(puff_centers)
            up_left = (tens_center.x - 5, tens_center.y - 5)
            bot_right = (tens_center.x + 5, tens_center.y + 5)
            cv2.rectangle(frame, up_left, bot_right, [126,255,255], 2)
            angle = self.__get_tens_angle(tens_center, puff_centers[0])
            frame = cv2.line(frame,
                             (tens_center.x, tens_center.y),
                             (puff_centers[0].x, puff_centers[0].y),
                             (0, 255, 255),
                             5)
            print(angle)
            cv2.imshow("Tracker View", frame)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                cv2.destroyAllWindows()
                break

    def __get_tens_angle(self, tc, pc):
        """
        Draw a line from the center of the tensegrity to the top of the frame.
        Draw another line from the center of the tensegrity to the first puff
        ball (i.e. self.puffs[0]). Calculate the angle between these two lines
        and return it as an int. Use basic trig by finding the sin^-1 of the
        ratio between the hypotenuse and opposite side of the triangle formed
        :return: Int value of the tensegrity's heading
        """
        # Point above the center of the tensegrity on the top of the screen
        ref_point = Point(tc.x, 0, 0)

        bearing_slope = (tc.y-pc.y)/()
        # Point where the line from center to puff hits the top of screen
        bearing_point = Point(pc.y - bearing_slope*pc.x, 0, 0)

        opp_length = ref_point.x - bearing_point.x
        hypo_length = int(math.sqrt((tc.x - bearing_point.x)**2 + (tc.y - bearing_point.y)**2))

        angle = asin(opp_length/float(hypo_length))*(180.0/math.pi)
        return angle

    def __get_tens_center(self, puff_centers):
        x_vals = [center.x for center in puff_centers]
        y_vals = [center.y for center in puff_centers]
        max_x = max(x_vals)
        min_x = min(x_vals)
        max_y = max(y_vals)
        min_y = min(y_vals)
        x_dist = max_x - min_x
        y_dist = max_y - min_y
        cx = int(min_x + x_dist/2)
        cy = int(min_y + y_dist/2)
        return Point(cx, cy, 0)

    def __get_puff_centers(self, frame):
        """
        Find the centers of the puffs by using algorithms
        :return: a list of (x,y) tuples for each puff
        """

        frame = cv2.medianBlur(frame, 15)
        puff_centers = []
        for puff in self.puffs:
            puff_low = puff[0]  # lower bound on color
            puff_high = puff[1]  # upper bound on color

            # mask frame
            mask = cv2.inRange(frame, puff_low, puff_high)

            # get the contours
            img, conts, hier = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # get the moments and find the center
            mmnts = cv2.moments(conts[0])
            cx = int(mmnts['m10']/mmnts['m00'])
            cy = int(mmnts['m01']/mmnts['m00'])

            puff_centers.append(Point(cx, cy, 0))

        return puff_centers

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
        cv2.createTrackbar("High Blue", "Puff View", 255, 255, update_phb)
        cv2.createTrackbar("High Green", "Puff View", 255, 255, update_phg)
        cv2.createTrackbar("High Red", "Puff View", 255, 255, update_phr)

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

        print(puff_low_limit, puff_hi_limit)
        return puff_low_limit, puff_hi_limit

    def __update_frame(self):
        """
        Update the current frame instance variable by retrieving the next frame
        from the camera. Meant to run as a separate thread.
        """
        while True:
            ret, self.__current_frame = self.capture.read()

    def __find_tens(self):
        pass

    def __shutdown(self):
        cv2.destroyAllWindows()
        self.capture.release()

    @property
    def tens_location(self):
        loc = Point(0, 0, 0)
        puff_locs = self.__get_puff_centers()


# Helpful method to show a given mask from the camera.
def show_contours():
    cap = cv2.VideoCapture(0)
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
    __, frame = cap.read()
    frame = cv2.medianBlur(frame, 5)
    mask = cv2.inRange(frame, puff_low_limit, puff_hi_limit)
    # Show first frame
    cv2.imshow("Puff View", mask)
    # Add trackbar
    cv2.createTrackbar("Low Blue", "Puff View", 0, 255, update_plb)
    cv2.createTrackbar("Low Green", "Puff View", 0, 255, update_plg)
    cv2.createTrackbar("Low Red", "Puff View", 0, 255, update_plr)
    cv2.createTrackbar("High Blue", "Puff View", 255, 255, update_phb)
    cv2.createTrackbar("High Green", "Puff View", 255, 255, update_phg)
    cv2.createTrackbar("High Red", "Puff View", 255, 255, update_phr)

    while not done_choosing:
        __, frame = cap.read()
        frame = cv2.medianBlur(frame, 5)
        mask = cv2.inRange(frame, puff_low_limit, puff_hi_limit)
        mask = cv2.bitwise_and(frame, frame, mask=mask)
        cv2.imshow("Puff View", mask)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            cv2.destroyAllWindows()
            break
    done_choosing = True if raw_input("Done (Y/N)").upper() == "Y" else False
    print(puff_low_limit, puff_hi_limit)
    while True:
        ret, frame = cap.read()
        frame = cv2.medianBlur(frame,15)
        mask = cv2.inRange(frame, puff_low_limit, puff_hi_limit)
        cont_mask = mask.copy()
        ret,thresh = cv2.threshold(cont_mask,127,255,cv2.THRESH_BINARY)
        img, conts, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        img = cv2.drawContours(img, conts, -1, (255,255,255), 3)
        mmnts = cv2.moments(conts[0])
        cx = int(mmnts['m10']/mmnts['m00'])
        cy = int(mmnts['m01']/mmnts['m00'])
        print cx, cy
        cv2.imshow("Cam View", frame)
        cv2.imshow("Mask View", mask)
        cv2.imshow("Contour View", img)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            cv2.destroyAllWindows()
            cap.release()
            break

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

    def matts_test_function(self, g_bounds, o_bounds, p_bounds, run_time):
        '''Continuously records the webcam image as well as the tracking boxes
	Coppied mostly from getTensCenter and /Resonance nodes/Frequency Response/track.py
        '''

        # Record a video since cv2.imshow() doesn't seem to work
        fourcc = cv2.cv.CV_FOURCC(*'XVID')
        out = cv2.VideoWriter('tracking_test_video.avi',fourcc, 30.0, (640,480))
        init_time = time.time()


        # a while(true) loop is ok here because even with a keyboard interupt the video file will safe succesfully
        while (time.time()-init_time < run_time):
            frame = self.getGoodFrame()
            imgHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            centers = {}
            if (True):
                centers["green"] = self.getColorCenter(imgHSV, g_bounds[0], g_bounds[1], "greenDetected")
                centers["orange"] = self.getColorCenter(imgHSV, o_bounds[0], o_bounds[1], "orangeDetected")
                centers["pink"] = self.getColorCenter(imgHSV, p_bounds[0], p_bounds[1], "pinkDetected")
            else:
                centers["green"] = self.alternateGetColorCenter(frame, g_bounds[0], g_bounds[1])
                centers["orange"] = self.alternateGetColorCenter(frame, o_bounds[0], o_bounds[1])
                centers["pink"] = self.alternateGetColorCenter(frame, p_bounds[0], p_bounds[1])

            print "centers = "+str(centers)
            colors = ["green","orange","pink"]
            colorValues = {}
            colorValues["green"] = (27+10,255,255)
            colorValues["orange"] = (11+10,255,255)
            colorValues["pink"] = (3+10,255,255)
            for color in colors:
                if centers[color] != (None,None):
                    # 5 is an arbitrary number of pixels. Makes a nice small box on the image over the pom pom
                    upperLeft = (centers[color][0]-5,centers[color][1]-5)
                    lowerRight = (centers[color][0]+5,centers[color][1]+5)
                    cv2.rectangle(imgHSV, upperLeft, lowerRight, colorValues[color], 2)

            imgBGR = cv2.cvtColor(imgHSV, cv2.COLOR_HSV2BGR)
            out.write(imgBGR)
            #print "imgBGR = "+str(imgBGR)
            #cv2.imwrite("trackingtestimage.png",imgBGR)
            #cv2.imshow("TrackingTest", imgBGR)

            #raw_input()

        out.release()


if __name__ == '__main__':
    from matplotlib import pyplot as plt
    observer = BoardObserver()
    observer.display_frame()
    #show_contours()

"""
(array([  0, 177,   0], dtype=uint8), array([255, 255, 231], dtype=uint8))
Done (Y/N)Y
(array([ 27,   0, 255], dtype=uint8), array([152, 105, 255], dtype=uint8))
Done (Y/N)y
(array([  0,  79, 250], dtype=uint8), array([ 11, 129, 255], dtype=uint8))
"""