#ifndef TRACKER_HPP
#define TRACKER_HPP
#include <opencv2/opencv.hpp>

using namespace cv;

void change_thresh(int, void*);

cv::Mat threshold_image(cv::Mat src,
                    int hueLow, int hueHigh,
                    int satLow, int satHigh,
                    int valLow, int valHigh);

cv::Point2f find_puff_center(cv::Mat threshed);

std::vector<cv::Point2f> find_puff_centers(cv::Mat red_threshed, cv::Mat green_threshed, cv::Mat blue_threshed);

int* get_puff_vals(cv::VideoCapture cap, int* puff_vals);

float get_abs_angle(cv::Point2f tens_center, cv::Point2f reference);

class Observer
{
  public:
    Observer( int camNum, bool GET_PUFFS );
    void updateLocationInfo();
    Point2f getCenter();
    float getAngle();
    Mat getFrame();
    void getNewPuffVals();
    void clearFrame();
    int getCodec();
    Size getFrameSize();
    bool isHome();

  private:
    VideoCapture cap;
    int red_puff_vals[6];
    int green_puff_vals[6];
    int blue_puff_vals[6];
    Point2f center;
    float abs_angle;
    Mat curFrame;
};

#endif
